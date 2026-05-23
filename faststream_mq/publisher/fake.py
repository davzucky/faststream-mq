from typing import TYPE_CHECKING, Union

from faststream._internal.endpoint.publisher.fake import FakePublisher

from faststream_mq.response import MQPublishCommand

if TYPE_CHECKING:
    from faststream._internal.producer import ProducerProto
    from faststream.response.response import PublishCommand


class MQFakePublisher(FakePublisher):
    def __init__(
        self,
        producer: "ProducerProto[MQPublishCommand]",
        queue: str,
        *,
        reply_to_qmgr: str = "",
        native_correlation_id: bytes | None = None,
    ) -> None:
        super().__init__(producer=producer)
        self.queue = queue
        self.reply_to_qmgr = reply_to_qmgr
        self.native_correlation_id = native_correlation_id

    def patch_command(
        self,
        cmd: Union["PublishCommand", MQPublishCommand],
    ) -> MQPublishCommand:
        real_cmd = MQPublishCommand.from_cmd(super().patch_command(cmd))
        real_cmd.destination = self.queue
        real_cmd.reply_to_qmgr = self.reply_to_qmgr
        real_cmd.native_correlation_id = self.native_correlation_id
        real_cmd.syncpoint = True
        return real_cmd
