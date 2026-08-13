# Vision Encoder

`vision_encoder` applies image-tile projection pressure representative of dense
compute and memory work in multimodal vision encoder front ends.

```bash
pantheon --test vision_encoder --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Compute | Dense image-tile projection-style arithmetic. |
| Memory | Synthetic image-state working-set reads. |
| Telemetry | SM/cache/DRAM activity, power, clocks, and thermals. |
| Result | Synthetic image tiles per second. |

This is not an image-classification, vision-language, or accuracy benchmark.
Use it to compare GPU-side behavior across hardware and configuration changes.
