#!/bin/bash
# Installs Voice Clone on a Mac with Apple Silicon (M1 or newer) and opens it.
# Paste this line into Terminal:
#
#   curl -fsSL https://raw.githubusercontent.com/newboy617-jpg/Abhi/claude/admiring-thompson-xh1iz2/install-mac.sh | bash
#
# Everything goes in ~/VoiceClone. Run it again any time to update; your voices are kept.

main() {
  set -euo pipefail
  local repo="newboy617-jpg/Abhi"
  local branch="${VOICECLONE_BRANCH:-claude/admiring-thompson-xh1iz2}"
  local app="$HOME/VoiceClone"

  if [ "$(uname -s)" != "Darwin" ]; then
    echo "This installer is for macOS. See the README for Windows and Linux."
    exit 1
  fi
  if [ "$(uname -m)" != "arm64" ]; then
    if [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = "1" ]; then
      echo "Terminal is running in Intel (Rosetta) mode. Quit Terminal, find it in"
      echo "Applications > Utilities, press Cmd+I, untick 'Open using Rosetta', then try again."
    else
      echo "Sorry, the voice models need a Mac with Apple Silicon (M1 or newer)."
    fi
    exit 1
  fi

  echo "==> Downloading Voice Clone into $app"
  local tmp
  tmp="$(mktemp -d)"
  curl -fsSL "https://github.com/$repo/archive/refs/heads/$branch.tar.gz" | tar -xz -C "$tmp" --strip-components=1
  mkdir -p "$app"
  cp -R "$tmp/." "$app/"
  rm -rf "$tmp"

  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v uv >/dev/null 2>&1; then
    echo "==> Installing uv (it sets up Python for the app)"
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi

  echo "==> Setting up Python"
  [ -x "$app/.venv/bin/python" ] || uv venv --python 3.12 "$app/.venv"

  echo "==> Installing the app's software (this takes a few minutes)"
  uv pip install --python "$app/.venv/bin/python" -r "$app/requirements-voiceclone.txt"

  echo "==> Creating the 'Voice Clone' shortcut"
  local launcher="$app/Voice Clone.command"
  cat > "$launcher" <<EOF
#!/bin/bash
# Double-click to open Voice Clone in your browser. Close this window to quit it.
cd "$app" && exec ./.venv/bin/python -m voiceclone ui
EOF
  chmod +x "$launcher"
  if cp "$launcher" "$HOME/Desktop/" 2>/dev/null; then
    echo "    Next time, double-click 'Voice Clone' on your Desktop."
  else
    echo "    Next time, double-click 'Voice Clone' in the VoiceClone folder in your home folder."
  fi

  echo
  echo "All done! Opening Voice Clone in your browser."
  echo "Keep this window open while you use it (close it to quit)."
  echo "The first time you make speech, it downloads the voice model (a few GB)."
  cd "$app"
  exec ./.venv/bin/python -m voiceclone ui
}

main "$@"
