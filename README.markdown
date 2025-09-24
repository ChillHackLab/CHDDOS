# CHDDOS - Advanced DoS/DDoS Attack Tool

**CHDDOS** is a powerful Python-based DoS/DDoS attack tool developed by ChillHackLab for authorized penetration testing and network stress testing. It supports a wide range of Layer 3 (Network), Layer 4 (Transport), and Layer 7 (Application) attack methods, featuring intelligent capabilities such as Nmap-based vulnerability scanning, proxy validation, IP spoofing, Tor integration for dark web targets, and real-time performance monitoring. Optimized for high impact, CHDDOS leverages efficient thread management and robust proxy handling to maximize attack effectiveness.

**⚠️ Legal Disclaimer**: CHDDOS is strictly for **authorized penetration testing only**. Unauthorized use for cyber attacks is illegal and violates global cybersecurity laws, including the Computer Fraud and Abuse Act (CFAA), EU Cybersecurity Act, and Hong Kong Computer Crimes Ordinance. Such actions carry severe legal consequences, including fines and imprisonment. Always obtain explicit written permission from the target system's owner before use. ChillHackLab is not responsible for any misuse or damages caused by this tool.

## Features
- **Multi-Layer Attack Support**: Over 35 attack methods across Layer 3, Layer 4, and Layer 7, targeting various services and protocols.
- **Intelligent Auto Mode**: Uses Nmap to scan for vulnerabilities and select optimal attack methods based on detected services.
- **Proxy Management**: Automatically validates and rotates proxies from files or URLs to distribute traffic and evade detection.
- **IP Spoofing**: Randomizes source IPs in Layer 4 packets and HTTP headers for anonymity.
- **Tor Integration**: Supports `.onion` targets for dark web testing using HTTP-based methods.
- **Real-Time Monitoring**: Tracks packets per second (PPS) and bytes per second (BPS) with dynamic method switching based on target response.
- **Multi-Method Attacks**: Executes multiple attack vectors simultaneously for maximum impact.
- **Optimized Performance**: Uses `ThreadPoolExecutor` for efficient thread management and robust error handling.
- **Protection Bypass**: Includes methods to bypass Cloudflare, DDoS-Guard, OVH, and other protections.

## Attack Methods
### Layer 7 (Application Layer) - HTTP/HTTPS
| Method       | Description                                      | Target              | Impact                     |
|--------------|--------------------------------------------------|---------------------|----------------------------|
| `http`       | High-frequency GET requests                     | Web servers         | High PPS                   |
| `post`       | POST requests with large payloads (1-10KB)      | Web servers         | High bandwidth             |
| `killer`     | Aggressive POST flood (5-50KB payloads)         | Web servers         | Maximum server overload    |
| `bomb`       | Massive POST payloads (5-100KB)                 | Web servers         | Extreme resource exhaustion|
| `stress`     | Oversized POST requests (10-100KB)              | Web servers         | Resource exhaustion        |
| `cfbuam`     | Cloudflare UAM bypass with forged cookies       | Cloudflare sites    | Protection bypass          |
| `cfb`        | Cloudflare bypass with cookie manipulation      | Cloudflare sites    | Protection bypass          |
| `dgb`        | DDoS-Guard bypass with custom headers           | Protected sites     | Protection bypass          |
| `avb`        | Arvancloud bypass with custom headers           | Protected sites     | Protection bypass          |
| `ovh`        | OVH protection bypass with custom headers       | OVH hosted sites    | Protection bypass          |
| `xmlrpc`     | WordPress XML-RPC exploitation                  | WordPress sites     | High amplification         |
| `slowloris`  | Slow HTTP DoS with partial requests             | Web servers         | Connection exhaustion      |
| `downloader` | Range header content streaming                  | Web servers         | Bandwidth exhaustion       |
| `apache`     | Apache Range header exploitation                | Apache servers      | Server crash               |
| `bypass`     | Generic WAF bypass with varied headers          | Protected sites     | Evasion                    |
| `stomp`      | CAPTCHA simulation bypass                       | Protected sites     | Protection bypass          |
| `rhex`       | Hex-encoded POST payloads                       | Web servers         | Obfuscation                |
| `dyn`        | Random subdomain attacks                        | CDN protected       | Cache bypass               |
| `gsb`        | Googlebot simulation                            | Search engines      | Legitimacy bypass          |
| `bot`        | Search engine bot simulation                    | Web servers         | Legitimacy bypass          |
| `cookie`     | Cookie header manipulation                      | Session-based sites | Session exhaustion         |
| `null`       | Null/empty User-Agent requests                  | Web servers         | Anomaly detection          |
| `head`       | HEAD method flood                               | Web servers         | Low bandwidth attack       |
| `pps`        | Maximum requests per second                     | Web servers         | Rate limiting              |
| `even`       | Continuous connection maintenance               | Web servers         | Connection pool exhaustion |

