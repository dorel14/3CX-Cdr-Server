# Stoppe le script en cas d'erreur
$ErrorActionPreference = "Stop"

# Charger les variables d'environnement
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^(.*?)=(.*)$') {
            Set-Item -Path "Env:$($matches[1])" -Value "$($matches[2])"
        }
    }
}

Write-Host "📦 Sauvegarde de la base de données..."
if (-Not (Test-Path -Path db_folder)) {
    New-Item -ItemType Directory -Path db_folder -Force | Out-Null
}
docker exec $Env:DB_CONTAINER pg_dump -U $Env:DB_USER -d $Env:DB_NAME > db_folder/backup.sql

Write-Host "📂 Détection des fichiers déplacés..."

# Récupérer les fichiers renommés (RXXX) et les déplacer
$renamedFiles = git diff --name-status master origin/master | Where-Object { $_ -match '^R\d+\s+(.+)\s+(.+)$' }

foreach ($line in $renamedFiles) {
    if ($line -match '^R\d+\s+(.+)\s+(.+)$') {
        $old = $matches[1]
        $new = $matches[2]

        if (Test-Path $old) {
            Write-Host "🔄 Déplacement de $old vers $new..."
            New-Item -ItemType Directory -Path (Split-Path $new) -Force | Out-Null
            Move-Item -Path $old -Destination $new -Force
        }
    }
}

Write-Host "🛠 Réinitialisation de la branche master..."
git fetch origin
git checkout master
git reset --hard origin/master

Write-Host "🧹 Nettoyage des fichiers obsolètes..."
git clean -df

Write-Host "🚀 Reconstruction de l'environnement..."
docker-compose down
docker-compose up -d --build

Write-Host "✅ Mise à jour terminée !"
