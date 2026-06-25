#!/bin/sh
# One-time TLS bootstrap for Zoids League.
# Obtains the first Let's Encrypt certificate so Nginx can start with HTTPS.
# Run this ONCE on the VPS after filling in .env and pointing DNS to the server.
set -e

COMPOSE="docker compose -f docker-compose.prod.yml"

# Load DOMAIN and CERTBOT_EMAIL from .env.
if [ ! -f .env ]; then
  echo "ERROR: .env not found. Copy .env.example to .env first."
  exit 1
fi
# shellcheck disable=SC1091
. ./.env

if [ -z "$DOMAIN" ] || [ -z "$CERTBOT_EMAIL" ]; then
  echo "ERROR: DOMAIN and CERTBOT_EMAIL must be set in .env."
  exit 1
fi

CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

echo "### Creating a temporary self-signed certificate so Nginx can boot..."
$COMPOSE run --rm --entrypoint "\
  sh -c 'mkdir -p $CERT_PATH && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout $CERT_PATH/privkey.pem \
    -out $CERT_PATH/fullchain.pem \
    -subj /CN=localhost'" certbot

echo "### Building and starting Nginx..."
$COMPOSE up -d --build nginx

echo "### Deleting the temporary certificate..."
$COMPOSE run --rm --entrypoint "\
  rm -rf /etc/letsencrypt/live/$DOMAIN \
  /etc/letsencrypt/archive/$DOMAIN \
  /etc/letsencrypt/renewal/$DOMAIN.conf" certbot

echo "### Requesting the real Let's Encrypt certificate..."
$COMPOSE run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --email $CERTBOT_EMAIL \
    -d $DOMAIN -d www.$DOMAIN \
    --rsa-key-size 2048 \
    --agree-tos \
    --no-eff-email \
    --force-renewal" certbot

echo "### Reloading Nginx with the real certificate..."
$COMPOSE exec nginx nginx -s reload

echo "### Done. TLS is set up for https://$DOMAIN"
