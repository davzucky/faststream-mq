# Troubleshooting

## Known problem: `ibmmq` OpenTelemetry crash with message handles

`ibmmq` 2.0.5 has a known OpenTelemetry bug where `Queue.get()` can crash when IBM MQ OpenTelemetry support is enabled and the get options use a message handle, for example with `MQGMO_PROPERTIES_IN_HANDLE`.

The failure looks like this:

```text
UnboundLocalError: cannot access local variable 'hc' where it is not associated with a value
```

This is tracked upstream in [`ibm-messaging/mq-mqi-python#20`](https://github.com/ibm-messaging/mq-mqi-python/issues/20){.external-link target="_blank"}.

`faststream-mq` reads IBM MQ message properties through `gmo.MsgHandle`, so this can affect consumers when `ibmmq`'s MQ-specific OpenTelemetry integration is active.

### Workaround

Disable `ibmmq`'s built-in OpenTelemetry hooks before running the application:

```bash
export MQIPY_NOOTEL=true
```

This disables `ibmmq`'s MQI-level OpenTelemetry propagation path. You can still use FastStream-level instrumentation through the `faststream-mq[otel]` extra.

### Notes

- This is an upstream `ibmmq` issue, not a broker configuration problem.
- If you see the error only after installing OpenTelemetry packages, set `MQIPY_NOOTEL=true` first to confirm the diagnosis.
- Remove the workaround once the upstream issue is fixed in the `ibmmq` version you use.
