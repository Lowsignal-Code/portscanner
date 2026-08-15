# Port Scanner

A lightweight, multithreaded TCP port scanner written in Python. It scans a target host for open ports, identifies common services running on well-known ports, and attempts to grab service banners where available.

## Table of Contents

- [Features](#features)
- [Preview](#preview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Examples](#examples)
- [How It Works](#how-it-works)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)
- [License](#license)

## Features

- Multithreaded scanning for significantly faster results compared to sequential checks
- Support for scanning a single port, a range of ports, or a custom comma-separated list
- Automatic identification of common services (SSH, HTTP, FTP, MySQL, RDP, and others)
- Best-effort banner grabbing for open ports that respond with identifying data
- Configurable thread count and connection timeout
- Optional export of scan results to a text file
- Built entirely on Python's standard library, no external dependencies required

## Preview

```
=======================================================
Target       : example.com (93.184.216.34)
Ports        : 1024 port(s)
Threads      : 100
=======================================================
[+] 80     open    HTTP
[+] 443    open    HTTPS
-------------------------------------------------------
Found 2 open port(s) in 4.31 seconds.
```

## Requirements

- Python 3.7 or newer
- No third-party packages are required; the script relies only on modules included in the Python standard library (`socket`, `threading`, `queue`, `argparse`).

## Installation

Clone the repository:

```bash
git clone https://github.com/<HoneySpider-Code>/<portscanner>.git
cd <portscanner>
```

No further installation steps are needed since the script has no external dependencies.

## Usage

Run the scanner from the terminal, providing a target hostname or IP address:

```bash
python Main.py <target>
```

By default, the script scans ports 1 through 1024 using 100 threads and a 0.5 second timeout per connection.

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `target` | Hostname or IP address to scan (required, positional) | — |
| `-p`, `--ports` | Ports to scan. Accepts a single port, a range, or a comma-separated list (e.g. `80`, `1-1000`, `22,80,443`) | `1-1024` |
| `-t`, `--threads` | Number of worker threads used for scanning | `100` |
| `--timeout` | Connection timeout in seconds for each port | `0.5` |
| `-o`, `--output` | File path to save the scan results to | None |

## Examples

Scan the default port range on a target:

```bash
python port_scanner.py 192.168.1.1
```

Scan a specific range of ports:

```bash
python port_scanner.py 192.168.1.1 -p 1-1024
```

Scan a specific set of ports:

```bash
python port_scanner.py example.com --ports 21,22,80,443
```

Increase thread count for a faster scan and save the results to a file:

```bash
python port_scanner.py example.com -t 200 -o results.txt
```

Use a longer timeout for scanning hosts on a slower or less reliable network:

```bash
python port_scanner.py 10.0.0.5 --timeout 1.5
```

## How It Works

1. **Host resolution** — The target hostname is resolved to an IP address using `socket.gethostbyname()`. If resolution fails, the script exits with an error message.
2. **Port parsing** — The `--ports` argument is parsed into a sorted list of individual port numbers, supporting single values, ranges, and comma-separated combinations.
3. **Work queue** — All ports to be scanned are placed into a thread-safe `queue.Queue`.
4. **Worker threads** — A configurable number of daemon threads pull ports from the queue and attempt a TCP connection using `socket.connect_ex()`, which returns immediately with an error code instead of raising an exception, making it efficient for scanning many ports.
5. **Service identification** — When a port is open, it is checked against a dictionary of common ports (such as 22 for SSH or 443 for HTTPS) to display a likely service name.
6. **Banner grabbing** — The script attempts to read a short response from the open socket. Not all services send data immediately, so this step is best-effort and silently skipped if no banner is received within a short timeout.
7. **Reporting** — Open ports are printed as they are found, in a thread-safe manner using a lock to prevent overlapping output. A summary and optional results file are generated once all threads finish.

## Limitations

- This is a basic connect-scan (TCP full connect), not a stealth or SYN scan; it is easily visible to firewalls and intrusion detection systems.
- Banner grabbing is best-effort and may not work for services that require a specific handshake or request before responding.
- Very large port ranges combined with a high thread count may be limited by the operating system's maximum number of concurrent sockets.
- The tool only scans TCP ports; UDP scanning is not supported.
- Results may vary depending on network conditions, firewalls, and rate limiting on the target host.

## Roadmap

Potential future improvements include:

- UDP port scanning support
- Export of results in structured formats such as JSON or CSV
- A progress indicator for large scans
- Optional stealth (SYN) scanning using raw sockets
- Service version detection beyond simple banner grabbing

## Disclaimer

This tool is intended for educational purposes and for use on systems and networks you own or have explicit authorization to test. Scanning networks or hosts without permission may be illegal in many jurisdictions. The author assumes no responsibility for misuse of this software.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
