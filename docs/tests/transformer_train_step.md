# Transformer Train Step

`transformer_train_step` applies controlled forward, backward, gradient, and
optimizer-style arithmetic pressure.

```bash
pantheon --test transformer_train_step --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Compute | Forward, gradient, and update-style arithmetic. |
| Memory | Synthetic activation and state working-set reads. |
| Telemetry | SM/cache/DRAM activity, power, clocks, and thermals. |
| Result | Synthetic training steps per second. |

It is not a convergence or time-to-train benchmark. Validate training quality,
collectives, optimizer selection, and framework behavior separately.
