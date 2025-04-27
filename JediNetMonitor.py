#!/usr/bin/env python3
# JediSecX Network Monitor v1
# For Termux / Mobile Recon
# Domains: jedi-sec.com | jedi-sec.us | jedi-sec.cloud | jedi-sec.online | jedi-sec.me

import os
import time
import socket
import subprocess
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Create log directory
log_dir = "/sdcard/NetworkMonitorLogs"
os.makedirs(log_dir, exist_ok=True)

# Banner
def banner():
    print(Fore.GREEN + """
╔════════════════════════════╗
║   JediSecX Network Monitor  ║
╚════════════════════════════╝
Domains: jedi-sec.com | jedi-sec.us | jedi-sec.cloud | jedi-sec.online | jedi-sec.me
    """)

# Get local IP info
def device_info():
    print(Fore.CYAN + "\n[+] Fetching Device Info...")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(Fore.YELLOW + f"Hostname: {hostname}")
        print(Fore.YELLOW + f"Local IP: {local_ip}")
        return hostname, local_ip
    except Exception as e:
        print(Fore.RED + f"Error fetching IP: {e}")
        return None, None

# Scan network for active devices (using ping sweep)
def scan_active_devices():
    print(Fore.CYAN + "\n[+] Scanning active devices...")
    _, local_ip = device_info()
    if local_ip:
        network = '.'.join(local_ip.split('.')[:-1]) + '.'
        live_hosts = []
        for i in range(1, 255):
            ip = network + str(i)
            result = subprocess.run(['ping', '-c', '1', '-W', '1', ip],
                                    stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                print(Fore.YELLOW + f" - {ip} is ONLINE")
                live_hosts.append(ip)
        save_log("Active Devices", live_hosts)
        return live_hosts
    else:
        print(Fore.RED + "Unable to determine network.")

# Continuous Ping Monitor
def continuous_ping():
    target = input(Fore.GREEN + "\nEnter IP or Domain to ping: ").strip()
    print(Fore.CYAN + f"\n[+] Pinging {target} continuously (Ctrl+C to stop)")
    try:
        while True:
            response = subprocess.run(['ping', '-c', '1', target],
                                      stdout=subprocess.DEVNULL)
            if response.returncode == 0:
                print(Fore.YELLOW + f" - {target} is reachable")
            else:
                print(Fore.RED + f" - {target} is unreachable")
            time.sleep(2)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Stopped continuous ping.")

# Basic Port Scanner
def port_scan():
    target = input(Fore.GREEN + "\nEnter IP to scan ports: ").strip()
    ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389]
    print(Fore.CYAN + f"\n[+] Scanning common ports on {target}...")
    open_ports = []
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect((target, port))
            print(Fore.YELLOW + f" - Port {port} is OPEN")
            open_ports.append(port)
        except:
            pass
        finally:
            s.close()
    save_log(f"Open Ports on {target}", open_ports)

# Watch for new devices joining
def new_device_watch():
    print(Fore.CYAN + "\n[+] Watching for new devices... (Ctrl+C to stop)")
    known_hosts = set(scan_active_devices())
    try:
        while True:
            current_hosts = set(scan_active_devices())
            new_hosts = current_hosts - known_hosts
            if new_hosts:
                print(Fore.RED + f"\n[!] New Device(s) Detected: {', '.join(new_hosts)}")
                save_log("New Devices Detected", list(new_hosts))
                known_hosts.update(new_hosts)
            time.sleep(10)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Stopped device watch.")

# Save session log
def save_log(title, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{log_dir}/{title.replace(' ','_')}_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(f"{title}\nGenerated: {datetime.now()}\n\n")
        for item in data:
            f.write(f"{item}\n")
    print(Fore.GREEN + f"\n[+] Log saved to {filename}")

# Menu
def menu():
    while True:
        banner()
        print(Fore.GREEN + """
[1] Show Device Info
[2] Scan Active Devices
[3] Continuous Ping Monitor
[4] Open Port Scan (Basic)
[5] Start New Device Watch
[6] Exit
""")
        choice = input(Fore.YELLOW + "Enter choice: ").strip()
        if choice == '1':
            device_info()
        elif choice == '2':
            scan_active_devices()
        elif choice == '3':
            continuous_ping()
        elif choice == '4':
            port_scan()
        elif choice == '5':
            new_device_watch()
        elif choice == '6':
            print(Fore.RED + "Exiting...")
            sys.exit()
        else:
            print(Fore.RED + "Invalid choice!")

if __name__ == "__main__":
    menu()
