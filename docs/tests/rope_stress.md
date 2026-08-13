# RoPE Stress

`rope_stress` exercises paired rotary-position-style arithmetic used around
transformer attention inputs.

```bash
pantheon --test rope_stress --duration 60 --gpu 0 --mem 25 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Compute | Paired rotation-style floating-point math. |
| Memory | Repeated reads through synthetic token state. |
| Telemetry | SM activity, clocks, power, and thermal response. |
| Result | Synthetic rotary tokens per second. |

It is a hardware-path diagnostic, not a replacement for a model runtime's
rotary embedding implementation.
