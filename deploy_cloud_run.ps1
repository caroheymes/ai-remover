param(
    [string]$ProjectId = "",
    [string]$Region = "europe-west1",
    [string]$RepoName = "ai-remover",
    [string]$ServiceName = "ai-remover-api",
    [string]$ApiToken = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    $ProjectId = (gcloud config get-value project 2>$null).Trim()
}
if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    throw "Aucun projet GCP actif. Passez -ProjectId <ID_PROJET> ou executez 'gcloud config set project <ID_PROJET>'."
}

if ([string]::IsNullOrWhiteSpace($ApiToken)) {
    $bytes = New-Object byte[] 24
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $ApiToken = ($bytes | ForEach-Object { $_.ToString("x2") }) -join ""
}

$ImageUri = "$Region-docker.pkg.dev/$ProjectId/$RepoName/api:latest"

Write-Host "[1/5] Verification des API Cloud Build, Cloud Run et Artifact Registry sur $ProjectId..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project $ProjectId

Write-Host "[2/5] Verification du depot Artifact Registry ($RepoName dans $Region)..."
$repoExists = $true
try {
    gcloud artifacts repositories describe $RepoName --location=$Region --project=$ProjectId *> $null
    if ($LASTEXITCODE -ne 0) { $repoExists = $false }
} catch {
    $repoExists = $false
}

if (-not $repoExists) {
    gcloud artifacts repositories create $RepoName `
        --repository-format=docker `
        --location=$Region `
        --description="Images Docker AI-Remover API" `
        --project=$ProjectId
}

Write-Host "[3/5] Application de la regle FinOps de purge automatique (conservation des 2 dernieres images uniquement)..."
$policyJson = @'
[
  {
    "name": "keep-latest-2",
    "action": {"type": "Keep"},
    "mostRecentVersions": {"keepCount": 2}
  },
  {
    "name": "delete-older-revisions",
    "action": {"type": "Delete"},
    "condition": {"tagState": "ANY"}
  }
]
'@
$policyFile = Join-Path $env:TEMP "ai_remover_ar_cleanup_policy.json"
Set-Content -Path $policyFile -Value $policyJson -Encoding UTF8
gcloud artifacts repositories set-cleanup-policies $RepoName `
    --location=$Region `
    --policy=$policyFile `
    --project=$ProjectId `
    --no-dry-run
Remove-Item -Path $policyFile -ErrorAction SilentlyContinue

Write-Host "[4/5] Build de l'image conteneur legere via Cloud Build..."
gcloud builds submit --tag $ImageUri --project $ProjectId .

Write-Host "[5/5] Deploiement sur Cloud Run (min-instances=0, max-instances=2, 512Mi, jeton Bearer actif, zero cle Gemini stockee)..."
gcloud run deploy $ServiceName `
    --image $ImageUri `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --min-instances 0 `
    --max-instances 2 `
    --memory 512Mi `
    --cpu 1 `
    --cpu-throttling `
    --concurrency 10 `
    --timeout 120 `
    --port 8080 `
    --set-env-vars "AI_REMOVER_API_TOKEN=$ApiToken" `
    --project $ProjectId

$ServiceUrl = (gcloud run services describe $ServiceName --region $Region --project $ProjectId --format="value(status.url)").Trim()

Write-Host ""
Write-Host "Deploiement termine."
Write-Host "URL du service : $ServiceUrl"
Write-Host "Jeton Bearer   : $ApiToken"
Write-Host ""
Write-Host "Exemple d'appel securise :"
Write-Host "Invoke-RestMethod -Method Post -Uri '$ServiceUrl/api/v1/humanize' -Headers @{'Authorization'='Bearer $ApiToken'; 'X-Gemini-API-Key'='<VOTRE_CLE_GEMINI>'} -ContentType 'application/json' -Body '{`"text`":`"Texte a humaniser`",`"profile_id`":`"architecte`"}'"
