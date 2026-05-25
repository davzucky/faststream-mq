from __future__ import annotations

import asyncio
from typing import Any

import pytest
from faststream.response.publish_type import PublishType
from faststream.security import BaseSecurity

from faststream_mq.helpers.client import AsyncMQConnection, MQConnectionConfig
from faststream_mq.message import MQRawMessage
from faststream_mq.response import MQPublishCommand
from faststream_mq.security import parse_security

from .basic import MQMemoryTestcaseConfig


class FakeMQMIError(Exception):
    def __init__(self, comp: int, reason: int) -> None:
        self.comp = comp
        self.reason = reason


class ReconnectableFakeMQ:
    MQMIError = FakeMQMIError

    class CMQC:
        MQRC_CONNECTION_BROKEN = 2009
        MQRC_HCONN_ERROR = 2018
        MQRC_Q_MGR_NOT_AVAILABLE = 2059
        MQRC_HOST_NOT_AVAILABLE = 2538
        MQRC_RECONNECTING = 2548
        MQRC_RECONNECTED = 2549
        MQRC_RECONNECT_FAILED = 2540
        MQRC_CALL_INTERRUPTED = 2530
        MQRC_RECONNECT_Q_MGR_REQD = 2556
        MQRC_RECONNECT_TIMED_OUT = 2557


class FailingSettlementConnection:
    async def commit(self) -> None:
        raise RuntimeError("commit failed")

    async def backout(self) -> None:
        raise RuntimeError("backout failed")


@pytest.mark.mq()
def test_commit_recovers_connection_and_reopens_consumer(monkeypatch) -> None:
    attempts = 0
    recoveries: list[bool] = []

    class FakeQMgr:
        def commit(self) -> None:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise FakeMQMIError(2, ReconnectableFakeMQ.CMQC.MQRC_CONNECTION_BROKEN)

    monkeypatch.setattr(
        "faststream_mq.helpers.client._load_ibmmq", lambda: ReconnectableFakeMQ
    )

    connection = AsyncMQConnection(
        connection_config=MQConnectionConfig(queue_manager="QM1"),
    )
    connection._qmgr = FakeQMgr()
    connection._consumer_queue_name = "DEV.QUEUE.1"
    connection._consumer_queue = object()

    def recover(*, reopen_consumer: bool) -> None:
        recoveries.append(reopen_consumer)
        connection._qmgr = FakeQMgr()

    monkeypatch.setattr(connection, "_recover_connection_sync", recover)

    connection._commit_sync()

    assert attempts == 2
    assert recoveries == [True]


@pytest.mark.mq()
def test_backout_recovers_connection_and_reopens_consumer(monkeypatch) -> None:
    attempts = 0
    recoveries: list[bool] = []

    class FakeQMgr:
        def backout(self) -> None:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise FakeMQMIError(2, ReconnectableFakeMQ.CMQC.MQRC_CONNECTION_BROKEN)

    monkeypatch.setattr(
        "faststream_mq.helpers.client._load_ibmmq", lambda: ReconnectableFakeMQ
    )

    connection = AsyncMQConnection(
        connection_config=MQConnectionConfig(queue_manager="QM1"),
    )
    connection._qmgr = FakeQMgr()
    connection._consumer_queue_name = "DEV.QUEUE.1"
    connection._consumer_queue = object()

    def recover(*, reopen_consumer: bool) -> None:
        recoveries.append(reopen_consumer)
        connection._qmgr = FakeQMgr()

    monkeypatch.setattr(connection, "_recover_connection_sync", recover)

    connection._backout_sync()

    assert attempts == 2
    assert recoveries == [True]


