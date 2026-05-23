import pytest

from faststream_mq import MQBroker
from faststream_mq.broker.router import MQPublisher, MQRoute, MQRouter
from tests.asyncapi.base.v3_0_0.router import RouterTestcase


@pytest.mark.mq()
class TestRouter(RouterTestcase):
    broker_class = MQBroker
    router_class = MQRouter
    publisher_class = MQPublisher
    route_class = MQRoute
