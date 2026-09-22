import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from faststream.specification import AsyncAPI

from faststream_mq.broker.router import MQRouter as MQBrokerRouter
from faststream_mq.fastapi import MQRouter
from faststream_mq.testing import TestMQBroker


@pytest.mark.mq()
@pytest.mark.asyncio()
@pytest.mark.parametrize("schema_version", ["2.6.0", "3.0.0"])
@pytest.mark.parametrize("endpoint_kind", ["subscriber", "publisher"])
async def test_schema_endpoint_queue_address(schema_version, endpoint_kind):
    router = MQRouter(
        specification=AsyncAPI(schema_version=schema_version),
        schema_url="/magpie/asyncapi",
    )
    mq_router = MQBrokerRouter(prefix="DEV.")

    if endpoint_kind == "subscriber":

        @mq_router.subscriber("QUEUE", title="display_name")
        async def handle(message: str) -> None: ...

    else:
        mq_router.publisher("QUEUE", title="display_name", schema=str)

    router.broker.include_router(mq_router, prefix="APP.")
    app = FastAPI()
    app.include_router(router)

    async with TestMQBroker(router.broker):
        with TestClient(app) as client:
            response = client.get("/magpie/asyncapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["asyncapi"] == schema_version
    assert "display_name" in schema["channels"]
    if schema_version == "3.0.0":
        assert schema["channels"]["display_name"]["address"] == "APP.DEV.QUEUE"
