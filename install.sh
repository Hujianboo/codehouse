#!/usr/bin/env sh
set -eu

REPO="${CODEHOUSE_REPO:-Hujianboo/codehouse}"
REF="${CODEHOUSE_REF:-main}"
INSTALL_DIR="${CODEHOUSE_INSTALL_DIR:-$HOME/.local/share/codehouse}"
BIN_DIR="${CODEHOUSE_BIN_DIR:-$HOME/.local/bin}"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${REF}"

say() {
  printf '%s\n' "$*"
}

die() {
  say "codehouse install: $*" >&2
  exit 1
}

have() {
  command -v "$1" >/dev/null 2>&1
}

download() {
  url="$1"
  dest="$2"
  if have curl; then
    curl -fsSL "$url" -o "$dest"
  elif have wget; then
    wget -qO "$dest" "$url"
  else
    die "curl or wget is required"
  fi
}

profile_path() {
  shell_name="$(basename "${SHELL:-}")"
  case "$shell_name" in
    zsh)
      printf '%s\n' "$HOME/.zshrc"
      ;;
    bash)
      if [ "$(uname -s 2>/dev/null || true)" = "Darwin" ]; then
        printf '%s\n' "$HOME/.bash_profile"
      else
        printf '%s\n' "$HOME/.bashrc"
      fi
      ;;
    *)
      printf '%s\n' "$HOME/.profile"
      ;;
  esac
}

path_contains_bin_dir() {
  case ":$PATH:" in
    *":$BIN_DIR:"*) return 0 ;;
    *) return 1 ;;
  esac
}

add_path_to_profile() {
  profile="$1"
  marker="codehouse installer"
  mkdir -p "$(dirname "$profile")"
  touch "$profile"

  if grep -F "$marker" "$profile" >/dev/null 2>&1; then
    say "PATH entry already exists in $profile"
    return 0
  fi

  {
    printf '\n'
    printf '# Added by %s\n' "$marker"
    printf 'export PATH="$HOME/.local/bin:$PATH"\n'
  } >>"$profile"

  say "Added ~/.local/bin to PATH in $profile"
}

maybe_add_path_to_profile() {
  if path_contains_bin_dir; then
    return 0
  fi

  say ""
  say "$BIN_DIR is not currently in PATH."

  profile="$(profile_path)"
  if [ "${CODEHOUSE_UPDATE_PROFILE:-}" = "1" ]; then
    add_path_to_profile "$profile"
    return 0
  fi

  if [ -r /dev/tty ] && [ -w /dev/tty ]; then
    printf 'Add it to %s now? [y/N] ' "$profile" >/dev/tty
    IFS= read -r answer </dev/tty || answer=""
    case "$answer" in
      y|Y|yes|YES|Yes)
        add_path_to_profile "$profile"
        say "Open a new terminal, or run: export PATH=\"\$HOME/.local/bin:\$PATH\""
        return 0
        ;;
    esac
  fi

  say "To use codehouse from any terminal, add this to your shell profile:"
  say "  export PATH=\"\$HOME/.local/bin:\$PATH\""
}

main() {
  have python3 || die "python3 is required. Please install Python 3 and run this installer again."

  mkdir -p "$INSTALL_DIR" "$BIN_DIR"

  tmp_file="${INSTALL_DIR}/codex_house.py.tmp"
  download "${RAW_BASE}/codex_house.py" "$tmp_file"
  mv "$tmp_file" "${INSTALL_DIR}/codex_house.py"

  version_tmp="${INSTALL_DIR}/VERSION.tmp"
  if download "${RAW_BASE}/VERSION" "$version_tmp"; then
    mv "$version_tmp" "${INSTALL_DIR}/VERSION"
  else
    rm -f "$version_tmp"
  fi

  launcher="${BIN_DIR}/codehouse"
  cat >"$launcher" <<EOF
#!/usr/bin/env sh
exec python3 "$INSTALL_DIR/codex_house.py" "\$@"
EOF
  chmod +x "$launcher"

  legacy="${BIN_DIR}/codex-house"
  if ln -sf "$launcher" "$legacy" 2>/dev/null; then
    :
  else
    cat >"$legacy" <<EOF
#!/usr/bin/env sh
exec "$launcher" "\$@"
EOF
    chmod +x "$legacy"
  fi

  say "Installed codehouse:"
  say "  $launcher"
  say "  $legacy"

  maybe_add_path_to_profile

  say ""
  say "Try it:"
  say "  codehouse"
  say "  codehouse --once"
}

main "$@"
