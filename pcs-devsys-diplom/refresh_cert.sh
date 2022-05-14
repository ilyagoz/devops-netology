#!/bin/bash
set -e

APP_TOKEN=$(curl --request POST --data @payload.json $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)
curl --header "X-Vault-Token: $APP_TOKEN" --request POST --data \
     '{"common_name": "www1.local", "ttl": "24h", "format": "pem_bundle"}' \
     $VAULT_ADDR/v1/pki_int/issue/webserver | jq > cert.json

jq -r .data.certificate < cert.json > $(hostname -f).crt
jq -r .data.private_key < cert.json > $(hostname -f).key
sudo cp $(hostname -f).crt /etc/ssl/certs/
sudo cp $(hostname -f).key /etc/ssl/private/

sudo systemctl restart nginx
echo Certificates refreshed at $(date) > last_refresh