### Layer 4 (Transport Layer)
| Method       | Protocol | Description                           | Requirements       |
|--------------|----------|---------------------------------------|--------------------|
| `syn`        | TCP      | SYN flood with random source IPs     | Root privileges    |
| `udp`        | UDP      | UDP flood with variable payloads     | Root privileges    |
| `tcp`        | TCP      | TCP flag flood (ACK/FIN/RST/PSH)    | Root privileges    |
| `connection` | TCP      | Rapid TCP connection establishment   | Root privileges    |
| `vse`        | UDP      | Valve Source Engine query flood      | Game servers       |
| `ts3`        | UDP      | TeamSpeak 3 query flood              | VoIP servers       |
| `fivem`      | UDP      | FiveM server query flood             | Gaming servers     |
| `minecraft`  | UDP/TCP  | Minecraft server query flood         | Game servers       |
| `mcbot`      | TCP      | Minecraft bot simulation             | Game servers       |
| `mcpe`       | UDP      | Minecraft PE query flood             | Mobile game servers|
| `quic`       | UDP      | QUIC protocol flood                  | Modern web servers |

### Layer 3 (Network Layer) - Amplification Attacks
| Method  | Protocol | Amplification Factor | Requirements       |
|---------|----------|----------------------|--------------------|
| `dns`   | DNS      | 50-100x              | Reflector list     |
| `ntp`   | NTP      | 200-500x             | Reflector list     |
| `mem`   | Memcached| 50,000x              | Reflector list     |
| `ssdp`  | SSDP     | 30-70x               | Reflector list     |
| `snmp`  | SNMP     | 6-12x                | Reflector list     |
| `cldap` | CLDAP    | 50-70x               | Reflector list     |
| `char`  | CHARGEN  | 358x                 | Reflector list     |
| `ard`   | ARD      | 30-50x               | Reflector list     |
| `rdp`   | RDP      | 10-20x               | Reflector list     |

### Auto Mode
| Method | Description |
|--------|-------------|
| `auto` | Scans target with Nmap to detect vulnerabilities and select optimal attack methods based on services and ports. |

## Installation

### System Requirements
- **Operating System**: Linux (Kali Linux recommended), macOS, or Windows
- **Python**: 3.6 or higher
- **Root Access**: Required for Layer 3/4 attacks and Nmap scanning
- **Dependencies**: Nmap, Tor (for `.onion` targets), and Python libraries (see `requirements.txt`)
- **Network**: High-bandwidth connection (100Mbps+ recommended for maximum impact)

### Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ChillHackLab/CHDDOS.git
   cd CHDDOS
   ```

2. **Install Python Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install System Dependencies** (Linux):
   ```bash
   sudo apt update
   sudo apt install nmap python3-scapy
   ```

4. **Install Tor** (for `.onion` targets):
   ```bash
   sudo apt install tor
   sudo service tor start
   ```

5. **Windows Setup**:
   - Install Python 3.6+ from [python.org](https://python.org).
   - Install Npcap for Scapy (Layer 3/4 attacks) from [nmap.org/npcap](https://nmap.org/npcap).
   - Install dependencies: `pip install -r requirements.txt`.
   - Run as Administrator for root-privileged features.

6. **Prepare Proxy and Reflector Files**:
   - Create `proxies.txt` with proxies in `ip:port` format (e.g., `192.168.1.100:8080` or `socks5://10.0.0.1:1080`).
   - Create `reflectors.txt` for amplification attacks (e.g., `8.8.8.8:53` for DNS).

