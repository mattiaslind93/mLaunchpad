#!/bin/bash
#
# Build a native macOS .app bundle for HomeLaunchPad.
#
# The bundle is a thin wrapper: it runs this repo's .venv Python on main.py, so
# the app always launches the latest code. The icon is generated from
# icons/homelaunchpad_icon.png (the Milford logo on a squircle).
#
# Usage:
#   ./build_macos_app.sh            # install to /Applications
#   ./build_macos_app.sh ~/Applications   # install elsewhere
#
set -e

REPO="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="HomeLaunchPad"
MASTER="$REPO/icons/homelaunchpad_icon.png"
DEST="${1:-/Applications}"
APP="$DEST/$APP_NAME.app"

if [ ! -f "$MASTER" ]; then
    echo "Saknar ikon: $MASTER" >&2
    exit 1
fi

# --- 1. Build AppIcon.icns from the 1024px master ---
echo "Bygger ikon ..."
ICONSET="$(mktemp -d)/AppIcon.iconset"
mkdir -p "$ICONSET"
for sz in 16 32 128 256 512; do
    sips -z "$sz" "$sz" "$MASTER" --out "$ICONSET/icon_${sz}x${sz}.png" >/dev/null
    sips -z "$((sz * 2))" "$((sz * 2))" "$MASTER" --out "$ICONSET/icon_${sz}x${sz}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$REPO/icons/AppIcon.icns"

# --- 2. Assemble the .app bundle ---
echo "Bygger $APP ..."
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$REPO/icons/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>            <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>     <string>$APP_NAME</string>
    <key>CFBundleExecutable</key>      <string>$APP_NAME</string>
    <key>CFBundleIconFile</key>        <string>AppIcon</string>
    <key>CFBundleIdentifier</key>      <string>se.mlind.homelaunchpad</string>
    <key>CFBundlePackageType</key>     <string>APPL</string>
    <key>CFBundleShortVersionString</key> <string>1.0</string>
    <key>CFBundleVersion</key>         <string>1</string>
    <key>CFBundleInfoDictionaryVersion</key> <string>6.0</string>
    <key>LSMinimumSystemVersion</key>  <string>11.0</string>
    <key>NSHighResolutionCapable</key> <true/>
</dict>
</plist>
PLIST

# Launcher executable: baked-in repo path + literal bootstrap logic.
{
    echo '#!/bin/bash'
    echo "REPO=\"$REPO\""
    cat <<'LAUNCH'
cd "$REPO" || exit 1

# Ensure the virtual environment exists (first launch / fresh clone).
if [ ! -x ".venv/bin/python" ]; then
    PYTHON_BIN="python3"
    for cand in \
        /opt/homebrew/bin/python3.13 \
        /opt/homebrew/bin/python3.12 \
        /opt/homebrew/bin/python3.11 \
        /opt/homebrew/bin/python3 \
        /usr/local/bin/python3 \
        python3; do
        if command -v "$cand" >/dev/null 2>&1; then PYTHON_BIN="$cand"; break; fi
    done
    "$PYTHON_BIN" -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/python main.py
LAUNCH
} > "$APP/Contents/MacOS/$APP_NAME"
chmod +x "$APP/Contents/MacOS/$APP_NAME"

# Refresh Finder/LaunchServices icon cache for this bundle.
touch "$APP"

echo "Klart: $APP"
