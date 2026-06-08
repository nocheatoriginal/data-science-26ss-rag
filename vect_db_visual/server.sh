#!/usr/bin/env bash

set -Eeuo pipefail

PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PID=""

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
RESET="\033[0m"

log_info() {
  printf "${BLUE}[INFO]${RESET} %s\n" "$1"
}

log_success() {
  printf "${GREEN}[OK]${RESET} %s\n" "$1"
}

log_warn() {
  printf "${YELLOW}[WARN]${RESET} %s\n" "$1"
}

log_error() {
  printf "${RED}[ERROR]${RESET} %s\n" "$1" >&2
}

cleanup() {
  if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" 2>/dev/null; then
    log_warn "Stopping HTTP server (PID ${SERVER_PID})..."
    kill "${SERVER_PID}" 2>/dev/null || true
    wait "${SERVER_PID}" 2>/dev/null || true
    log_success "HTTP server stopped. Port ${PORT} is free again."
  fi
}

port_is_used() {
  lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1
}

trap cleanup EXIT
trap 'log_warn "Interrupt received."; exit 130' INT
trap 'log_warn "Termination signal received."; exit 143' TERM

if ! command -v python3 >/dev/null 2>&1; then
  log_error "python3 was not found. Please install Python 3 or check your PATH."
  exit 1
fi

if ! command -v lsof >/dev/null 2>&1; then
  log_error "lsof was not found. This script needs lsof to check the port."
  exit 1
fi

if port_is_used; then
  log_error "Port ${PORT} is already in use:"
  lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >&2 || true
  exit 1
fi

log_info "Starting HTTP server..."
log_info "Root: ${ROOT_DIR}"
log_info "Address: http://${HOST}:${PORT}"

cd "${ROOT_DIR}"
python3 -m http.server "${PORT}" --bind "${HOST}" &
SERVER_PID="$!"

sleep 0.5

if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
  log_error "HTTP server could not be started."
  exit 1
fi

log_success "HTTP server is running (PID ${SERVER_PID}). Press Ctrl+C to stop."
wait "${SERVER_PID}"
