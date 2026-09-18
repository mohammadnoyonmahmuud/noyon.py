<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=48&duration=2800&pause=700&color=FF0033&center=true&vCenter=true&width=900&height=100&lines=NOYON.PY;WPS+PIN+ATTACK+TOOL;PIXIE+DUST+EXPLOIT" alt="NOYON.PY" />

<br>

### ⚡ WPS PIN / PIXIE DUST ATTACK TOOL FOR TERMUX ⚡

<br>

[![Python](https://img.shields.io/badge/PYTHON-3.6%2B-FF0033?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Termux](https://img.shields.io/badge/PLATFORM-TERMUX-000000?style=for-the-badge&logo=android&logoColor=FF0033)](https://termux.com)
[![License](https://img.shields.io/badge/LICENSE-MIT-FF0033?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/AUTHOR-MOHAMMAD%20NOYON-FF0033?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mohammadnoyonmahmuud)

<br>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF0033&height=3&section=header" width="100%"/>

<br>

Author: [MOHAMMAD NOYON](https://github.com/mohammadnoyonmahmuud)

Based on: OneShotPin by rofl0r & drygdryg

<br>

</div>

---

<br>

## 🚀 Features

<br>

<table>
<tr>
<td width="50%">

- 🎯 WPS PIN Generation — 24/28/32-bit, D-Link, ASUS, Airocon
- 🧚 Pixie Dust Attack — Fast offline WPS PIN recovery
- 🔨 Smart Bruteforce — Sequential half-sweep algorithm

</td>
<td width="50%">

- 📡 Built-in Scanner — Detects WPS-enabled networks
- 💾 Auto Save — Credentials saved to TXT / CSV / JSON
- 📱 Termux Ready — Full Android support

</td>
</tr>
</table>

<br>

---

<br>

## 📋 Requirements

<br>

| COMPONENT | DESCRIPTION |
|:----------|:------------|
| 📱 Android | Rooted device (Magisk / SuperSU) |
| 💻 Termux | [DOWNLOAD FROM F-DROID](https://f-droid.org/repo/com.termux_1022.apk) |
| 📦 BusyBox | [DOWNLOAD BUSYBOX APK](https://github.com/mohammadnoyonmahmuud/noyon.py/raw/main/BusyBox%20Free_64.apk) |

<br>

> ⚠️ Root access is required. Without it, WPS attack will not work.

<br>

---

<br>

### ⚡ SIMPLE METHOD Installation

<br>

Install everything with a single command:

```bash
termux-setup-storage && pkg update -y && pkg upgrade -y && pkg install tsu git python root-repo wpa-supplicant pixiewps iw openssl -y && pip install pyfiglet wcwidth && cd ~ && git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git && cd ~/noyon.py && echo "INSTALLATION COMPLETE"
```

<br>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF0033&height=3&section=header" width="100%"/>

<br>

## 🛠️ Installation — First Time Setup

<br>

### 😈 STEP 1 — STORAGE

```bash
termux-setup-storage
```

> Tap ALLOW when the popup appears.

<br>

### 😈 STEP 2 — UPDATE

```bash
pkg update -y && pkg upgrade -y
```

<br>

### 😈 STEP 3 — TSU

```bash
pkg install tsu -y
```

<br>

### 😈 STEP 4 — GIT & PYTHON

```bash
pkg install git python root-repo -y
```

<br>

### 😈 STEP 5 — PACKAGES

```bash
pkg install wpa-supplicant pixiewps iw openssl -y
```

<br>

### 😈 STEP 6 — PIP INSTALL

```bash
pip install pyfiglet wcwidth
```

<br>

### 😈 STEP 7 — CLONE

```bash
cd ~
git clone https://github.com/mohammadnoyonmahmuud/noyon.py.git
```

<br>

### 😈 STEP 8 — ENTER FOLDER

```bash
cd ~/noyon.py
```

<br>

### 😈 STEP 9 — GAVE POWER

```bash
tsu
```

> Tap GRANT on the Magisk popup.

<br>

### 😈 STEP 10 — RUN COMMAND

<br>

If your interface is `wlan0`:

```bash
python noyon.py -i wlan0 -K
```

<br>

If your interface is `wlan1`:

```bash
python noyon.py -i wlan1 -K
```

<br>

---

<br>



## ⚡✅✅ **SHORTCUT SETUP  (Optional)**

<br>

আপনি এই সেটাপ করলে পরবর্তীতে TERMUX এ যখন ঢুকবেন । কোন এক্সট্রা কামান্ড দেওয়া লাগবে না শুধু এইটা এন্টার করে দিবেন। run হয়ে যাবে।
<br>

------------------------------------------------------------------------------
<br>

Once you complete the setup, the next time you open Termux, you won't need to enter any commands. Just press Enter, and it will run automatically.

<br>

Run this once in Termux:

```bash
echo "alias noyon='cd ~/noyon.py && sudo python noyon.py'" >> ~/.bashrc
source ~/.bashrc
```

<br>

Now just type:

<br>

For `wlan0`:

```bash
noyon -i wlan0 -K
```

<br>

For `wlan1`:

```bash
noyon -i wlan1 -K
```

<br>

---

<br>

## 📖 Usage Options

<br>


## 🎯 Manually Method V2

<br>

> Follow these steps every time you want to run Noyon.py

<br>

### 😈 STEP 1 — OPEN TERMUX

Just open the Termux app on your device.

<br>

### 😈 STEP 2 — GET ROOT

```bash
tsu
```

> Tap GRANT on the Magisk popup.

<br>

### 😈 STEP 3 — GO TO FOLDER

```bash
cd /data/data/com.termux/files/home/noyon.py
```

<br>

### 😈 STEP 4 — CHECK INTERFACE

```bash
iw dev
```

### 😈 STEP 5 —  NOW RUN

<br>

If your interface is `wlan0`:

```bash
python noyon.py -i wlan0 -K
```

<br>

If your interface is `wlan1`:

```bash
python noyon.py -i wlan1 -K
```

<br>


> Look for `Interface wlan0` or `Interface wlan1` and remember it.

<br>

---

<br>

## 🎯 Manually Method V3

<br>

### 😈 STEP 1 — ENTER ROOT

```bash
tsu
```

<br>

### 😈 STEP 2 — ENTER FOLDER

```bash
cd /data/data/com.termux/files/home/noyon.py
```

<br>

### 😈 STEP 3 — ATTACK

<br>

If your interface is `wlan0`:

```bash
python noyon.py -i wlan0 -K
```

<br>

If your interface is `wlan1`:

```bash
python noyon.py -i wlan1 -K
```

<br>

Attack a specific target by BSSID:

```bash
python noyon.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K
```

<br>

---

<br>

### ⚡ QUICK RUN — 3 COMMANDS

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

### ⚡ ALL-IN-ONE COMMAND

<br>

Run everything with one command:

```bash
tsu -c "cd /data/data/com.termux/files/home/noyon.py && python noyon.py -i wlan0 -K"
```

<br>

For `wlan1`:

```bash
tsu -c "cd /data/data/com.termux/files/home/noyon.py && python noyon.py -i wlan1 -K"
```

<br>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF0033&height=3&section=header" width="100%"/>

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

## 🔧 Troubleshooting

<br>

| PROBLEM | SOLUTION |
|:--------|:---------|
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

## ⚠️ Disclaimer

<br>

> This tool is for educational purposes and authorized security testing only.
>
> Unauthorized access to networks is illegal. Use only on your own networks or with explicit written permission from the owner.
>
> The author (MOHAMMAD NOYON) is not responsible for any misuse or damage.

<br>

---

<br>

## 🏆 Acknowledgements

<br>

- 🥇 [rofl0r](https://github.com/rofl0r) — Original OneShot
- 🥈 [drygdryg](https://github.com/drygdryg) — OneShotPin Mod
- 🥉 [Termux](https://termux.com) — Android Terminal Emulator

<br>

---

<br>

## 📜 License

<br>

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

<br>

---
<br>


### ⭐ STAR THIS REPO IF YOU FOUND IT USEFUL ⭐

<br>

💖 MADE WITH LOVE BY [MOHAMMAD NOYON](https://github.com/mohammadnoyonmahmuud) 💖

<br>

</div>
