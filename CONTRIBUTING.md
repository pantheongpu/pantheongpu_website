# Contributing to Pantheon

Pantheon uses this public repository for documentation, releases, benchmark data, and community feedback. The GPU stress-runner source remains private; public binary releases are available from the [release page](https://pantheongpu.com/release/).

## Choose the right channel

- **GitHub Discussions**: installation help, workload ideas, benchmark showcases, and general questions.
- **Benchmark submission issue**: a raw `pantheon_report_*.json` result that you permit Pantheon to publish.
- **Hardware regression issue**: a reproducible crash, artifact, system hang, throttling anomaly, or score regression.
- **Security advisory**: a potential vulnerability. Do not disclose it in a public issue or discussion.

## Benchmark submissions

Use the benchmark submission form and include the exact Pantheon version, GPU, OS, driver, CUDA/ROCm version, command, duration, and cooling/power conditions. Attach the raw JSON report after removing any information you do not want published.

Results are reviewed before publication. Community submissions may be marked separately from maintainer-verified results, and Pantheon may decline results that are incomplete, unsafe, unreproducible, or lack permission to publish.

## Pull requests

Documentation, website, benchmark-data, and release-page pull requests are welcome. Keep each change focused, run `python -m pytest`, and run `python -m mkdocs build --strict` before opening a pull request.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
