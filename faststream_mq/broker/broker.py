import logging
import time
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any, Optional, cast

import anyio
from fast_depends import Provider, dependency_provider
from faststream._internal.broker import BrokerUsecase
from faststream._internal.constants import EMPTY
from faststream._internal.context.repository import ContextRepo
from faststream._internal.di import FastDependsConfig
from faststream.response.publish_type import PublishType
from faststream.specification.schema import BrokerSpec
from typing_extensions import override

from faststream_mq.configs import MQBrokerConfig
from faststream_mq.helpers import MQConnectionConfig
from faststream_mq.helpers.client import is_retryable_mq_exception
from faststream_mq.publisher.producer import AsyncMQFastProducerImpl
from faststream_mq.response import MQPublishCommand
from faststream_mq.schemas import MQQueue
from faststream_mq.security import parse_security
from faststream_mq.tls import MQTLSConfig, validate_tls_configuration

from .logging import make_mq_logger_state
from .registrator import MQRegistrator

if TYPE_CHECKING:
    from types import TracebackType

    from fast_depends.dependencies import Dependant
    from fast_depends.library.serializer import SerializerProto
    from faststream._internal.basic_types import LoggerProto, SendableMessage
    from faststream._internal.types import BrokerMiddleware, CustomCallable
    from faststream.security import BaseSecurity
    from faststream.specification.schema.extra import Tag, TagDict

    from faststream_mq.helpers.client import AsyncMQConnection
    from faststream_mq.message import MQMessage, MQRawMessage  # noqa: F401


