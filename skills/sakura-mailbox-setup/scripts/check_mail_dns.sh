#!/bin/sh
set -eu

DOMAIN="${1:-}"
FROM_ADDRESS="${2:-}"

if [ -z "$DOMAIN" ] || [ -z "$FROM_ADDRESS" ]; then
  echo "Usage: $0 example.com notify@example.com" >&2
  exit 2
fi

echo "== Local mail commands =="
command -v sendmail || true
command -v mail || true
if command -v php >/dev/null 2>&1; then
  php -i 2>/dev/null | grep -i 'sendmail_path\|sendmail_from' || true
fi

echo
echo "== DNS =="
if command -v dig >/dev/null 2>&1; then
  dig +short A "$DOMAIN" || true
  dig +short MX "$DOMAIN" || true
  dig +short TXT "$DOMAIN" || true
  dig +short TXT "_dmarc.$DOMAIN" || true
else
  echo "dig not found"
fi

echo
echo "From address to configure: $FROM_ADDRESS"

