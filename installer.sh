#!/data/data/com.termux/files/usr/bin/bash
# Noyon.py installer — by Noyon
# ULTRA ENGINE Edition — WPS PIN / Pixie Dust / MAC Rotation

echo "═══════════════════════════════════════════"
echo "       Noyon.py Installer"
echo "       ULTRA ENGINE Edition"
echo "       Author: Noyon"
echo "═══════════════════════════════════════════"
echo ""

echo "[*] Requesting storage permission…"
termux-setup-storage

echo "[*] Updating packages…"
pkg update -y && pkg upgrade -y

echo "[*] Installing tsu (root access)…"
pkg install -y tsu

echo "[*] Installing root-repo…"
pkg install -y root-repo

echo "[*] Installing main dependencies…"
pkg install -y git python wpa-supplicant pixiewps iw openssl

echo "[*] Installing network tools (MAC rotation support)…"
pkg install -y iproute2 termux-api

echo "[*] Installing Python packages…"
pip install --upgrade pip
pip install pyfiglet wcwidth

echo "[*] Cloning Noyon repository…"
cd ~
if [ -d "Noyon-WPS" ]; then
    cd Noyon-WPS
    git pull
else
    git clone https://github.com/mohammadnoyonmahmuud/Noyon-WPS
    cd Noyon-WPS
fi

chmod +x noyon.py

echo ""
echo "═══════════════════════════════════════════"
echo "  [✔] Installation Complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "Features:"
echo "  • Multi-Vendor WPS attack (100+ vendors)"
echo "  • Pixie Dust attack"
echo "  • Smart Bruteforce"
echo "  • Auto MAC Rotation (bypass WPS lock)"
echo "  • External Engine Architecture"
echo ""
echo "To run noyon.py:"
echo "  tsu"
echo "  cd ~/Noyon-WPS"
echo "  python noyon.py -i wlan0 -K -w"
echo ""
echo "Available engines:"
echo "  -K     Pixie Dust"
echo "  -M     Multi-PIN"
echo "  -B     Bruteforce"
echo "  -p     Single PIN"
echo "  --pbc  Push Button"
echo ""

chmod +x noyon.py

echo ""
echo "═══════════════════════════════════════════"
echo "  [✔] Installation Complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "To run Noyon.py:"
echo "  tsu"
echo "  python ~/Noyon-WPS/noyon.py -i wlan0 -K"
echo ""
