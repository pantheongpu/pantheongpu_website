$ErrorActionPreference = "Stop"
$website = "C:\Users\sssnk\OneDrive\Documents\pantheon_publish_tmp"
$remote = "ubuntu@137.131.6.1"
$key = "/home/saqib/.ssh/id_rsa"
$ssh = "ssh -o StrictHostKeyChecking=no -o BatchMode=yes -i $key $remote"
$scp = "scp -o StrictHostKeyChecking=no -o BatchMode=yes -i $key"
$workloads = @(
  "memory_retention_bake", "memory_pc_pingpong", "memory_bank_thrash", "memory_tsv_thrasher",
  "tlb_avalanche", "ras_validator", "int_virus", "scheduler", "mma_virus", "fp64_virus",
  "memory_write", "memory_write_agg", "memory_read", "memory_read_agg", "voltage", "incinerator",
  "cache_lat", "sfu_stress", "pcie_bandwidth", "pulse_virus", "tensor_virus", "atomic_virus",
  "omni_virus", "p2p_thrasher", "all_reduce", "transformer_virus", "llm_decode", "llm_prefill",
  "kv_cache_churn", "fused_attention", "rope_stress", "quantized_gemm", "serving_mix",
  "speculative_decode", "moe_router", "transformer_train_step", "allocation_fragmentation",
  "graph_replay", "rag_embedding", "vision_encoder", "rt_virus", "media_enc_virus"
)

function Invoke-Wsl([string]$script) {
  & wsl.exe -d Ubuntu-24.04 -- bash -lc $script
  return $LASTEXITCODE
}

foreach ($workload in $workloads) {
  $started = Get-Date
  Write-Host "[$started] START $workload"
  $runCommand = "$ssh 'cd /home/ubuntu/pantheongpu && python3 pantheon.py --platform cuda --test $workload --duration 300 --gpu all --mem 50 --verify'"
  $runCode = Invoke-Wsl $runCommand
  $runId = (& wsl.exe -d Ubuntu-24.04 -- bash -lc "$ssh 'ls -td /home/ubuntu/pantheongpu/results/* | head -1'").Trim()
  $runId = Split-Path $runId -Leaf
  $copy = "${remote}:/home/ubuntu/pantheongpu/database/pantheon_report_${runId}_0001_${workload}_gpu*.json /mnt/c/Users/sssnk/OneDrive/Documents/pantheon_publish_tmp/database/"
  $copyCode = Invoke-Wsl "$scp $copy"
  if ($copyCode -eq 0) {
    Push-Location $website
    try {
      python website_utils/generate_web_data.py | Select-Object -Last 1
      python -m pytest -q
      & C:\Users\sssnk\OneDrive\Documents\pantheon\.venv\Scripts\mkdocs.exe build --strict
      git add "database/pantheon_report_${runId}_0001_${workload}_gpu*.json" docs/assets/web_data.json
      git commit -m "Add Lambda A100 $workload benchmark"
      git push origin HEAD:main
    } finally { Pop-Location }
  } else {
    Write-Warning "No per-GPU report files found for $workload (run exit $runCode, copy exit $copyCode)"
  }
  Write-Host "[$(Get-Date)] DONE $workload"
}
