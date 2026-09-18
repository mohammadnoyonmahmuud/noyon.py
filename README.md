<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&size=40&duration=3000&pause=800&color=00FFAA&center=true&vCenter=true&width=800&lines=Noyon.py;WPS+PIN+%2F+Pixie+Dust+Attack+Tool" alt="Noyon.py" />

### 🔐 **WPS PIN / Pixie Dust Attack Tool for Termux**

[![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Termux](https://img.shields.io/badge/Platform-Termux-000000?style=for-the-badge&logo=android&logoColor=00FFAA)](https://termux.com)
[![License](https://img.shields.io/badge/License-MIT-00FFAA?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Noyon-FF0055?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mohammadnoyonmahmuud)

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=2,12,24&height=3&section=header" width="100%"/>

**Author:** [Noyon](https://github.com/mohammadnoyonmahmuud) · **Based on:** OneShotPin by rofl0r & drygdryg

</div>

---

## ⚡ **FEATURES**

<table>
<tr>
<td width="50%">

- 🎯 **WPS PIN Generation** — 24/28/32-bit, D-Link, ASUS, Airocon
- 🧚 **Pixie Dust Attack** — Fast offline WPS PIN recovery
- 🔨 **Smart Bruteforce** — Sequential half-sweep algorithm

</td>
<td width="50%">

- 📡 **Built-in Scanner** — Detects WPS-enabled networks
- 💾 **Auto Save** — Credentials saved to TXT / CSV / JSON
- 📱 **Termux Ready** — Full Android support

</td>
</tr>
</table>

---

## 📋 **REQUIREMENTS**

| Component | Description |
|:----------|:------------|
| 🖥️ **Android** | Rooted device (Magisk / SuperSU) |
| 📟 **Termux** | [Download from F-Droid](https://f-droid.org/repo/com.termux_1022.apk) |
| 📦 **BusyBox** | [Download BusyBox Free_64.apk](https://github.com/mohammadnoyonmahmuud/noyon.py/raw/main/BusyBox%20Free_64.apk) |

> ⚠️ **Root access is REQUIRED. Without it, WPS attack will NOT work.**

---

## 🚀 **INSTALLATION** — First Time Setup

### **STEP 1** — Storage Permission

```bash
termux-setup-storage
```

> Tap **ALLOW** when the popup appears.

---

### **STEP 2** — Update & Upgrade

```bash
pkg update -y && pkg upgrade -y
```

---

### **STEP 3** — Install TSU (Root Access)

```bash
pkg install tsu -y
```

---

### **STEP 4** — Install Git, Python & Root-Repo

```bash
pkg install git python root-repo -y
```

---

### **STEP 5** — Install Required Packages

```bash
pkg install wpa-supplicant pixiewps iw openssl -y
```

---

### **STEP 6** — Install Python Packages

```bash
pip install pyfiglet wcwidth
```

---

### **STEP 7** — Clone Repository

```bash
cd ~
git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git
```

---

### **STEP 8** — Enter Folder

```bash
cd ~/noyon.py
```

---

### ⚡ **ONE-LINE FULL INSTALL**

Install everything with a single command:

```bash
termux-setup-storage && pkg update -y && pkg upgrade -y && pkg install tsu git python root-repo wpa-supplicant pixiewps iw openssl -y && pip install pyfiglet wcwidth && cd ~ && git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git && cd ~/noyon.py && echo "✅ INSTALLATION COMPLETE"
```

---

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=2,12,24&height=3&section=header" width="100%"/>

## ▶️ **RUN COMMAND**

> 🟢 **Follow these steps EVERY TIME you want to run Noyon.py**

<br>

### **STEP 1** — Open Termux

Just open the Termux app on your device.

---

### **STEP 2** — Get Root Access

```bash
tsu
```

> Tap **GRANT** on the Magisk popup.

---

### **STEP 3** — Navigate to Folder

```bash
cd /data/data/com.termux/files/home/noyon.py
```

---

### **STEP 4** — Check WiFi Interface

```bash
iw dev
```

> Look for `Interface wlan0` or `Interface wlan1` and remember it.

---

### **STEP 5** — Start the Attack

**If your interface is `wlan0`:**

```bash
python noyon.py -i wlan0 -K
```

**If your interface is `wlan1`:**

```bash
python noyon.py -i wlan1 -K
```

**Attack a specific target by BSSID:**

```bash
python noyon.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K
```

---

### 🎯 **QUICK RUN — 3 COMMANDS**

```bash
tsu
```

```bash
cd /data/data/com.termux/files/home/noyon.py
```

```bash
python noyon.py -i wlan0 -K
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=2,12,24&height=3&section=header" width="100%"/>

---

## ⚡ **SHORTCUT SETUP** (Optional)

Tired of typing long commands? Create a custom alias.

**Run this once in Termux:**

```bash
echo "alias noyon='cd ~/noyon.py && sudo python noyon.py'" >> ~/.bashrc
source ~/.bashrc
```

**Now just type:**

```bash
noyon -i wlan0 -K
```

---

## 📖 **USAGE OPTIONS**

| Flag | Description |
|:-----|:------------|
| `-i` | Interface name (e.g. `wlan0`) |
| `-b` | Target BSSID (MAC address) |
| `-p` | Specific WPS PIN |
| `-K` | Pixie Dust Attack |
| `-B` | Online Bruteforce |
| `-F` | Pixie Dust with `--force` |
| `-X` | Show Pixiewps Command |
| `-w` | Save Credentials to File |
| `--pbc` | Push Button Connection |
| `--iface-down` | Down Interface When Done |
| `-v` | Verbose Output |

---

## 🛠️ **TROUBLESHOOTING**

| ❌ Problem | ✅ Solution |
|:-----------|:------------|
| `wpa_supplicant: not found` | `pkg install -y wpa-supplicant` |
| `Unable to up interface` | Run `iw dev` and use correct name |
| `No WPS networks found` | Enable WiFi and move closer to router |
| `RF-kill error` | `sudo rfkill unblock wifi` |
| `Device or resource busy (-16)` | Turn off WiFi, add `--iface-down` |
| `pyfiglet missing` | `pip install pyfiglet` |
| Root popup not showing | Magisk → Superuser → Termux → Enable |

---

## ⚠️ **DISCLAIMER**

> **THIS TOOL IS FOR EDUCATIONAL PURPOSES AND AUTHORIZED SECURITY TESTING ONLY.**
>
> Unauthorized access to networks is **ILLEGAL**. Use only on your own networks or with explicit written permission from the owner.
>
> The author (**Noyon**) is not responsible for any misuse or damage.

---

## 🙏 **ACKNOWLEDGEMENTS**

- [rofl0r](https://github.com/rofl0r) — Original OneShot
- [drygdryg](https://github.com/drygdryg) — OneShotPin Mod
- [Termux](https://termux.com) — Android Terminal Emulator

---

## 📜 **LICENSE**

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,12,24&height=120&section=footer" width="100%"/>

### ⭐ **Star this repo if you found it useful!**

**Made with ❤️ by [Noyon](https://github.com/mohammadnoyonmahmuud)**

</div>
