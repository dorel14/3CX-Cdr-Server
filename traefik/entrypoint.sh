#!/bin/sh
set -e  # Stoppe le script si une commande échoue

# Vérifie que SERVER_PORT est bien défini
if [ -z "$SERVER_PORT" ]; then
  echo "[ERROR] SERVER_PORT n'est pas défini !"
  exit 1
fi

echo "[INFO] Démarrage de Traefik avec SERVER_PORT=$SERVER_PORT"

exec traefik --entryPoints.tcp.address=":$SERVER_PORT" --configFile=/etc/traefik/traefik.yml