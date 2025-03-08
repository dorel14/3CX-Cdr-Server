#!/bin/sh

WEB_SERVER_NAME=${WEB_SERVER_NAME:-localhost}

# Vérifie si le domaine principal est résolu sur Internet
#if nslookup "$WEB_SERVER_NAME" 8.8.8.8 | grep -q "Address"; then
#    echo "[INFO] $WEB_SERVER_NAME est déjà résolu sur Internet. Pas besoin de dnsmasq."
#    exit 0
#else
    echo "[INFO] $WEB_SERVER_NAME n'est pas résolu. Activation de dnsmasq pour sous-domaines."
    echo "address=/${WEB_SERVER_NAME}/172.18.0.190" >> /etc/dnsmasq.d/mydnsmasq.conf
    echo "address=/*.${WEB_SERVER_NAME}/172.18.0.190" >> /etc/dnsmasq.d/mydnsmasq.conf
    # Démarre dnsmasq avec redirection de tous les sous-domaines vers 127.0.0.1
#fi
