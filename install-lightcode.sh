#!/bin/sh
# lightcode installer: sets up isolated dirs, wrapper, binary copy, bridge.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.config/lightcode-root/opencode" \
         "$HOME/.local/share/lightcode" "$HOME/.cache/lightcode" \
         "$HOME/.local/bin"
cp "$SRC/config/opencode/opencode.jsonc" "$HOME/.config/lightcode-root/opencode/opencode.jsonc"
cp "$SRC/bridge/telegram_bridge.py" "$HOME/.config/lightcode-root/telegram_bridge.py"
cp "$SRC/bridge/serve.sh" "$HOME/.config/lightcode-root/serve.sh"
chmod +x "$HOME/.config/lightcode-root/serve.sh"
if [ ! -f "$HOME/.local/bin/lightcode-bin.exe" ]; then
  echo "installing lightcode binary (~140MB)..."
  cp "$SRC/../lightcode/packages/opencode/dist/opencode-darwin-arm64/bin/opencode" "$HOME/.local/bin/lightcode-bin.exe" 2>/dev/null || cp ./packages/opencode/dist/opencode-darwin-arm64/bin/opencode "$HOME/.local/bin/lightcode-bin.exe"
fi
cp "$SRC/bin/lightcode" "$HOME/.local/bin/lightcode"
chmod +x "$HOME/.local/bin/lightcode"
echo "done. add your BotFather token to ~/.config/lightcode-root/telegram.token"
echo "then: lightcode"