@pytest.mark.mq()
def test_reply_publish_recovers_and_preserves_reply_to_qmgr(monkeypatch) -> None:
    published: list[dict[str, Any]] = []
    recoveries: list[bool] = []

    class FakeProperties:
        def set(self, name, value) -> None:
            return None

    class FakeMessageHandle:
        def __init__(self, qmgr) -> None:
            self.msg_handle = 1
            self.properties = FakeProperties()

        def dlt(self) -> None:
            return None

    class FakeMD:
        def __init__(self, Version=None) -> None:
            self.ReplyToQ = ""
            self.ReplyToQMgr = ""
            self.Priority = None
            self.Persistence = None
            self.Expiry = None
            self.CorrelId = None
            self.MsgId = b""

    class FakePMO:
        def __init__(self, Version=None) -> None:
            self.Options = 0
            self.OriginalMsgHandle = None

    class FakeQueue:
        def __init__(self, qmgr, target, open_opts) -> None:
            self.target = target

        def put(self, body, md, pmo) -> None:
            published.append(
                {
                    "body": body,
                    "destination": self.target,
                    "reply_to_qmgr": md.ReplyToQMgr,
                    "correl_id": md.CorrelId,
                    "syncpoint": pmo.Options & FakeMQ.CMQC.MQPMO_SYNCPOINT,
                }
            )
            if len(published) == 1:
                raise FakeMQMIError(2, FakeMQ.CMQC.MQRC_CONNECTION_BROKEN)

        def close(self) -> None:
            return None

    class FakeMQ(ReconnectableFakeMQ):
        Queue = FakeQueue
        MessageHandle = FakeMessageHandle
        MD = FakeMD
        PMO = FakePMO

        class CMQC(ReconnectableFakeMQ.CMQC):
            MQMD_CURRENT_VERSION = 1
            MQPMO_VERSION_3 = 3
            MQPMO_SYNCPOINT = 2
            MQOO_OUTPUT = 2
            MQPER_PERSISTENT = 1
            MQPER_NOT_PERSISTENT = 0

    monkeypatch.setattr("faststream_mq.helpers.client._load_ibmmq", lambda: FakeMQ)

    connection = AsyncMQConnection(
        connection_config=MQConnectionConfig(queue_manager="QM1"),
    )
    connection._qmgr = object()
    connection._consumer_queue_name = "DEV.REQUESTS"
    connection._consumer_queue = object()

    def recover(*, reopen_consumer: bool) -> None:
        recoveries.append(reopen_consumer)
        connection._qmgr = object()

    monkeypatch.setattr(connection, "_recover_connection_sync", recover)

    cmd = MQPublishCommand(
        "reply",
        destination="DEV.REPLY",
        _publish_type=PublishType.REPLY,
        reply_to_qmgr="REMOTE.QM",
        native_correlation_id=b"request-message-id",
        syncpoint=True,
    )

    connection._publish_sync(cmd, serializer=None)

    assert recoveries == [True]
    assert published == [
        {
            "body": b"reply",
            "destination": "DEV.REPLY",
            "reply_to_qmgr": "REMOTE.QM",
            "correl_id": b"request-message-id",
            "syncpoint": FakeMQ.CMQC.MQPMO_SYNCPOINT,
        },
        {
            "body": b"reply",
            "destination": "DEV.REPLY",
            "reply_to_qmgr": "REMOTE.QM",
            "correl_id": b"request-message-id",
            "syncpoint": FakeMQ.CMQC.MQPMO_SYNCPOINT,
        },
    ]


@pytest.mark.mq()
@pytest.mark.asyncio()
class TestRuntimeRegressionTransactions(MQMemoryTestcaseConfig):
    async def test_failed_manual_settlement_releases_consume_loop(
        self, queue: str
    ) -> None:
        broker = self.get_broker()

        async def broken_parser(msg, original):
            raise ValueError("boom")

        subscriber = broker.subscriber(queue, parser=broken_parser)

        @subscriber
        async def handler(msg) -> None: ...

        raw_message = MQRawMessage(
            body=b"hello",
            queue=queue,
            connection=FailingSettlementConnection(),
        )

        async with self.patch_broker(broker) as br:
            await br.start()
            await asyncio.wait_for(
                subscriber.consume(raw_message), timeout=self.timeout
            )

        assert raw_message.settled is None
        assert raw_message.settled_event.is_set()


@pytest.mark.mq()
def test_unsupported_security_object_is_rejected() -> None:
    with pytest.raises(NotImplementedError, match="MQBroker does not support"):
        parse_security(BaseSecurity())
