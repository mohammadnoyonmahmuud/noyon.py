<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=52&duration=2800&pause=700&color=FF0033&center=true&vCenter=true&width=900&height=100&lines=NOYON.PY;WPS+PIN+ATTACK+TOOL;PIXIE+DUST+EXPLOIT" alt="NOYON.PY" />

<br>

### 🔥 **WPS PIN / PIXIE DUST ATTACK TOOL FOR TERMUX** 🔥

<br>

[![Python](https://img.shields.io/badge/PYTHON-3.6%2B-FF0033?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Termux](https://img.shields.io/badge/PLATFORM-TERMUX-000000?style=for-the-badge&logo=android&logoColor=FF0033)](https://termux.com)
[![License](https://img.shields.io/badge/LICENSE-MIT-FF0033?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/AUTHOR-MOHAMMAD%20NOYON-FF0033?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mohammadnoyonmahmuud)

<br>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF0033&height=3&section=header" width="100%"/>

<br>

**AUTHOR:** [MOHAMMAD NOYON](https://github.com/mohammadnoyonmahmuud)

**BASED ON:** ONESHOTPIN BY ROFL0R & DRYGDRYG

<br>

</div>

---

<br>

## ⚡ **FEATURES**

<br>

<table>
<tr>
<td width="50%">

- 🎯 **WPS PIN GENERATION** — 24/28/32-bit, D-Link, ASUS, Airocon
- 🧚 **PIXIE DUST ATTACK** — Fast offline WPS PIN recovery
- 🔨 **SMART BRUTEFORCE** — Sequential half-sweep algorithm

</td>
<td width="50%">

- 📡 **BUILT-IN SCANNER** — Detects WPS-enabled networks
- 💾 **AUTO SAVE** — Credentials saved to TXT / CSV / JSON
- 📱 **TERMUX READY** — Full Android support

</td>
</tr>
</table>

<br>

---

<br>

## 📋 **REQUIREMENTS**

<br>

| COMPONENT | DESCRIPTION |
|:----------|:------------|
| 🖥️ **ANDROID** | Rooted device (Magisk / SuperSU) |
| 📟 **TERMUX** | [DOWNLOAD FROM F-DROID](https://f-droid.org/repo/com.termux_1022.apk) |
| 📦 **BUSYBOX** | [DOWNLOAD BUSYBOX APK](https://github.com/mohammadnoyonmahmuud/noyon.py/raw/main/BusyBox%20Free_64.apk) |

<br>

> ⚠️ **ROOT ACCESS IS REQUIRED. WITHOUT IT, WPS ATTACK WILL NOT WORK.**

<br>

---

<br>

## 🚀 **INSTALLATION — FIRST TIME SETUP**

<br>

### **STEP 1** — STORAGE

```bash
termux-setup-storage
```

> Tap **ALLOW** when the popup appears.

<br>

### **STEP 2** — UPDATE

```bash
pkg update -y && pkg upgrade -y
```

<br>

### **STEP 3** — TSU

```bash
pkg install tsu -y
```

<br>

### **STEP 4** — GIT & PYTHON

```bash
pkg install git python root-repo -y
```

<br>

### **STEP 5** — PACKAGES

```bash
pkg install wpa-supplicant pixiewps iw openssl -y
```

<br>

### **STEP 6** — PIP INSTALL

```bash
pip install pyfiglet wcwidth
```

<br>

### **STEP 7** — CLONE

```bash
cd ~
git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git
```

<br>

### **STEP 8** — ENTER FOLDER

```bash
cd ~/noyon.py
```

<br>

---

<br>

### ⚡ **ONE-LINE FULL INSTALL**

<br>

Install everything with a single command:

```bash
termux-setup-storage && pkg update -y && pkg upgrade -y && pkg install tsu git python root-repo wpa-supplicant pixiewps iw openssl -y && pip install pyfiglet wcwidth && cd ~ && git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git && cd ~/noyon.py && echo "✅ INSTALLATION COMPLETE"
```

<br>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF0033&height=3&section=header" width="100%"/>

<br>

## ▶️ **RUN COMMAND**

<br>

> 🔥 **FOLLOW THESE STEPS EVERY TIME YOU WANT TO RUN NOYON.PY**

<br>

### **STEP 1** — OPEN TERMUX

Just open the Termux app on your device.

<br>

### **STEP 2** — GET ROOT

```bash
tsu
```

> Tap **GRANT** on the Magisk popup.

<br>

### **STEP 3** — GO TO FOLDER

```bash
cd /data/data/com.termux/files/home/noyon.py
```

<br>

### **STEP 4** — CHECK INTERFACE

```bash
iw dev
```

> Look for `Interface wlan0` or `Interface wlan1` and remember it.

<br>

---

<br>

### 🎯 **FINAL ENTER**

<br>

### **STEP 1** — ENTER ROOT

```bash
tsu
```

<br>

### **STEP 2** — ENTER FOLDER

```bash
cd /data/data/com.termux/files/home/noyon.py
```

<br>

### **STEP 3** — ATTACK

<br>

**IF YOUR INTERFACE IS `wlan0`:**

```bash
python noyon.py -i wlan0 -K
```

<br>

**IF YOUR INTERFACE IS `wlan1`:**

```bash
python noyon.py -i wlan1 -K
```

<br>

**ATTACK A SPECIFIC TARGET BY BSSID:**

```bash
python noyon.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K
```

<br>

---

<br>

### 🎯 **QUICK RUN — 3 COMMANDS**

<br>

```bash
tsu
```

<br>

```bash
cd /data/data/com.termux/files/home/noyon.py
```

<br>

```bash
python noyon.py -i wlan0 -K
```

<br>

---

<br>

### 🎯 **ALL-IN-ONE COMMAND**

<br>

Run everything with **one command**:

```bash
tsu -c "cd /data/data/com.termux/files/home/noyon.py && python noyon.py -i wlan0 -K"
```

<br>

**FOR `wlan1`:**

```bash
tsu -c "cd /data/data/com.termux/files/home/noyon.py && python noyon.py -i wlan1 -K"
```

<br>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF0033&height=3&section=header" width="100%"/>

<br>

## ⚡ **SHORTCUT SETUP** (OPTIONAL)

<br>

Tired of typing long commands? Create a custom alias.

<br>

**RUN THIS ONCE IN TERMUX:**

```bash
echo "alias noyon='cd ~/noyon.py && sudo python noyon.py'" >> ~/.bashrc
source ~/.bashrc
```

<br>

**NOW JUST TYPE:**

<br>

**FOR `wlan0`:**

```bash
noyon -i wlan0 -K
```

<br>

**FOR `wlan1`:**

```bash
noyon -i wlan1 -K
```

<br>

---

<br>

## 📖 **USAGE OPTIONS**

<br>

| FLAG | DESCRIPTION |
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

<br>

---

<br>

## 🛠️ **TROUBLESHOOTING**

<br>

| ❌ PROBLEM | ✅ SOLUTION |
|:-----------|:------------|
| `wpa_supplicant: not found` | `pkg install -y wpa-supplicant` |
| `Unable to up interface` | Run `iw dev` and use correct name |
| `No WPS networks found` | Enable WiFi and move closer to router |
| `RF-kill error` | `sudo rfkill unblock wifi` |
| `Device or resource busy (-16)` | Turn off WiFi, add `--iface-down` |
| `pyfiglet missing` | `pip install pyfiglet` |
| Root popup not showing | Magisk → Superuser → Termux → Enable |

<br>

---

<br>

## ⚠️ **DISCLAIMER**

<br>

> **THIS TOOL IS FOR EDUCATIONAL PURPOSES AND AUTHORIZED SECURITY TESTING ONLY.**
>
> Unauthorized access to networks is **ILLEGAL**. Use only on your own networks or with explicit written permission from the owner.
>
> The author (**MOHAMMAD NOYON**) is not responsible for any misuse or damage.

<br>

---

<br>

## 🙏 **ACKNOWLEDGEMENTS**

<br>

- [ROFL0R](https://github.com/rofl0r) — Original OneShot
- [DRYGDRYG](https://github.com/drygdryg) — OneShotPin Mod
- [TERMUX](https://termux.com) — Android Terminal Emulator

<br>

---

<br>

## 📜 **LICENSE**

<br>

This project is licensed under the **MIT LICENSE** — see the [LICENSE](LICENSE) file for details.

<br>

---

<br>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=FF0033&height=140&section=footer" width="100%"/>

<br>

### ⭐ **STAR THIS REPO IF YOU FOUND IT USEFUL!** ⭐

<br>

**MADE WITH ❤️ BY [MOHAMMAD NOYON](https://github.com/mohammadnoyonmahmuud)**

<br>

</div>
