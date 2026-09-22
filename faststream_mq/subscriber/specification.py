from faststream._internal.endpoint.subscriber import SubscriberSpecification
from faststream.specification.asyncapi.utils import resolve_payloads
from faststream.specification.schema import Message, Operation, SubscriberSpec

from faststream_mq.configs import MQBrokerConfig

from .config import MQSubscriberSpecificationConfig


class MQSubscriberSpecification(
    SubscriberSpecification[MQBrokerConfig, MQSubscriberSpecificationConfig],
):
    @property
    def channel_labels(self) -> list[str]:
        return [f"{self._outer_config.prefix}{self.config.queue.name}"]

    def get_schema(self) -> dict[str, SubscriberSpec]:
        channel_name = self.name
        return {
            channel_name: SubscriberSpec(
                address=self.channel_labels[0],
                description=self.description,
                operation=Operation(
                    bindings=None,
                    message=Message(
                        title=f"{channel_name}:Message",
                        payload=resolve_payloads(self.get_payloads()),
                    ),
                ),
                bindings=None,
            ),
        }
