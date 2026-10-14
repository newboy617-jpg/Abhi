#!/bin/bash
# Shoot Ravan's Ten Heads: opens the game full screen, like an app, with sound ready from the start.
# Double-click this file. The first time, macOS may refuse: right-click it, choose Open, then press Open.
cd "$(dirname "$0")" || exit 1
GAME="shoot-ravan.html"
[ -f "$GAME" ] || GAME="index.html"
if [ ! -f "$GAME" ]; then
  osascript -e 'display alert "Ravan game not found" message "Keep this launcher in the same folder as shoot-ravan.html."' >/dev/null 2>&1
  exit 1
fi
FILE_PATH="$PWD/$GAME"
URL="file://${FILE_PATH// /%20}#stall"
# its own browser profile, so scores, settings and recordings stay together and the sound setting applies
PROFILE="$HOME/Library/Application Support/RavanGame"
for BROWSER in "Google Chrome" "Microsoft Edge" "Brave Browser" "Chromium"; do
  if open -Ra "$BROWSER" >/dev/null 2>&1; then
    open -na "$BROWSER" --args --app="$URL" --start-fullscreen --autoplay-policy=no-user-gesture-required \
      --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check
    exit 0
  fi
done
# no Chrome-style browser installed: open it in the default browser (tap once to start the sound)
open "$FILE_PATH"
