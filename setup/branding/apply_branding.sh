#!/usr/bin/env bash
# Optional cosmetic layer: failure here does not affect the training pipeline.
set -u
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WALLPAPER="$PROJECT_ROOT/setup/branding/wallpaper.png"
sudo hostnamectl set-hostname cyberlab || echo "Could not set hostname; continue without branding."
if command -v gsettings >/dev/null 2>&1 && [ -f "$WALLPAPER" ]; then
  gsettings set org.gnome.desktop.background picture-uri "file://$WALLPAPER" || true
fi
mkdir -p "$HOME/Desktop"
cat > "$HOME/Desktop/CyberLab-Dashboard.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=CyberLab Dashboard
Comment=Open the local CyberLab training dashboard
Exec=xdg-open http://localhost:5000
Icon=utilities-terminal
Terminal=false
Categories=Education;Security;
EOF
chmod +x "$HOME/Desktop/CyberLab-Dashboard.desktop"
echo "Optional branding applied. Start dashboard first, then open the desktop launcher."