## Usage
### Basic Syntax
```bash
sudo python3 chddos.py -t <target> [options]
```

### Command Line Arguments
#### Core Parameters
| Flag            | Description                           | Default | Example                     |
|-----------------|-------------------------------|---------|-----------------------------|
| `-t, --target`  | Target IP/URL/domain          | Required| `-t example.com`            |
| `-p, --port`    | Target port                   | 80      | `-p 443`                   |
| `-d, --duration`| Attack duration (seconds)     | 60      | `-d 600`                   |
| `-m, --method`  | Attack method (see table)     | `http`  | `-m killer`                |

#### Performance Controls
| Flag            | Description                           | Default | Example                     |
|-----------------|---------------------------------------|---------|-----------------------------|
| `--threads`     | Number of concurrent threads          | 100     | `--threads 1000`           |
| `--rpc`         | Requests per connection (HTTP-based)  | 100     | `--rpc 500`                |

#### Network Evasion
| Flag            | Description                           | Default | Example                     |
|-----------------|---------------------------------------|---------|-----------------------------|
| `-s, --spoof`   | Enable IP spoofing                    | Disabled| `-s`                       |
| `--proxies`     | Proxy list file (ip:port)             | None    | `--proxies proxies.txt`    |
| `--proxy-url`   | URL to fetch proxies                  | None    | `--proxy-url https://api.proxyscrape.com` |
| `--multi`       | Comma-separated attack methods        | None    | `--multi http,killer,bomb` |

#### Advanced Features
| Flag            | Description                           | Default | Example                     |
|-----------------|---------------------------------------|---------|-----------------------------|
| `--reflectors`  | Reflector list for amplification       | None    | `--reflectors reflectors.txt` |
| `--persist`     | Auto-restart interval (minutes)       | None    | `--persist 30`             |

### Example Commands
#### High-Impact HTTP Attacks
```bash
# Aggressive POST flood with proxies and spoofing
sudo python3 chddos.py -t testphp.vulnweb.com -p 80 -m killer --threads 2000 --rpc 1000 -s --proxies proxies.txt

# Multi-vector Layer 7 attack
sudo python3 chddos.py -t testphp.vulnweb.com -p 80 -m auto --multi killer,bomb,cfbuam,xmlrpc --threads 1500 --rpc 500 -s --proxies proxies.txt

# Cloudflare bypass
sudo python3 chddos.py -t protected.com -p 80 -m cfbuam --threads 800 --rpc 300 --proxies proxies.txt
```

#### Layer 4 Network Attacks
```bash
# SYN flood (requires root)
sudo python3 chddos.py -t 192.168.1.1 -p 80 -m syn --threads 500 -s

# UDP flood
sudo python3 chddos.py -t target.com -p 53 -m udp --threads 1000 -s

# Connection exhaustion
sudo python3 chddos.py -t target.com -p 443 -m connection --threads 2000 -s
```

#### Amplification Attacks
```bash
# DNS amplification
sudo python3 chddos.py -t target.com -m dns --reflectors dns_servers.txt --threads 100 -s

# NTP amplification
sudo python3 chddos.py -t target.com -m ntp --reflectors ntp_servers.txt --threads 50 -s

# Memcached amplification (high amplification)
sudo python3 chddos.py -t target.com -m mem --reflectors memcached.txt --threads 20 -s
```

#### Dark Web Targets
```bash
# .onion target attack (requires Tor)
sudo python3 chddos.py -t example.onion -p 80 -m http --threads 200 --rpc 100
```

#### Persistent Attacks
```bash
# Auto-restart every 30 minutes
sudo python3 chddos.py -t target.com -p 80 -m auto --persist 30 --threads 1000 --proxies proxies.txt
```

### File Formats
#### Proxy File (`proxies.txt`)
```
192.168.1.100:8080
45.67.89.12:3128
socks5://10.0.0.1:1080
http://proxy.example.com:8000
```

