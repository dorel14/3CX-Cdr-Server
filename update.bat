@echo off
setlocal enabledelayedexpansion

echo 📦 Sauvegarde de la base de données...
for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b
if not exist db_folder mkdir db_folder
docker exec %DB_CONTAINER% pg_dump -U %DB_USER% -d %DB_NAME% > db_folder/backup.sql

echo 📂 Détection des fichiers déplacés...

:: Récupérer les fichiers renommés (RXXX) et les déplacer
for /f "tokens=1,2,3 delims= " %%a in ('git diff --name-status master origin/master') do (
    if "%%a"=="R100" (
        set "OLD_PATH=%%b"
        set "NEW_PATH=%%c"

        if exist "!OLD_PATH!" (
            echo 🔄 Déplacement de !OLD_PATH! vers !NEW_PATH!...
            mkdir "!NEW_PATH!" 2>nul
            move "!OLD_PATH!" "!NEW_PATH!"
        )
    )
)

echo 🛠 Réinitialisation de la branche master...
git fetch origin
git checkout master
git reset --hard origin/master

echo 🧹 Nettoyage des fichiers obsolètes...
git clean -df

echo 🚀 Reconstruction de l'environnement...
docker-compose down
docker-compose up -d --build

echo ✅ Mise à jour terminée !
pause
