<div align="center">

# 🔐 noyon.py

### WPS PIN / Pixie Dust Attack Tool for Termux

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Termux](https://img.shields.io/badge/Platform-Termux-black?style=flat-square&logo=android)](https://termux.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Noyon-red?style=flat-square)](https://github.com/mohammadnoyonmahmuud)

**Author:** [Noyon](https://github.com/mohammadnoyonmahmuud)  
**Based on:** OneShotPin by rofl0r & drygdryg

</div>

---

## ⚡ Features

- 🎯 **WPS PIN Generation** — 24/28/32-bit, D-Link, ASUS, Airocon
- 🧚 **Pixie Dust Attack** — Fast offline WPS PIN recovery
- 🔨 **Smart Bruteforce** — Sequential half-sweep algorithm
- 📡 **Built-in Scanner** — Detects WPS-enabled networks
- 💾 **Auto Save** — Credentials saved to TXT / CSV / JSON
- 📱 **Termux Ready** — Full Android support

---

## 📋 Requirements

- **Android** with **Root** access (Magisk / SuperSU)
- **Termux** app → [Download from F-Droid](https://f-droid.org/repo/com.termux_1022.apk)
- **BusyBox** → [Download BusyBox Free_64.apk](https://github.com/mohammadnoyonmahmuud/noyon.py/raw/main/BusyBox%20Free_64.apk)

> ⚠️ **Root access ছাড়া WPS attack কাজ করবে না।**

---

## 🚀 Installation (First Time Setup)

### 📌 STEP 1 — Storage Permission

```bash
termux-setup-storage
```

> 📱 Popup আসলে **Allow** ট্যাপ করুন।

---

### 📌 STEP 2 — Update & Upgrade

```bash
pkg update -y && pkg upgrade -y
```

---

### 📌 STEP 3 — Install tsu (Root access)

```bash
pkg install tsu -y
```

---

### 📌 STEP 4 — Install Git, Python & Root-repo

```bash
pkg install git python root-repo -y
```

---

### 📌 STEP 5 — Install Required Packages

```bash
pkg install wpa-supplicant pixiewps iw openssl -y
```

---

### 📌 STEP 6 — Install Python Packages

```bash
pip install pyfiglet wcwidth
```

---

### 📌 STEP 7 — Clone Repository

```bash
cd ~
git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git
```

---

### 📌 STEP 8 — Enter Folder

```bash
cd ~/noyon.py
```

---

### ⚡ One-Line Full Install (Copy-Paste)

সব একসাথে করতে চাইলে নিচের কমান্ডটি ব্যবহার করুন:

```bash
termux-setup-storage && pkg update -y && pkg upgrade -y && pkg install tsu git python root-repo wpa-supplicant pixiewps iw openssl -y && pip install pyfiglet wcwidth && cd ~ && git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git && cd ~/noyon.py && echo "✅ Installation Complete!"
```

---

## ▶️ How to Run (প্রতিবার চালানোর নিয়ম)

### 🔹 Step 1 — Termux ওপেন করুন

### 🔹 Step 2 — Root নিন

```bash
tsu
```

> 📱 Magisk popup আসলে → **Grant** ট্যাপ করুন।

### 🔹 Step 3 — ফোল্ডারে যান

```bash
cd /data/data/com.termux/files/home/noyon.py
```

### 🔹 Step 4 — Interface নাম চেক করুন

```bash
iw dev
```

> `Interface wlan0` অথবা `Interface wlan1` — যেটা দেখবেন, সেটা মনে রাখুন।

### 🔹 Step 5 — Attack চালান

**যদি interface `wlan0` হয়:**

```bash
python noyon.py -i wlan0 -K
```

**যদি interface `wlan1` হয়:**

```bash
python noyon.py -i wlan1 -K
```

**নির্দিষ্ট BSSID দিয়ে:**

```bash
python noyon.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K
```

---

## ⚡ Shortcut Setup (Optional)

প্রতিবার লম্বা কমান্ড টাইপ করতে না চাইলে একটা alias বানিয়ে নিন:

**Termux এ (root ছাড়া):**

```bash
echo "alias noyon='cd ~/noyon.py && sudo python noyon.py'" >> ~/.bashrc
source ~/.bashrc
```

এখন শুধু লিখবেন:

```bash
noyon -i wlan0 -K
```

---

## 📖 Usage Options

| Flag | Description |
|:-----|:------------|
| `-i` | Interface name (e.g. wlan0) |
| `-b` | Target BSSID (MAC address) |
| `-p` | Specific WPS PIN |
| `-K` | Pixie Dust attack |
| `-B` | Online bruteforce |
| `-F` | Pixie Dust with --force |
| `-X` | Show Pixiewps command |
| `-w` | Save credentials to file |
| `--pbc` | Push button connection |
| `--iface-down` | Down interface when done |
| `-v` | Verbose output |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|:--------|:---------|
| `wpa_supplicant: not found` | `pkg install -y wpa-supplicant` |
| `Unable to up interface` | `iw dev` দিয়ে সঠিক নাম বের করুন |
| `No WPS networks found` | WiFi চালু করুন, রাউটারের কাছে যান |
| `RF-kill error` | `sudo rfkill unblock wifi` |
| `Device or resource busy (-16)` | WiFi বন্ধ করুন, `--iface-down` যোগ করুন |
| `pyfiglet missing` | `pip install pyfiglet` |
| Root popup আসছে না | Magisk → Superuser → Termux → Enable |

---

## ⚠️ Disclaimer

> **This tool is for educational purposes and authorized security testing only.**
>
> Unauthorized access to networks is **illegal**. Use only on your own networks or with explicit written permission from the owner.
>
> The author (**Noyon**) is not responsible for any misuse or damage.

---

## 🙏 Acknowledgements

- [rofl0r](https://github.com/rofl0r) — Original OneShot
- [drygdryg](https://github.com/drygdryg) — OneShotPin mod
- [Termux](https://termux.com) — Android Terminal Emulator

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file.

---

<div align="center">

**Made with ❤️ by [Noyon](https://github.com/mohammadnoyonmahmuud)**

⭐ Star this repo if you found it useful!

</div>
