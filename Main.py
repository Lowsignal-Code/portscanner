import socket
import sys
import argparse
import threading
import queue
import time

# a few well-known ports so we can show a friendly name next to the number
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Alt",
}

print_lock = threading.Lock()
open_ports = []


def parse_port_range(port_arg):
    """Turn something like '1-100' or '22,80,443' into a list of ints."""
    ports = set()

    for part in port_arg.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-")
            start, end = int(start), int(end)
            if start > end:
                start, end = end, start
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))

    return sorted(ports)


def resolve_host(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        print(f"Could not resolve host: {target}")
        sys.exit(1)


def grab_banner(sock):
    # not every service sends a banner right away, so this is best-effort
    try:
        sock.settimeout(0.8)
        banner = sock.recv(1024)
        return banner.decode(errors="ignore").strip()
    except Exception:
        return ""


def scan_port(ip, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            service = COMMON_PORTS.get(port, "unknown")
            banner = grab_banner(sock)

            with print_lock:
                line = f"[+] {port:<6} open    {service}"
                if banner:
                    line += f"  -> {banner[:50]}"
                print(line)

            open_ports.append(port)
    except socket.error:
        pass
    finally:
        sock.close()


def worker(ip, timeout, q):
    while True:
        try:
            port = q.get_nowait()
        except queue.Empty:
            return
        scan_port(ip, port, timeout)
        q.task_done()


def run_scan(ip, ports, threads, timeout):
    q = queue.Queue()
    for p in ports:
        q.put(p)

    workers = []
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(ip, timeout, q), daemon=True)
        t.start()
        workers.append(t)

    for t in workers:
        t.join()


def save_results(target, ip, ports, duration, filename):
    with open(filename, "w") as f:
        f.write(f"Scan results for {target} ({ip})\n")
        f.write(f"Ports scanned: {len(ports) if ports else 0}\n")
        f.write(f"Scan duration: {duration:.2f}s\n\n")

        if open_ports:
            for p in sorted(open_ports):
                service = COMMON_PORTS.get(p, "unknown")
                f.write(f"{p}\t{service}\n")
        else:
            f.write("No open ports found.\n")

    print(f"\nResults saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description="A basic multithreaded TCP port scanner.")
    parser.add_argument("target", help="hostname or IP address to scan")
    parser.add_argument(
        "-p", "--ports", default="1-1024",
        help="ports to scan, e.g. 80 or 1-1000 or 22,80,443 (default: 1-1024)"
    )
    parser.add_argument(
        "-t", "--threads", type=int, default=100,
        help="number of threads to use (default: 100)"
    )
    parser.add_argument(
        "--timeout", type=float, default=0.5,
        help="connection timeout in seconds (default: 0.5)"
    )
    parser.add_argument(
        "-o", "--output", help="save results to a text file"
    )

    args = parser.parse_args()

    ip = resolve_host(args.target)
    try:
        ports = parse_port_range(args.ports)
    except ValueError:
        print("Invalid port format. Use something like 80 or 1-1000 or 22,80,443")
        sys.exit(1)

    print("=" * 55)
    print(f"Target       : {args.target} ({ip})")
    print(f"Ports        : {len(ports)} port(s)")
    print(f"Threads      : {args.threads}")
    print("=" * 55)

    start = time.time()
    run_scan(ip, ports, args.threads, args.timeout)
    duration = time.time() - start

    print("-" * 55)
    if open_ports:
        print(f"Found {len(open_ports)} open port(s) in {duration:.2f} seconds.")
    else:
        print(f"No open ports found. ({duration:.2f} seconds)")

    if args.output:
        save_results(args.target, ip, ports, duration, args.output)


if __name__ == "__main__":
    main()
