#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
APP_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)
COMPOSE_FILE="$APP_DIR/docker-compose.yml"
NGINX_CONF="$APP_DIR/nginx/default.conf"
STATE_FILE="$SCRIPT_DIR/active_color"
MAX_ATTEMPTS=12

compose() {
  docker-compose -f "$COMPOSE_FILE" "$@"
}

active_color=$(cat "$STATE_FILE" 2>/dev/null || printf 'blue')
case "$active_color" in
  blue) inactive_color=green ;;
  green) inactive_color=blue ;;
  *)
    printf 'Invalid active color in %s: %s\n' "$STATE_FILE" "$active_color" >&2
    exit 1
    ;;
esac

rollback() {
  printf 'Deployment failed; keeping %s active and stopping %s.\n' "$active_color" "$inactive_color" >&2
  compose --profile "$inactive_color" stop "app-$inactive_color" || true
}

trap rollback ERR

printf 'Deploying %s while %s remains active.\n' "$inactive_color" "$active_color"
compose up -d redis nginx
compose --profile "$inactive_color" up -d --build "app-$inactive_color"

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  if compose exec -T "app-$inactive_color" python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"; then
    break
  fi

  if [ "$attempt" -eq "$MAX_ATTEMPTS" ]; then
    printf 'Healthcheck did not pass after %s attempts.\n' "$MAX_ATTEMPTS" >&2
    exit 1
  fi
  sleep 2
done

status=$(compose exec -T "app-$inactive_color" python -c \
  "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/status').read().decode())")
case "$status" in
  *"\"deploy_color\":\"$inactive_color\""*) ;;
  *)
    printf 'Smoke test failed: expected deploy_color=%s, got %s\n' "$inactive_color" "$status" >&2
    exit 1
    ;;
esac

sed -i "s/set \$upstream app-$active_color;/set \$upstream app-$inactive_color;/" "$NGINX_CONF"
compose exec -T nginx nginx -s reload
printf '%s\n' "$inactive_color" > "$STATE_FILE"
compose --profile "$active_color" stop "app-$active_color" || true
trap - ERR

printf 'Deployment complete: %s is now active.\n' "$inactive_color"