class MQBroker(
    MQRegistrator, BrokerUsecase["MQRawMessage", "AsyncMQConnection", MQBrokerConfig]
):
    def __init__(
        self,
        queue_manager: str = "QM1",
        *,
        channel: str | None = None,
        conn_name: str | None = None,
        host: str | None = None,
        port: int | None = None,
        ccdt_url: str | None = None,
        reconnect: str = "disabled",
        username: str | None = None,
        password: str | None = None,
        tls: MQTLSConfig | None = None,
        reply_model_queue: str = "DEV.APP.MODEL.QUEUE",
        wait_interval: float = 1.0,
        graceful_timeout: float | None = None,
        decoder: Optional["CustomCallable"] = None,
        parser: Optional["CustomCallable"] = None,
        dependencies: Iterable["Dependant"] = (),
        middlewares: Sequence["BrokerMiddleware[Any, Any]"] = (),
        routers: Iterable[MQRegistrator] = (),
        security: Optional["BaseSecurity"] = None,
        specification_url: str | None = None,
        protocol: str | None = None,
        protocol_version: str | None = "mqi",
        description: str | None = None,
        tags: Iterable["Tag | TagDict"] = (),
        logger: Optional["LoggerProto"] = EMPTY,
        log_level: int = logging.INFO,
        apply_types: bool = True,
        serializer: Optional["SerializerProto"] = EMPTY,
        provider: Optional["Provider"] = None,
        context: Optional["ContextRepo"] = None,
    ) -> None:
        security_args = parse_security(security)
        validate_tls_configuration(
            tls=tls,
            use_ssl=bool(security_args.get("use_ssl", False)),
            ssl_context=security_args.get("ssl_context"),
        )

        if ccdt_url is None:
            channel = channel or "DEV.APP.SVRCONN"
            if conn_name is None:
                host = host or "127.0.0.1"
                port = port or 1414
                conn_name = f"{host}({port})"

        else:
            if any(v is not None for v in (conn_name, host, port)):
                msg = (
                    "`ccdt_url` cannot be combined with `conn_name`, `host`, or `port`."
                )
                raise ValueError(msg)

            conn_name = None

        username = security_args.get("username") or username
        password = security_args.get("password") or password

        specification_target = conn_name or ccdt_url or "ccdt"
        specification_url = (
            specification_url or f"mq://{queue_manager}@{specification_target}"
        )
        protocol = protocol or "ibmmq"

        super().__init__(
            routers=routers,  # ty: ignore[invalid-argument-type]
            config=MQBrokerConfig(
                connection_config=MQConnectionConfig(
                    queue_manager=queue_manager,
                    channel=channel,
                    conn_name=conn_name,
                    ccdt_url=ccdt_url,
                    reconnect_mode=reconnect,
                    username=username,
                    password=password,
                    tls=tls,
                    reply_model_queue=reply_model_queue,
                    wait_interval=wait_interval,
                ),
                producer=AsyncMQFastProducerImpl(
                    parser=parser,
                    decoder=decoder,
                ),
                broker_middlewares=middlewares,
                broker_parser=parser,
                broker_decoder=decoder,
                logger=make_mq_logger_state(
                    logger=logger,
                    log_level=log_level,
                ),
                fd_config=FastDependsConfig(
                    use_fastdepends=apply_types,
                    serializer=serializer,
                    provider=provider or dependency_provider,
                    context=context or ContextRepo(),
                ),
                broker_dependencies=dependencies,
                graceful_timeout=graceful_timeout,
                extra_context={
                    "broker": self,
                },
            ),
            specification=BrokerSpec(  # ty: ignore[unknown-argument]
                description=description,
                url=[specification_url],
                protocol=protocol,
                protocol_version=protocol_version,
                security=security,
                tags=tags,
            ),
        )

    @property
    def _mq_config(self) -> MQBrokerConfig:
        return cast(MQBrokerConfig, self.config)

    @override
    async def _connect(self) -> "AsyncMQConnection":
        timeout = self._mq_config.connection_config.startup_retry_timeout
        interval = self._mq_config.connection_config.startup_retry_interval
        deadline = time.monotonic() + timeout

        while True:
            try:
                await self._mq_config.connect()
                break
            except Exception as exc:
                if not is_retryable_mq_exception(exc):
                    raise
                if timeout <= 0 or time.monotonic() >= deadline:
                    raise
                await anyio.sleep(interval)

        assert self._mq_config.producer.connection is not None
        return self._mq_config.producer.connection

    async def stop(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: Optional["TracebackType"] = None,
    ) -> None:
        await super().stop(exc_type, exc_val, exc_tb)
        await self._mq_config.disconnect()
        self._connection = None

    async def start(self) -> None:
        await self.connect()
        await super().start()

    @override
    async def ping(self, timeout: float | None = None) -> bool:
        return await self._mq_config.producer.ping(timeout or 5.0)

    @override
    async def publish(
        self,
        message: "SendableMessage" = None,
        queue: MQQueue | str = "",
        *,
        headers: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        reply_to: str = "",
        reply_to_qmgr: str = "",
        priority: int | None = None,
        persistence: bool | None = None,
        expiry: int | None = None,
        message_type: str | None = None,
        message_id: str | None = None,
    ) -> None:
        cmd = MQPublishCommand(
            message,
            destination=MQQueue.validate(queue)
            .add_prefix(self._mq_config.prefix)
            .routing(),
            headers=headers,
            correlation_id=correlation_id,
            reply_to=reply_to,
            reply_to_qmgr=reply_to_qmgr,
            priority=priority,
            persistence=persistence,
            expiry=expiry,
            message_type=message_type,
            message_id=message_id,
            _publish_type=PublishType.PUBLISH,
        )
        await super()._basic_publish(cmd, producer=self._producer)

    @override
    async def request(  # ty: ignore[invalid-method-override]
        self,
        message: "SendableMessage" = None,
        queue: MQQueue | str = "",
        *,
        headers: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        priority: int | None = None,
        persistence: bool | None = None,
        expiry: int | None = None,
        message_type: str | None = None,
        message_id: str | None = None,
        timeout: float = 5.0,
    ) -> "MQMessage":
        cmd = MQPublishCommand(
            message,
            destination=MQQueue.validate(queue)
            .add_prefix(self._mq_config.prefix)
            .routing(),
            headers=headers,
            correlation_id=correlation_id,
            priority=priority,
            persistence=persistence,
            expiry=expiry,
            message_type=message_type,
            message_id=message_id,
            timeout=timeout,
            _publish_type=PublishType.PUBLISH,
        )
        return await super()._basic_request(cmd, producer=self._producer)
