# Download NoLiMa dataset and code from GitHub and HuggingFace
# License: Adobe Research License (non-commercial research only)
# Source: https://github.com/adobe-research/NoLiMa
# Dataset: https://huggingface.co/datasets/amodaresi/NoLiMa

$ErrorActionPreference = "Stop"
$DownloadDir = $PSScriptRoot

Write-Host "Downloading NoLiMa repository and dataset..." -ForegroundColor Cyan

# Clone the GitHub repo
$repoDir = Join-Path $DownloadDir "NoLiMa"
if (-not (Test-Path $repoDir)) {
    Write-Host "Cloning adobe-research/NoLiMa from GitHub..."
    git clone https://github.com/adobe-research/NoLiMa.git $repoDir
} else {
    Write-Host "Repository already exists. Pulling latest..."
    Push-Location $repoDir
    git pull
    Pop-Location
}

# Download dataset from HuggingFace (requires huggingface_hub or git-lfs)
$dataDir = Join-Path $repoDir "data"
if (-not (Test-Path (Join-Path $dataDir "needlesets"))) {
    Write-Host "Downloading NoLiMa data from HuggingFace..."
    Push-Location $repoDir
    if (Test-Path "data/download_NoLiMa_data.sh") {
        # Convert bash script to PowerShell equivalent
        Write-Host "Running download script (requires git-lfs)..."
        # The script downloads from: https://huggingface.co/datasets/amodaresi/NoLiMa
        # Manual alternative:
        Write-Host "If download_NoLiMa_data.sh fails, manually download from:"
        Write-Host "  https://huggingface.co/datasets/amodaresi/NoLiMa"
        Write-Host "  Place contents in: $dataDir"
        bash data/download_NoLiMa_data.sh
    }
    Pop-Location
} else {
    Write-Host "Data already downloaded."
}

Write-Host "`nDownload complete. Contents:" -ForegroundColor Green
Write-Host "  Repository: $repoDir"
Write-Host "  Needle sets: $dataDir\needlesets\"
Write-Host "  Haystacks: $dataDir\haystack\"
Write-Host "`nKey files:"
Write-Host "  - needle_set.json (58 question-needle pairs)"
Write-Host "  - needle_set_hard.json (10 hardest pairs)"
Write-Host "  - evaluation/ (evaluation scripts)"
Write-Host "  - evaluation/model_configs/ (model configuration templates)"
