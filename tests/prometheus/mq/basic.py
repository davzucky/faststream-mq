from typing import Any

from faststream.prometheus import MetricsSettingsProvider

from faststream_mq.prometheus import MQPrometheusMiddleware
from faststream_mq.prometheus.provider import MQMetricsSettingsProvider
from tests.brokers.mq.basic import MQTestcaseConfig
from tests.brokers.mq.utils import ManagedMQBroker, MQAdminConfig


class MQPrometheusSettings(MQTestcaseConfig):
    messaging_system = "ibm_mq"

    def get_broker(self, apply_types: bool = False, **kwargs: Any) -> ManagedMQBroker:
        broker = super().get_broker(apply_types=apply_types, **kwargs)
        return ManagedMQBroker(broker, admin_config=MQAdminConfig())

    def get_middleware(self, **kwargs: Any) -> MQPrometheusMiddleware:
        return MQPrometheusMiddleware(**kwargs)

    def get_settings_provider(self) -> MetricsSettingsProvider[Any]:
        return MQMetricsSettingsProvider()
