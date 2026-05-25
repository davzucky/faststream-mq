import os

from faststream.security import SASLPlaintext

from faststream_mq import MQBroker

security = SASLPlaintext(username="app", password="password", use_ssl=False)

broker = MQBroker(
    queue_manager="QM1",
    conn_name=os.getenv("FASTSTREAM_MQ_CONN_NAME", "localhost(1414)"),
    security=security,
)
