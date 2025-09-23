# CHDDOS Manual

**Developed by ChillHack Hong Kong Web Development**  
**Website**: [https://chillhack.net](https://chillhack.net)  
**Contact**: [info@chillhack.net](mailto:info@chillhack.net)  
**Version**: 1.0 (September 23, 2025)

**WARNING: CHDDOS is strictly for authorized penetration testing and educational purposes only. Unauthorized use for cyber attacks is illegal and carries extremely high legal consequences under global cybersecurity laws, including the Computer Fraud and Abuse Act (CFAA), EU Cybersecurity Act, and Hong Kong Computer Crimes Ordinance. Use responsibly and obtain explicit permission from system owners before testing.**

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Advanced Configuration](#advanced-configuration)
6. [Output Interpretation](#output-interpretation)
7. [Legal Disclaimer](#legal-disclaimer)
8. [Contributing](#contributing)
9. [Contact](#contact)

---

## Introduction
CHDDOS is a Python-based, advanced Denial of Service (DoS) and Distributed Denial of Service (DDoS) simulation tool designed for ethical penetration testing. Built to surpass existing tools like MHDDoS, CHDDOS offers a modern, stable, and user-friendly platform for testing network and application resilience in authorized environments. It supports a wide range of attack methods across OSI Layers 3, 4, and 7, with intelligent features such as automated service detection, dynamic parameter adjustment, and comprehensive monitoring.

This manual provides detailed instructions for installing, configuring, and using CHDDOS, along with guidance on interpreting its output and adhering to legal and ethical standards.

---

## Features
CHDDOS includes the following key features:

- **Multi-Layer Attack Support**:
  - **Layer 3 (Network)**: IP Spoof Flood, ICMP Flood
  - **Layer 4 (Transport)**: SYN Flood, UDP Flood, TCP Flood, NTP Amplification, SSDP Amplification
  - **Layer 7 (Application)**: HTTP Flood, POST Flood, Slowloris, Cloudflare Bypass (CFB), RUDY (R-U-Dead-Yet)
- **Automated Service Detection**:
  - Scans target ports (e.g., 21, 22, 80, 443, 53, 123, 1900) to identify services (HTTP, HTTPS, DNS, FTP, SSH, SSDP).
  - Dynamically selects optimal attack methods based on detected services.
- **Dynamic Parameter Adjustment**:
  - Adjusts requests per connection (RPC) and timeout based on response times and HTTP status codes (e.g., reduces RPC on 429 Too Many Requests).
  - Switches attack methods if success rate falls below 0.2.
- **Botnet Simulation**:
  - Randomizes source IPs (Layers 3/4) and `X-Forwarded-For` headers (Layer 7) to mimic distributed attacks.
- **Proxy Support**:
  - Supports HTTP, SOCKS4, and SOCKS5 proxies, with automatic downloading from ProxyScrape API.
  - Integrates Tor for anonymous testing (requires root privileges).
- **Real-Time Monitoring**:
  - Displays packets per second (PPS), bytes per second (BPS), CPU, and memory usage.
  - Color-coded output: red for success rate < 0.8, green for PPS > 1000.
  - ASCII charts for PPS and success rate trends.
- **CSV Logging**:
  - Records attack metrics (timestamp, target, PPS, BPS, CPU, memory, worker stats) to a CSV file for post-test analysis.
- **Machine Learning Prediction**:
  - Uses a weighted scoring system to predict the most effective attack method based on success rates and response times.
- **Cross-Platform Compatibility**:
  - Enhanced Windows support via `colorama` for ANSI color output.
  - Cross-platform console clearing (`cls` for Windows, `clear` for Linux).

---

## Installation
### Prerequisites
- **Operating System**: Linux (recommended), Windows, or macOS
- **Python**: 3.8 or higher
- **Dependencies**: `aiohttp`, `scapy`, `dnspython`, `pysocks`, `tqdm`, `psutil`, `requests`, `colorama`
- **Root Privileges**: Required for `--spoof`, `--botnet`, or `--tor` options
- **Tor**: Optional, for anonymous testing with `--tor` (install via `sudo apt install tor` on Debian/Ubuntu)

### Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ChillHack/chddos.git
   cd chddos
   ```
2. **Install Dependencies**:
   ```bash
   pip install aiohttp scapy dnspython pysocks tqdm psutil requests colorama
   ```
   - If `pip` fails, ensure you have Python 3.8+ and use `pip3`.
   - On Linux, you may need to install `libpcap` for `scapy`: `sudo apt install libpcap-dev`.
3. **Configure Tor (Optional)**:
   - Install Tor: `sudo apt install tor` (Debian/Ubuntu) or `brew install tor` (macOS).
   - Start Tor service: `sudo service tor start`.
4. **Verify Permissions**:
   - For IP spoofing, botnet simulation, or Tor, run the script with `sudo`:
     ```bash
     sudo python3 chddos.py --help
     ```

---

## Usage
CHDDOS is controlled via command-line arguments. The basic syntax is:

```bash
python3 chddos.py -t <target> -p <ports> [options]
```

### Command-Line Arguments
| Argument | Description | Example |
|----------|-------------|---------|
| `-t, --target` | Target IP/domain or file containing targets (required) | `-t example.com` or `-t targets.txt` |
| `-p, --port` | Target ports (comma-separated, required) | `-p 80,443` |
| `--proxy-file` | File with proxy list (IP:Port) | `--proxy-file proxies.txt` |
| `--proxy-type` | Proxy type: `http`, `socks4`, `socks5` (default: `http`) | `--proxy-type socks5` |
| `-r, --agent-file` | File with custom User-Agent list | `--agent-file agents.txt` |
| `--add-agent` | Additional User-Agents (comma-separated) | `--add-agent "Mozilla/5.0,Opera/9.80"` |
| `--threads` | Number of threads (default: 100, max: 1000) | `--threads 200` |
| `--rpc` | Requests per connection (default: 10, max: 100) | `--rpc 20` |
| `--duration` | Attack duration in seconds (default: 300) | `--duration 600` |
| `--spoof` | Enable IP spoofing (requires root) | `--spoof` |
| `--tor` | Use Tor network (requires root) | `--tor` |
| `--botnet` | Simulate botnet with randomized source IPs (requires root) | `--botnet` |
| `--dns-resolvers` | DNS resolvers for amplification (default: `8.8.8.8:53,1.1.1.1:53`) | `--dns-resolvers "8.8.8.8:53,1.1.1.1:53"` |
| `--ntp-resolvers` | NTP resolvers for amplification (default: `pool.ntp.org:123`) | `--ntp-resolvers "pool.ntp.org:123"` |
| `--ssdp-resolvers` | SSDP resolvers for amplification (default: `239.255.255.250:1900`) | `--ssdp-resolvers "239.255.255.250:1900"` |

### Example Commands
1. **Basic HTTP Attack**:
   ```bash
   python3 chddos.py -t example.com -p 80,443
   ```
   - Targets `example.com` on ports 80 and 443 with HTTP-based attacks.
2. **Botnet Simulation with Proxies**:
   ```bash
   sudo python3 chddos.py -t target.txt -p 80,443 --botnet --proxy-file proxies.txt --proxy-type socks5
   ```
   - Simulates a botnet attack with randomized IPs and SOCKS5 proxies.
3. **DNS Amplification**:
   ```bash
   sudo python3 chddos.py -t target.txt -p 53 --dns-resolvers "8.8.8.8:53,1.1.1.1:53"
   ```
   - Performs DNS amplification attack on port 53.
4. **SSDP Amplification**:
   ```bash
   sudo python3 chddos.py -t target.txt -p 1900 --ssdp-resolvers "239.255.255.250:1900"
   ```
   - Targets IoT devices with SSDP amplification.
5. **Custom User-Agent Attack**:
   ```bash
   python3 chddos.py -t example.com -p 80 --agent-file agents.txt --add-agent "Mozilla/5.0,Opera/9.80"
   ```
   - Uses custom User-Agent list and additional agents for HTTP attacks.

### Notes
- **Root Privileges**: Use `sudo` for `--spoof`, `--botnet`, or `--tor` to enable IP spoofing or Tor routing.
- **Target File**: Create a `targets.txt` file with one IP/domain per line (e.g., `example.com\n192.168.1.1`).
- **Proxy File**: Format as `IP:Port` per line (e.g., `192.168.1.100:8080`).
- **Service Detection**: If no ports are open, CHDDOS falls back to user-specified ports.

---

## Advanced Configuration
### Optimizing Attack Parameters
- **Threads (`--threads`)**:
  - Default: 100. Increase for higher load (e.g., `--threads 500`), but monitor CPU/memory usage to avoid crashes.
  - Maximum: 1000 (adjusted based on system limits).
- **Requests per Connection (`--rpc`)**:
  - Default: 10. Increase for aggressive attacks (e.g., `--rpc 50`), but reduce if rate-limited (429 status).
- **Duration (`--duration`)**:
  - Default: 300 seconds. Extend for prolonged tests (e.g., `--duration 1800` for 30 minutes).
- **Dynamic Adjustment**:
  - CHDDOS automatically adjusts RPC and timeout:
    - Response time < 0.5s: RPC increases by 1.5x (max 100).
    - Response time > 2.0s or 429 status: RPC decreases by 0.5x (min 1).
    - Timeout adjusts dynamically (0.8x on success, 1.5x on failure, max 3.0s).

### Proxy and Botnet Configuration
- **Proxies**:
  - Use `--proxy-file` for a custom proxy list or rely on ProxyScrape API for automatic downloads.
  - Test proxies with `--proxy-type socks5` for better anonymity.
- **Botnet Simulation**:
  - Enable `--botnet` to randomize source IPs (Layers 3/4) and `X-Forwarded-For` headers (Layer 7).
  - Requires root privileges and is mutually exclusive with `--spoof` and `--proxy-file`.
- **Tor Integration**:
  - Enable `--tor` for anonymous routing (requires Tor service running).
  - Ensure Tor is configured (`sudo service tor start`).

### Customizing Attack Methods
- **Layer 3/4 Attacks**:
  - Use `--spoof` or `--botnet` for IP spoofing in `ip_spoof_flood`, `icmp_flood`, `syn_flood`, `udp_flood`, `tcp_flood`, `ntp_amplification`, `ssdp_amplification`.
  - Specify resolvers for amplification attacks (e.g., `--dns-resolvers`, `--ntp-resolvers`, `--ssdp-resolvers`).
- **Layer 7 Attacks**:
  - Use `--agent-file` or `--add-agent` to customize User-Agent headers for `http_flood`, `post_flood`, `cfb_flood`, `rudy_flood`.
  - `cfb_flood` includes randomized `Referer` headers to bypass Cloudflare.
  - `rudy_flood` sends slow POST requests to exhaust server connections.

### CSV Logging
- Attack metrics are logged to `chddos_report_<timestamp>.csv`.
- Fields: Timestamp, Target, PPS, BPS, CPU, Memory, Worker, Port, Service, Attack, Sent, Failed, Success Rate.
- Example:
  ```
  Timestamp,Target,PPS,BPS,CPU,Memory,Worker,Port,Service,Attack,Sent,Failed,Success Rate
  2025-09-23 15:17:31,example.com,649,356506,6.8,65.8,example.com:80:0,80,http,http,100,5,0.95
  ```

---

## Output Interpretation
CHDDOS provides real-time output for monitoring attack progress:

### Example Output
```
Target: example.com
Worker           Port  Service    Attack     Sent     Failed   Success Rate
example.com:80:0 80    http       http       100      5        0.95
example.com:80:1 80    http       post       90       10       0.90
Other Workers    -     -          -          450      20       0.96
Total            -     -          -          640      35       0.95
Attack Status | Duration: 31s / 300s
PPS: 649 | BPS: 356,506 | CPU: 6.8% | Memory: 65.8%
PPS and Success Rate Trend:
██████████████████████████ | PPS: 649 | Success Rate: 0.95
████████████████████████ | PPS: 620 | Success Rate: 0.94
...
--------------------------------------------------------------------------------
```

### Explanation
- **Worker Table**:
  - **Worker**: Unique identifier for each thread (e.g., `example.com:80:0`).
  - **Port**: Target port (e.g., 80).
  - **Service**: Detected service (e.g., `http`, `dns`).
  - **Attack**: Current attack method (e.g., `http`, `syn`).
  - **Sent/Failed**: Number of successful/failed requests or packets.
  - **Success Rate**: Ratio of successful requests (colored red if < 0.8).
- **Other Workers**: Aggregates stats for threads beyond the top 5 (abnormal or normal).
- **Total**: Summarizes sent, failed, and average success rate for all workers.
- **Attack Status**:
  - **Duration**: Current runtime vs. total duration (e.g., `31s / 300s`).
  - **PPS/BPS**: Packets/bytes per second (PPS colored green if > 1000).
  - **CPU/Memory**: System resource usage.
- **ASCII Chart**: Visualizes PPS and success rate trends over the last 10 seconds.

### CSV Report
- Located at `chddos_report_<timestamp>.csv`.
- Useful for post-test analysis and generating penetration testing reports.

---

## Legal Disclaimer
**CHDDOS is developed exclusively for authorized penetration testing and educational purposes.** Unauthorized use of this tool for cyber attacks is strictly prohibited and violates global cybersecurity laws, including:
- **United States**: Computer Fraud and Abuse Act (CFAA)
- **European Union**: EU Cybersecurity Act
- **Hong Kong**: Computer Crimes Ordinance

Such actions carry **extremely high legal consequences**, including substantial fines, imprisonment, and civil liabilities. **ChillHack Hong Kong Web Development and its contributors are not responsible for any misuse or damage caused by this tool.** Always obtain explicit written permission from the target system's owner before conducting any tests.

---

## Contributing
We welcome contributions to improve CHDDOS! To contribute:
1. Fork the repository: [https://github.com/ChillHack/chddos](https://github.com/ChillHack/chddos)
2. Create a pull request with your changes or report issues.
3. Ensure code adheres to ethical standards and includes proper documentation.

---

## Contact
For inquiries, feedback, or support, contact ChillHack Hong Kong Web Development:
- **Email**: [info@chillhack.net](mailto:info@chillhack.net)
- **Website**: [https://chillhack.net](https://chillhack.net)

---

# CHDDOS 使用手冊

**由 ChillHack 香港網站開發公司開發**  
**網站**：[https://chillhack.net](https://chillhack.net)  
**聯繫方式**：[info@chillhack.net](mailto:info@chillhack.net)  
**版本**：1.0（2025年9月23日）

**警告：CHDDOS 僅限於授權滲透測試同教育用途。未經授權用於網絡攻擊係非法行為，違反全球網絡安全法規，包括美國《計算機詐欺與濫用法》（CFAA）、歐盟網絡安全法案同香港《電腦罪行條例》，將承擔極高法律後果，包括高額罰款、監禁同民事責任。請負責任使用並獲得系統擁有者嘅明確許可。**

## 目錄
1. [介紹](#介紹)
2. [功能](#功能)
3. [安裝](#安裝)
4. [使用方法](#使用方法)
5. [進階配置](#進階配置)
6. [輸出解釋](#輸出解釋)
7. [法律免責聲明](#法律免責聲明)
8. [貢獻](#貢獻)
9. [聯繫方式](#聯繫方式)

---

## 介紹
CHDDOS 係一個基於 Python 嘅進階拒絕服務（DoS）同分散式拒絕服務（DDoS）模擬工具，專為合法滲透測試設計。佢目標超越 MHDDoS 等現有工具，提供現代化、穩定同用戶友好嘅平台，用於喺授權環境下測試網絡同應用程式嘅抗壓能力。CHDDOS 支援 OSI 第 3、4、7 層嘅多種攻擊方法，具備智能化功能，例如自動服務檢測、動態參數調整同全面監控。

本手冊提供詳細嘅安裝、配置同使用說明，同時解釋輸出內容並強調法律同倫理標準。

---

## 功能
CHDDOS 包含以下核心功能：

- **多層攻擊支援**：
  - **第 3 層（網絡層）**：IP 偽造洪水、ICMP 洪水
  - **第 4 層（傳輸層）**：SYN 洪水、UDP 洪水、TCP 洪水、NTP 放大、SSDP 放大
  - **第 7 層（應用層）**：HTTP 洪水、POST 洪水、Slowloris、Cloudflare 繞過 (CFB)、RUDY
- **自動服務檢測**：
  - 掃描目標端口（例如 21、22、80、443、53、123、1900），識別服務（HTTP、HTTPS、DNS、FTP、SSH、SSDP）。
  - 根據檢測結果動態選擇最佳攻擊方法。
- **動態參數調整**：
  - 根據響應時間同 HTTP 狀態碼（例如 429 速率限制）調整每連線請求數（RPC）同超時時間。
  - 若成功率低於 0.2，自動切換攻擊方法。
- **殭屍網絡模擬**：
  - 喺第 3/4 層隨機化來源 IP，第 7 層隨機化 `X-Forwarded-For` 頭，模擬分散式攻擊。
- **代理支持**：
  - 支援 HTTP、SOCKS4、SOCKS5 代理，透過 ProxyScrape API 自動下載。
  - 整合 Tor 進行匿名測試（需 root 權限）。
- **實時監控**：
  - 顯示每秒封包數（PPS）、每秒位元數（BPS）、CPU 同記憶體使用率。
  - 顏色高亮：成功率 < 0.8 紅色，PPS > 1000 綠色。
  - ASCII 圖表顯示 PPS 同成功率趨勢。
- **CSV 記錄**：
  - 將攻擊數據（時間戳、目標、PPS、BPS、CPU、記憶體、線程狀態）記錄到 CSV 文件。
- **機器學習預測**：
  - 使用基於成功率同響應時間嘅加權計分系統，預測最佳攻擊方法。
- **跨平台兼容**：
  - 透過 `colorama` 增強 Windows ANSI 顏色支持。
  - 跨平台清屏（Windows 用 `cls`，Linux 用 `clear`）。

---

## 安裝
### 前置條件
- **操作系統**：Linux（推薦）、Windows 或 macOS
- **Python**：3.8 或以上
- **依賴庫**：`aiohttp`、`scapy`、`dnspython`、`pysocks`、`tqdm`、`psutil`、`requests`、`colorama`
- **Root 權限**：`--spoof`、`--botnet` 或 `--tor` 選項需 root 權限
- **Tor**：可選，用於 `--tor` 匿名測試（Debian/Ubuntu 上：`sudo apt install tor`）

### 安裝步驟
1. **克隆倉庫**：
   ```bash
   git clone https://github.com/ChillHack/chddos.git
   cd chddos
   ```
2. **安裝依賴**：
   ```bash
   pip install aiohttp scapy dnspython pysocks tqdm psutil requests colorama
   ```
   - 若 `pip` 失敗，確保使用 Python 3.8+ 並嘗試 `pip3`。
   - Linux 上可能需為 `scapy` 安裝 `libpcap`：`sudo apt install libpcap-dev`。
3. **配置 Tor（可選）**：
   - 安裝 Tor：`sudo apt install tor`（Debian/Ubuntu）或 `brew install tor`（macOS）。
   - 啟動 Tor 服務：`sudo service tor start`。
4. **驗證權限**：
   - 針對需 root 權限嘅功能，運行：
     ```bash
     sudo python3 chddos.py --help
     ```

---

## 使用方法
CHDDOS 透過命令行參數控制，基本語法為：

```bash
python3 chddos.py -t <目標> -p <端口> [選項]
```

### 命令行參數
| 參數 | 描述 | 範例 |
|------|------|------|
| `-t, --target` | 目標 IP/域名或包含目標嘅文件（必須） | `-t example.com` 或 `-t targets.txt` |
| `-p, --port` | 目標端口（逗號分隔，必須） | `-p 80,443` |
| `--proxy-file` | 代理列表文件（IP:Port） | `--proxy-file proxies.txt` |
| `--proxy-type` | 代理類型：`http`、`socks4`、`socks5`（預設：`http`） | `--proxy-type socks5` |
| `-r, --agent-file` | 自定義 User-Agent 列表文件 | `--agent-file agents.txt` |
| `--add-agent` | 額外 User-Agent（逗號分隔） | `--add-agent "Mozilla/5.0,Opera/9.80"` |
| `--threads` | 線程數（預設：100，最大：1000） | `--threads 200` |
| `--rpc` | 每連線請求數（預設：10，最大：100） | `--rpc 20` |
| `--duration` | 攻擊持續時間（秒，預設：300） | `--duration 600` |
| `--spoof` | 啟用 IP 偽造（需 root 權限） | `--spoof` |
| `--tor` | 使用 Tor 網絡（需 root 權限） | `--tor` |
| `--botnet` | 模擬殭屍網絡，隨機化來源 IP（需 root 權限） | `--botnet` |
| `--dns-resolvers` | DNS 放大解析器（預設：`8.8.8.8:53,1.1.1.1:53`） | `--dns-resolvers "8.8.8.8:53,1.1.1.1:53"` |
| `--ntp-resolvers` | NTP 放大解析器（預設：`pool.ntp.org:123`） | `--ntp-resolvers "pool.ntp.org:123"` |
| `--ssdp-resolvers` | SSDP 放大解析器（預設：`239.255.255.250:1900`） | `--ssdp-resolvers "239.255.255.250:1900"` |

### 使用範例
1. **基本 HTTP 攻擊**：
   ```bash
   python3 chddos.py -t example.com -p 80,443
   ```
   - 針對 `example.com` 嘅 80 同 443 端口進行 HTTP 攻擊。
2. **殭屍網絡模擬加代理**：
   ```bash
   sudo python3 chddos.py -t target.txt -p 80,443 --botnet --proxy-file proxies.txt --proxy-type socks5
   ```
   - 使用隨機 IP 同 SOCKS5 代理模擬殭屍網絡攻擊。
3. **DNS 放大攻擊**：
   ```bash
   sudo python3 chddos.py -t target.txt -p 53 --dns-resolvers "8.8.8.8:53,1.1.1.1:53"
   ```
   - 喺 53 端口進行 DNS 放大攻擊。
4. **SSDP 放大攻擊**：
   ```bash
   sudo python3 chddos.py -t target.txt -p 1900 --ssdp-resolvers "239.255.255.250:1900"
   ```
   - 針對 IoT 設備進行 SSDP 放大攻擊。
5. **自定義 User-Agent 攻擊**：
   ```bash
   python3 chddos.py -t example.com -p 80 --agent-file agents.txt --add-agent "Mozilla/5.0,Opera/9.80"
   ```
   - 使用自定義 User-Agent 列表同額外 User-Agent 進行 HTTP 攻擊。

### 注意事項
- **Root 權限**：`--spoof`、`--botnet` 或 `--tor` 需使用 `sudo` 運行。
- **目標文件**：`targets.txt` 每行一個 IP/域名（例如：`example.com\n192.168.1.1`）。
- **代理文件**：格式為每行 `IP:Port`（例如：`192.168.1.100:8080`）。
- **服務檢測**：若無開放端口，CHDDOS 會使用用戶指定端口。

---

## 進階配置
### 優化攻擊參數
- **線程數（`--threads`）**：
  - 預設：100。增加可提升負載（例如：`--threads 500`），但需監控 CPU/記憶體避免崩潰。
  - 最大值：1000（根據系統限制自動調整）。
- **每連線請求數（`--rpc`）**：
  - 預設：10。增加可加強攻擊（例如：`--rpc 50`），若遇 429 狀態碼則應降低。
- **持續時間（`--duration`）**：
  - 預設：300 秒。延長可用於長期測試（例如：`--duration 1800` 表示 30 分鐘）。
- **動態調整**：
  - CHDDOS 自動調整 RPC 同超時時間：
    - 響應時間 < 0.5 秒：RPC 增加 1.5 倍（最大 100）。
    - 響應時間 > 2.0 秒或 429 狀態碼：RPC 減少 0.5 倍（最小 1）。
    - 超時時間成功時減少 0.8 倍，失敗時增加 1.5 倍（最大 3.0 秒）。

### 代理同殭屍網絡配置
- **代理**：
  - 使用 `--proxy-file` 指定自定義代理列表，或依賴 ProxyScrape API 自動下載。
  - 使用 `--proxy-type socks5` 可提升匿名性。
- **殭屍網絡模擬**：
  - 啟用 `--botnet` 隨機化第 3/4 層來源 IP 及第 7 層 `X-Forwarded-For` 頭。
  - 需 root 權限，與 `--spoof` 及 `--proxy-file` 互斥。
- **Tor 整合**：
  - 啟用 `--tor` 進行匿名路由（需運行 Tor 服務）。
  - 確保 Tor 已配置（`sudo service tor start`）。

### 自定義攻擊方法
- **第 3/4 層攻擊**：
  - 使用 `--spoof` 或 `--botnet` 啟用 IP 偽造，適用於 `ip_spoof_flood`、`icmp_flood`、`syn_flood`、`udp_flood`、`tcp_flood`、`ntp_amplification`、`ssdp_amplification`。
  - 指定放大攻擊解析器（例如 `--dns-resolvers`、`--ntp-resolvers`、`--ssdp-resolvers`）。
- **第 7 層攻擊**：
  - 使用 `--agent-file` 或 `--add-agent` 自定義 User-Agent，適用於 `http_flood`、`post_flood`、`cfb_flood`、`rudy_flood`。
  - `cfb_flood` 包含隨機 `Referer` 頭以繞過 Cloudflare。
  - `rudy_flood` 發送慢速 POST 請求，耗盡服務器連線。

### CSV 記錄
- 攻擊數據記錄於 `chddos_report_<時間戳>.csv`。
- 字段：時間戳、目標、PPS、BPS、CPU、記憶體、線程、端口、服務、攻擊類型、發送數、失敗數、成功率。
- 範例：
  ```
  Timestamp,Target,PPS,BPS,CPU,Memory,Worker,Port,Service,Attack,Sent,Failed,Success Rate
  2025-09-23 15:17:31,example.com,649,356506,6.8,65.8,example.com:80:0,80,http,http,100,5,0.95
  ```

---

## 輸出解釋
CHDDOS 提供實時輸出以監控攻擊進度：

### 範例輸出
```
Target: example.com
Worker           Port  Service    Attack     Sent     Failed   Success Rate
example.com:80:0 80    http       http       100      5        0.95
example.com:80:1 80    http       post       90       10       0.90
Other Workers    -     -          -          450      20       0.96
Total            -     -          -          640      35       0.95
Attack Status | Duration: 31s / 300s
PPS: 649 | BPS: 356,506 | CPU: 6.8% | Memory: 65.8%
PPS and Success Rate Trend:
██████████████████████████ | PPS: 649 | Success Rate: 0.95
████████████████████████ | PPS: 620 | Success Rate: 0.94
...
--------------------------------------------------------------------------------
```

### 解釋
- **線程表格**：
  - **線程（Worker）**：每個線程嘅唯一標識（例如：`example.com:80:0`）。
  - **端口（Port）**：目標端口（例如：80）。
  - **服務（Service）**：檢測到嘅服務（例如：`http`、`dns`）。
  - **攻擊類型（Attack）**：當前攻擊方法（例如：`http`、`syn`）。
  - **發送/失敗（Sent/Failed）**：成功/失敗嘅請求或封包數。
  - **成功率（Success Rate）**：成功請求比例（若 < 0.8 顯示紅色）。
- **其他線程（Other Workers）**：聚合超過前 5 條線程（異常或正常）嘅統計。
- **總計（Total）**：總結所有線程嘅發送數、失敗數同平均成功率。
- **攻擊狀態（Attack Status）**：
  - **持續時間（Duration）**：當前運行時間 vs 總時間（例如：`31s / 300s`）。
  - **PPS/BPS**：每秒封包數/位元數（PPS > 1000 顯示綠色）。
  - **CPU/記憶體**：系統資源使用率。
- **ASCII 圖表**：顯示最近 10 秒嘅 PPS 同成功率趨勢。

### CSV 報告
- 儲存於 `chddos_report_<時間戳>.csv`。
- 用於後續分析同滲透測試報告生成。

---

## 法律免責聲明
**CHDDOS 僅為授權滲透測試同教育目的開發。** 未經授權使用本工具進行網絡攻擊係嚴格禁止嘅非法行為，違反全球網絡安全法規，包括：
- **美國**：計算機詐欺與濫用法（CFAA）
- **歐盟**：網絡安全法案
- **香港**：電腦罪行條例

此類行為將承擔**極高法律後果**，包括高額罰款、監禁同民事責任。**ChillHack 香港網站開發公司及其貢獻者對任何濫用或由此工具造成嘅損害概不負責。** 在進行任何測試前，必須獲得目標系統擁有者嘅明確書面許可。

---

## 貢獻
我們歡迎貢獻以改進 CHDDOS！貢獻方式：
1. 複製倉庫：[https://github.com/ChillHack/chddos](https://github.com/ChillHack/chddos)
2. 提交 pull request 或報告 issue。
3. 確保程式碼符合倫理標準並包含完整文檔。

---

## 聯繫方式
如有查詢、反饋或支持需求，請聯繫 ChillHack 香港網站開發公司：
- **電郵**：[info@chillhack.net](mailto:info@chillhack.net)
- **網站**：[https://chillhack.net](https://chillhack.net)
