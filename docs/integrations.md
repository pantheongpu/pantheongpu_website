---
title: Integrations
description: Run PantheonGPU from Slurm, NHC, ReFrame and GitHub Actions, with a node check that answers with a verdict and an exit code.
---

<div class="page-intro" markdown>
<p class="page-intro__eyebrow">Integrations</p>

# Put PantheonGPU where your cluster already looks

A scheduler wants a yes or a no about a node, not a table. These files turn a Pantheon run into that answer. They are in the source repository under [`integrations/`](https://github.com/pantheongpu/pantheon/tree/main/integrations), and they work with Pantheon 1.2.2 and later.
</div>

| Where | What it does | Files |
|---|---|---|
| Anything that reads an exit code | Runs the workloads you name and answers with a verdict for the node and for each card | [`pantheon_node_check.py`](https://github.com/pantheongpu/pantheon/blob/main/integrations/pantheon_node_check.py) |
| Slurm | Tests the cards of a job when it ends, and accepts a node before it goes into service | [`slurm/`](https://github.com/pantheongpu/pantheon/tree/main/integrations/slurm) |
| NHC | Adds `check_pantheon` to the node health check that Slurm or PBS runs | [`nhc/`](https://github.com/pantheongpu/pantheon/tree/main/integrations/nhc) |
| ReFrame | A regression test with a score and a temperature for each card | [`reframe/`](https://github.com/pantheongpu/pantheon/tree/main/integrations/reframe) |
| GitHub Actions | Checks the cards of a self-hosted runner before a job uses them | [Pantheon GPU Health Check](https://github.com/marketplace/actions/pantheon-gpu-health-check) |

Each one is a plain file that you copy. None of them is installed with the `pantheon-gpu` package.

## The node check

`pantheon_node_check.py` needs Python 3.9 or later and nothing else. It runs Pantheon, reads the reports, and prints one line for the node and one for each card:

```console
$ pantheon_node_check.py --gpu 0 --duration 8
PANTHEON HEALTHY: 1 GPU HEALTHY
GPU 0 (NVIDIA GeForce RTX 3060): HEALTHY, memory_read 336.269 GB/s, march_test 2901230000.0 march-ops/s
  note: PCIe link recovery during memory_read, march_test: link power-state cycling, not a fault
$ echo $?
0
```

A card that returns wrong data, here with Pantheon's own fault injection:

```console
$ pantheon_node_check.py --gpu 0 --test march_test --duration 5
PANTHEON FAULT: GPU 0 FAULT (march_test failed: memory errors detected or the workload aborted)
GPU 0 (NVIDIA GeForce RTX 3060): FAULT, march_test failed: memory errors detected or the workload aborted
$ echo $?
2
```

| Exit code | Verdict | Meaning |
|---|---|---|
| 0 | `HEALTHY` | Every workload completed and nothing was found |
| 0 | `SKIPPED` | The job has no GPU, so nothing was tested |
| 1 | `WATCH` | The card works, and something deserves a look: heat, correctable errors, or a workload that did not complete |
| 2 | `FAULT` | A memory test failed, or the card counted uncorrectable errors during the run |
| 3 | `INCOMPLETE`, `NO GPU TESTED`, `NOT RUN` | Nothing was tested or the run did not finish. It is never a pass |

The verdict comes from the reports and not from Pantheon's exit code. Pantheon exits with an error when a workload fails; errors that a card counted during a run that completed are in the report only.

Without `nvcc` or `hipcc` on the node, Pantheon runs on a CPU backend that tests no hardware. The check answers `NO GPU TESTED` and exit code 3 in that case.

## Slurm

The epilog tests the cards of each job that had a GPU, for 10 seconds, and drains the node when a card has a fault. Only a fault drains the node; a warning goes to the log.

```bash
install -m 755 pantheon_node_check.py /usr/local/sbin/pantheon_node_check.py
install -m 755 slurm/epilog.sh /etc/slurm/epilog.d/50-pantheon.sh
```

After a job on a card with an injected fault, on our test cluster:

```console
$ scontrol show node node1 | grep -o -E 'State=[A-Z+]+|Reason=.*'
State=IDLE+DRAIN
Reason=PANTHEON FAULT: GPU 0 FAULT (march_test failed: memory errors detected or the workload aborted) [root@2026-09-29T16:18:37]
```

`slurm/burnin.sbatch` is an acceptance job for one node. It runs four workloads on every card, keeps the reports, and fails when the verdict is not `HEALTHY`:

```bash
sbatch --nodelist=node042 --gres=gpu:8 burnin.sbatch
```

The [Slurm README](https://github.com/pantheongpu/pantheon/blob/main/integrations/slurm/README.md) has the settings and what each costs in time.

## NHC

NHC's own GPU check calls `nvidia-healthmon`, which NVIDIA no longer ships. `check_pantheon` tests the memory of each card, and it is the same check on NVIDIA and on AMD cards. In `/etc/nhc/nhc.conf`:

```
* || export TIMEOUT=90
* || check_pantheon
```

The check loads the GPUs, so let NHC run it on idle nodes only, with `HealthCheckNodeState=IDLE` in `slurm.conf`. The [NHC README](https://github.com/pantheongpu/pantheon/blob/main/integrations/nhc/README.md) has the rest.

## ReFrame

The test runs one workload on the GPUs of a node and reports the score and the highest temperature of each card as performance values, so a card that got slower shows up against the reference of its node type.

```console
$ reframe -C settings_example.py -c pantheon_check.py -r --exec-policy serial -S devices=0 -S duration=5
[  PASSED  ] Ran 4/4 test case(s) from 4 check(s) (0 failure(s), 0 expected failure(s), 0 skipped, 0 aborted)
```

The [ReFrame README](https://github.com/pantheongpu/pantheon/blob/main/integrations/reframe/README.md) lists the variables.

## How much load a check puts on a card

The workload sets the load, so a check can be as gentle as it needs to be. Average power during the run, as the median over the cards in our [database](benchmarks.md):

| Workload | A100 SXM4 40GB (limit 400 W) | L40S (limit 350 W) | H100 PCIe (limit 350 W) |
|---|---|---|---|
| `galpat`, memory pattern test | 101 W | 87 W | 91 W |
| `march_test`, memory pattern test | 176 W | 185 W | 176 W |
| `memory_read`, memory bandwidth | 283 W | 218 W | 346 W |
| `incinerator`, compute | 307 W | 265 W | 289 W |

## What we tested, and what we did not

We ran the node check on two RTX 3060 cards, with and without an injected fault. We ran the epilog, the acceptance job and the NHC check under Slurm 23.11.4 on a one-node test cluster with Pantheon on its CPU backend, and the ReFrame test with ReFrame 4.10.4 on an RTX 3060.

We have not run these files on a cluster with real GPUs under Slurm, on AMD cards, or with MIG devices. If you do, tell us how it went in the [discussions](https://github.com/pantheongpu/pantheon/discussions).