#### Reflector File (`reflectors.txt`)
```
8.8.8.8:53          # DNS
pool.ntp.org:123    # NTP
239.255.255.250:1900 # SSDP
192.168.1.50:11211  # Memcached
```

## Performance Monitoring
CHDDOS provides real-time attack statistics:
```
Starting killer attack on target.com:80 for 300s with CHDDOS, 1000 threads, spoofing=enabled
[14:23:45 - INFO] PPS: 24567 | BPS: 1.23 GB/s | Success: 94.2%
[14:23:46 - INFO] PPS: 27891 | BPS: 1.45 GB/s | Success: 95.1%
[14:23:47 - INFO] Method killer effective, maintaining attack
[14:23:48 - INFO] PPS: 31245 | BPS: 1.67 GB/s | Success: 96.3%
```

- **Dynamic Switching**: Automatically switches methods if HTTP status codes (e.g., 403, 429) or low latency (<100ms) indicate blocking.
- **Metrics**: Tracks PPS, BPS, and success rate, resetting counters every second for accurate monitoring.

## System Integration
### Nmap Integration
- **Purpose**: Used in `auto` mode to detect vulnerabilities and services (e.g., HTTP, SMB, DNS).
- **Scripts**: Includes `http-slowloris`, `smb-vuln-*`, `broadcast-avahi-dos`, etc.
- **Execution**: Runs with aggressive `-T4` timing for rapid scanning.

### Tor Integration
- **Purpose**: Enables attacks on `.onion` domains via HTTP-based methods.
- **Setup**:
  1. Install Tor: `sudo apt install tor`
  2. Start service: `sudo service tor start`
  3. Use methods: `http`, `post`, `killer`, `bomb`, etc.

### Proxy Validation
- **Mechanism**: Validates proxies using HTTPBin, accepting only those with status codes <400.
- **Parallel Checking**: Uses `ThreadPoolExecutor` for fast validation.
- **Rotation**: Automatically rotates proxies to prevent IP bans.

## Troubleshooting
### Common Issues
| Issue                     | Solution                                                                 |
|---------------------------|--------------------------------------------------------------------------|
| `Permission denied`       | Run with `sudo` for Layer 3/4 attacks or Nmap scanning                   |
| `Nmap not found`          | Install Nmap: `sudo apt install nmap`                                    |
| `Scapy errors`            | Install Npcap (Windows) or ensure root access                            |
| `Proxy validation fails`  | Verify proxy format (`ip:port` or `protocol://ip:port`)                  |
| `Tor connection failed`   | Start Tor: `sudo service tor start`                                      |
| `Low PPS/BPS`             | Increase `--threads` and `--rpc`, use high-quality proxies               |

### Performance Optimization
- **Network**: Use a high-bandwidth connection (100Mbps+).
- **Hardware**: Multi-core CPU and 8GB+ RAM recommended.
- **Proxies**: Use 1000+ high-quality proxies for better distribution.
- **Threads**: Start with 500-1000 threads, scale based on system capacity.
- **RPC**: Set 100-500 requests per connection for optimal performance.

## Legal and Ethical Guidelines
### Authorized Use Only
- **Permission**: Obtain explicit written consent from the target system's owner.
- **Scope**: Define clear testing boundaries and duration.
- **Notification**: Inform stakeholders of testing schedules.
- **Documentation**: Maintain records of authorization and test results.

### Prohibited Activities
- Targeting production systems without permission.
- Conducting attacks that disrupt critical infrastructure.
- Sharing or distributing the tool for malicious purposes.

## Contributing
Contributions are welcome! Please submit issues or pull requests to [https://github.com/ChillHackLab/CHDDOS](https://github.com/ChillHackLab/CHDDOS).

## Contact
For inquiries, contact ChillHackLab:
- **Website**: [https://chillhack.net](https://chillhack.net)
- **Email**: [info@chillhack.net](mailto:info@chillhack.net)

## License
This project is licensed under the MIT License.

## About
CHDDOS supports Layer 3 (Network), Layer 4 (Transport), and Layer 7 (Application) attacks, with intelligent features like automated service detection, dynamic parameter adjustment, and real-time monitoring. Developed by ChillHackLab, Hong Kong.

© 2025 ChillHackLab