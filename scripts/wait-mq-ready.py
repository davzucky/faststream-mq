from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MQEndpoint:
    name: str
    queue_manager: str
    channel: str
    conn_name: str
    username: str
    password: str


def _load_ibmmq() -> Any:
    import ibmmq as mq

    return mq


def _probe(endpoint: MQEndpoint) -> None:
    mq = _load_ibmmq()
    qmgr = mq.QueueManager(None)

    try:
        qmgr.connect_tcp_client(
            endpoint.queue_manager,
            mq.CD(),
            endpoint.channel,
            endpoint.conn_name,
            endpoint.username,
            endpoint.password,
        )
        qmgr.get_name()
    finally:
        if getattr(qmgr, "is_connected", False):
            qmgr.disconnect()


def _wait_for_endpoint(
    endpoint: MQEndpoint, *, timeout: float, interval: float
) -> None:
    deadline = time.monotonic() + timeout
    last_error: BaseException | None = None

    while time.monotonic() < deadline:
        try:
            _probe(endpoint)
            print(f"IBM MQ endpoint {endpoint.name} is ready at {endpoint.conn_name}.")
            return
        except BaseException as exc:
            last_error = exc
            print(
                f"IBM MQ endpoint {endpoint.name} is not ready yet at "
                f"{endpoint.conn_name}: {exc!r}",
                flush=True,
            )
            time.sleep(interval)

    msg = f"Timed out waiting for IBM MQ endpoint {endpoint.name} at {endpoint.conn_name}."
    if last_error is not None:
        raise TimeoutError(msg) from last_error
    raise TimeoutError(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for IBM MQ client connectivity.")
    parser.add_argument("--queue-manager", default="QM1")
    parser.add_argument("--channel", default="DEV.ADMIN.SVRCONN")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="password")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument(
        "conn_names",
        nargs="+",
        help="Connection names to probe, for example '127.0.0.1(1414)'.",
    )
    args = parser.parse_args()

    for index, conn_name in enumerate(args.conn_names, start=1):
        _wait_for_endpoint(
            MQEndpoint(
                name=f"mq-{index}",
                queue_manager=args.queue_manager,
                channel=args.channel,
                conn_name=conn_name,
                username=args.username,
                password=args.password,
            ),
            timeout=args.timeout,
            interval=args.interval,
        )


if __name__ == "__main__":
    main()
