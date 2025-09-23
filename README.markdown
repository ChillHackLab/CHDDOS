# CHDDOS - Advanced DoS/DDoS Simulation Tool

**Developed by ChillHack Hong Kong Web Development**  
**Website**: [https://chillhack.net](https://chillhack.net)  
**Contact**: [info@chillhack.net](mailto:info@chillhack.net)

**WARNING: This tool is strictly for authorized penetration testing only. Unauthorized use for cyber attacks is illegal and carries severe legal consequences (extremely high) under global cybersecurity laws. Use responsibly and ethically.**

## Overview
CHDDOS is a Python-based, advanced DoS/DDoS simulation tool designed for ethical penetration testing. It supports Layer 3 (Network), Layer 4 (Transport), and Layer 7 (Application) attacks, with intelligent features like automated service detection, dynamic parameter adjustment, and real-time monitoring. Built to surpass tools like MHDDoS, CHDDOS offers enhanced stability, user-friendliness, and modern features for testing network resilience in authorized environments.

## Features
- **Multi-Layer Attacks**: Supports 12 attack methods across Layers 3, 4, and 7:
  - **Layer 3**: IP Spoof Flood, ICMP Flood
  - **Layer 4**: SYN Flood, UDP Flood, TCP Flood, NTP Amplification, SSDP Amplification
  - **Layer 7**: HTTP Flood, POST Flood, Slowloris, Cloudflare Bypass (CFB), RUDY
- **Automated Service Detection**: Scans open ports and identifies services (HTTP, HTTPS, DNS, FTP, SSH, SSDP) to select optimal attack methods.
- **Dynamic Parameter Adjustment**: Adjusts RPC (requests per connection) and timeout based on response times and HTTP status codes (e.g., 429 rate limiting).
- **Botnet Simulation**: Randomizes source IPs and `X-Forwarded-For` headers to mimic distributed attacks.
- **Proxy Support**: Supports HTTP, SOCKS4, SOCKS5 proxies with automatic proxy downloading via ProxyScrape API.
- **Real-Time Monitoring**: Displays PPS (packets per second), BPS (bytes per second), CPU/memory usage, with color-coded output (red for low success rate, green for high PPS) and ASCII trend charts.
- **CSV Logging**: Records attack metrics (PPS, BPS, CPU, memory, worker stats) to CSV for post-test analysis.
- **Machine Learning Prediction**: Uses a simple ML-based scoring system to predict the best attack method based on success rates and response times.
- **Cross-Platform Compatibility**: Enhanced Windows support with `colorama` for ANSI colors.

## Installation
### Prerequisites
- Python 3.8+
- Required libraries: `aiohttp`, `scapy`, `dnspython`, `pysocks`, `tqdm`, `psutil`, `requests`, `colorama`
- Root privileges for `--spoof`, `--botnet`, or `--tor` options

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/ChillHack/chddos.git
   cd chddos
   ```
2. Install dependencies:
   ```bash
   pip install aiohttp scapy dnspython pysocks tqdm psutil requests colorama
   ```
3. For root-required features (e.g., IP spoofing, botnet simulation, Tor):
   - Ensure `sudo` privileges.
   - Install and configure Tor for `--tor` (e.g., `sudo apt install tor` on Debian/Ubuntu).

## Usage
Run `chddos.py` with the following command-line arguments:

```bash
python3 chddos.py -t <target> -p <ports> [options]
```

### Command-Line Options
| Option | Description | Example |
|--------|-------------|---------|
| `-t, --target` | Target IP/domain or file with targets (required) | `-t example.com` or `-t targets.txt` |
| `-p, --port` | Target ports (comma-separated, required) | `-p 80,443` |
| `--proxy-file` | Proxy list file (IP:Port) | `--proxy-file proxies.txt` |
| `--proxy-type` | Proxy type (http, socks4, socks5) | `--proxy-type socks5` |
| `-r, --agent-file` | Custom User-Agent list file | `--agent-file agents.txt` |
| `--add-agent` | Additional User-Agents (comma-separated) | `--add-agent "Mozilla/5.0,Opera/9.80"` |
| `--threads` | Number of threads (default: 100) | `--threads 200` |
| `--rpc` | Requests per connection (default: 10) | `--rpc 20` |
| `--duration` | Attack duration in seconds (default: 300) | `--duration 600` |
| `--spoof` | Enable IP spoofing (requires root) | `--spoof` |
| `--tor` | Use Tor network (requires root) | `--tor` |
| `--botnet` | Simulate botnet with randomized source IPs (requires root) | `--botnet` |
| `--dns-resolvers` | DNS resolvers for amplification | `--dns-resolvers "8.8.8.8:53,1.1.1.1:53"` |
| `--ntp-resolvers` | NTP resolvers for amplification | `--ntp-resolvers "pool.ntp.org:123"` |
| `--ssdp-resolvers` | SSDP resolvers for amplification | `--ssdp-resolvers "239.255.255.250:1900"` |

### Example Commands
- Basic HTTP attack:
  ```bash
  python3 chddos.py -t example.com -p 80,443
  ```
- Botnet simulation with proxies:
  ```bash
  sudo python3 chddos.py -t target.txt -p 80,443 --botnet --proxy-file proxies.txt --proxy-type socks5
  ```
- DNS amplification:
  ```bash
  sudo python3 chddos.py -t target.txt -p 53 --dns-resolvers "8.8.8.8:53,1.1.1.1:53"
  ```
- SSDP amplification:
  ```bash
  sudo python3 chddos.py -t target.txt -p 1900 --ssdp-resolvers "239.255.255.250:1900"
  ```

## Output
The tool displays real-time attack status for each target, including:
- Worker status (port, service, attack type, sent/failed requests, success rate).
- Aggregated stats for "Other Workers" and a total row.
- Attack metrics (Duration, PPS, BPS, CPU, Memory) with color highlights (red for success rate < 0.8, green for PPS > 1000).
- ASCII chart showing PPS and success rate trends.
- CSV report (`chddos_report_<timestamp>.csv`) for post-test analysis.

Example output:
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

## Legal Disclaimer
**CHDDOS is developed solely for authorized penetration testing and educational purposes.** Unauthorized use of this tool for cyber attacks is strictly prohibited and violates global cybersecurity laws, including but not limited to the **Computer Fraud and Abuse Act (CFAA)**, **EU Cybersecurity Act**, and **Hong Kong Computer Crimes Ordinance**. Such actions carry **extremely high legal consequences**, including fines, imprisonment, and civil liabilities.

**ChillHack Hong Kong Web Development and its contributors are not responsible for any misuse or damage caused by this tool.** Always obtain explicit permission from the target system's owner before conducting any tests.

## Contributing
Contributions are welcome! Please submit pull requests or issues to [https://github.com/ChillHack/chddos](https://github.com/ChillHack/chddos).

## Contact
For inquiries, contact ChillHack Hong Kong Web Development:  
- **Email**: [info@chillhack.net](mailto:info@chillhack.net)  
- **Website**: [https://chillhack.net](https://chillhack.net)

---

# CHDDOS - 進階 DoS/DDoS 模擬工具

**由 ChillHack 香港網站開發公司開發**  
**網站**：[https://chillhack.net](https://chillhack.net)  
**聯繫方式**：[info@chillhack.net](mailto:info@chillhack.net)

**警告：本工具僅限於授權滲透測試使用。未經授權用於網絡攻擊係非法行為，根據全球網絡安全法規將承擔極高法律後果。請負責任同合乎倫理地使用。**

## 概覽
CHDDOS 係一個基於 Python 嘅進階 DoS/DDoS 模擬工具，專為合法滲透測試設計。佢支援第 3 層（網絡層）、第 4 層（傳輸層）同第 7 層（應用層）攻擊，具備智能化功能，例如自動服務檢測、動態參數調整同實時監控。CHDDOS 目標超越 MHDDoS，提供更高穩定性、易用性同現代化功能，適合喺授權環境下測試網絡抗壓能力。

## 功能
- **多層攻擊**：支援 12 種攻擊方法，涵蓋第 3、4、7 層：
  - **第 3 層**：IP 偽造洪水、ICMP 洪水
  - **第 4 層**：SYN 洪水、UDP 洪水、TCP 洪水、NTP 放大、SSDP 放大
  - **第 7 層**：HTTP 洪水、POST 洪水、Slowloris、Cloudflare 繞過 (CFB)、RUDY
- **自動服務檢測**：掃描開放端口並識別服務（HTTP、HTTPS、DNS、FTP、SSH、SSDP），自動選擇最佳攻擊方法。
- **動態參數調整**：根據響應時間同 HTTP 狀態碼（例如 429 速率限制）動態調整 RPC（每連線請求數）同超時時間。
- **殭屍網絡模擬**：隨機化來源 IP 及 `X-Forwarded-For` 頭，模擬分散式攻擊。
- **代理支持**：支援 HTTP、SOCKS4、SOCKS5 代理，透過 ProxyScrape API 自動下載代理。
- **實時監控**：顯示 PPS（每秒封包數）、BPS（每秒位元數）、CPU/記憶體使用率，帶有顏色高亮（成功率 < 0.8 紅色，PPS > 1000 綠色）同 ASCII 趨勢圖表。
- **CSV 記錄**：將攻擊數據（PPS、BPS、CPU、記憶體、線程狀態）記錄到 CSV 文件，方便後續分析。
- **機器學習預測**：使用簡單 ML 計分系統，根據成功率同響應時間預測最佳攻擊方法。
- **跨平台兼容**：透過 `colorama` 增強 Windows ANSI 顏色支持。

## 安裝
### 前置條件
- Python 3.8 或以上
- 必要庫：`aiohttp`、`scapy`、`dnspython`、`pysocks`、`tqdm`、`psutil`、`requests`、`colorama`
- `--spoof`、`--botnet` 或 `--tor` 需 root 權限

### 安裝步驟
1. 克隆倉庫：
   ```bash
   git clone https://github.com/ChillHack/chddos.git
   cd chddos
   ```
2. 安裝依賴：
   ```bash
   pip install aiohttp scapy dnspython pysocks tqdm psutil requests colorama
   ```
3. 針對需 root 權限嘅功能（例如 IP 偽造、殭屍網絡模擬、Tor）：
   - 確保有 `sudo` 權限。
   - 安裝並配置 Tor（例如 Debian/Ubuntu 上：`sudo apt install tor`）。

## 使用方法
使用以下命令運行 `chddos.py`：

```bash
python3 chddos.py -t <目標> -p <端口> [選項]
```

### 命令行選項
| 選項 | 描述 | 範例 |
|------|------|------|
| `-t, --target` | 目標 IP/域名或目標文件（必須） | `-t example.com` 或 `-t targets.txt` |
| `-p, --port` | 目標端口（逗號分隔，必須） | `-p 80,443` |
| `--proxy-file` | 代理列表文件（IP:Port） | `--proxy-file proxies.txt` |
| `--proxy-type` | 代理類型 (http, socks4, socks5) | `--proxy-type socks5` |
| `-r, --agent-file` | 自定義 User-Agent 列表文件 | `--agent-file agents.txt` |
| `--add-agent` | 額外 User-Agent（逗號分隔） | `--add-agent "Mozilla/5.0,Opera/9.80"` |
| `--threads` | 線程數（預設：100） | `--threads 200` |
| `--rpc` | 每連線請求數（預設：10） | `--rpc 20` |
| `--duration` | 攻擊持續時間（秒，預設：300） | `--duration 600` |
| `--spoof` | 啟用 IP 偽造（需 root 權限） | `--spoof` |
| `--tor` | 使用 Tor 網絡（需 root 權限） | `--tor` |
| `--botnet` | 模擬殭屍網絡（需 root 權限） | `--botnet` |
| `--dns-resolvers` | DNS 放大解析器 | `--dns-resolvers "8.8.8.8:53,1.1.1.1:53"` |
| `--ntp-resolvers` | NTP 放大解析器 | `--ntp-resolvers "pool.ntp.org:123"` |
| `--ssdp-resolvers` | SSDP 放大解析器 | `--ssdp-resolvers "239.255.255.250:1900"` |

### 使用範例
- 基本 HTTP 攻擊：
  ```bash
  python3 chddos.py -t example.com -p 80,443
  ```
- 殭屍網絡模擬加代理：
  ```bash
  sudo python3 chddos.py -t target.txt -p 80,443 --botnet --proxy-file proxies.txt --proxy-type socks5
  ```
- DNS 放大攻擊：
  ```bash
  sudo python3 chddos.py -t target.txt -p 53 --dns-resolvers "8.8.8.8:53,1.1.1.1:53"
  ```
- SSDP 放大攻擊：
  ```bash
  sudo python3 chddos.py -t target.txt -p 1900 --ssdp-resolvers "239.255.255.250:1900"
  ```

## 輸出
工具會實時顯示每個目標嘅攻擊狀態，包括：
- 線程狀態（端口、服務、攻擊類型、發送/失敗請求、成功率）。
- 「其他線程」聚合統計同總計行。
- 攻擊指標（持續時間、PPS、BPS、CPU、記憶體），帶有顏色高亮（成功率 < 0.8 紅色，PPS > 1000 綠色）。
- ASCII 圖表顯示 PPS 同成功率趨勢。
- CSV 報告（`chddos_report_<時間戳>.csv`）用於後續分析。

範例輸出：
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

## 法律免責聲明
**CHDDOS 僅為授權滲透測試同教育目的開發。** 未經授權使用本工具進行網絡攻擊係嚴格禁止嘅非法行為，違反全球網絡安全法規，包括但不限於**美國《計算機詐欺與濫用法》（CFAA）**、**歐盟網絡安全法案**同**香港《電腦罪行條例》**。此類行為將承擔**極高法律後果**，包括罰款、監禁同民事責任。

**ChillHack 香港網站開發公司及其貢獻者對任何濫用或由此工具造成嘅損害概不負責。** 在進行任何測試前，必須獲得目標系統擁有者嘅明確授權。

## 貢獻
歡迎貢獻！請提交 pull request 或 issue 至 [https://github.com/ChillHack/chddos](https://github.com/ChillHack/chddos)。

## 聯繫方式
如有查詢，請聯繫 ChillHack 香港網站開發公司：  
- **電郵**：[info@chillhack.net](mailto:info@chillhack.net)  
- **網站**：[https://chillhack.net](https://chillhack.net)