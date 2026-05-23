from faststream.security import SASLPlaintext

from faststream_mq import MQBroker

security = SASLPlaintext(username="app", password="password", use_ssl=False)

broker = MQBroker(
    queue_manager="QM1",
    conn_name="ibmmq(1414)",
    security=security,
)
