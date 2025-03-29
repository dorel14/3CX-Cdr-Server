#!/bin/bash

set -e  # Stoppe le script en cas d'erreur

# Charger les variables d'environnement
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "📦 Sauvegarde de la base de données..."
[ ! -d db_folder ] && mkdir -p db_folder
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > db_folder/backup.sql

echo "📂 Détection des fichiers déplacés..."

# Récupérer les fichiers renommés (RXXX) et les déplacer
git diff --name-status master origin/master | awk '$1 ~ /^R/ {print $2, $3}' | while read old new; do
    if [ -e "$old" ]; then
        echo "🔄 Déplacement de $old vers $new..."
        mkdir -p "$(dirname "$new")"
        mv "$old" "$new"
    fi
done

echo "🛠 Réinitialisation de la branche master..."
git fetch origin
git checkout master
git reset --hard origin/master

echo "🧹 Nettoyage des fichiers obsolètes..."
git clean -df

echo "🚀 Reconstruction de l'environnement..."
docker-compose down
docker-compose up -d --build

echo "✅ Mise à jour terminée !"
