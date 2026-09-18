#!/data/data/com.termux/files/usr/bin/bash
# Noyon.py installer — by Noyon
# WPS PIN / Pixie Dust Attack Tool

echo "═══════════════════════════════════════════"
echo "       Noyon.py Installer"
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

echo "[*] Installing Python packages…"
pip install --upgrade pip
pip install pyfiglet wcwidth

echo "[*] Cloning Noyon repository…"
cd ~
if [ -d "Noyon-WPS" ]; then
    cd Noyon-WPS && git pull
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
echo "To run Noyon.py:"
echo "  tsu"
echo "  python ~/Noyon-WPS/noyon.py -i wlan0 -K"
echo ""
