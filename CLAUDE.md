# Pantheon GPU Project Context
A diagnostic and stress-testing suite for NVIDIA (CUDA) and AMD (ROCm/SYCL) GPUs, optimized for WSL2. Specializes in Silent Data Corruption (SDC) detection.

## Essential Commands
- **Install Dependencies (Ubuntu/WSL):** `sudo apt-get update && sudo apt-get install -y python3-tk python3-pip nvidia-cuda-toolkit`
- **Install Python Stack:** `pip install numpy psutil pandas openpyxl cmake customtkinter pyinstaller uvicorn`
- **Run Full Gauntlet:** `./pantheon --test all --duration 30 --verify`
- **SDC Check:** Always include the `--verify` flag to catch bit-flips in real-time.

## Hardware & Environment Rules
- **WSL2 Driver Rule:** IMPORTANT: Do NOT install Linux GPU drivers inside WSL. Use host Windows drivers only.
- **Hardware Targets:** Primary development on NVIDIA RTX 3080 Ti (350W TDP).
- **Architecture:** Xenon-optimized kernels; focus on Integer, Tensor, and RT core saturation.

## Code Conventions
- **Naming:** Use the compiled executable `pantheon` for user-facing instructions; `pantheon.py` is the source.
- **Team Voice:** Always use "We" in documentation and social outreach messages.
- **SDC Messaging:** Every test result must be validated. "Passed" means 0 bit-flips detected.
