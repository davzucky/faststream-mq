from dataclasses import dataclass

from faststream_mq.schemas import MQQueue


@dataclass(kw_only=True)
class MQConfig:
    queue: MQQueue
