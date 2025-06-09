import argparse
import re
import socket
import threading
import time
import random
import sys
import signal
import json
import ssl
from urllib.parse import urlparse
from itertools import cycle

try:
    import socks
except ImportError:
    print("Pls pip install PySocks")
    sys.exit(1)

class Colors:
    RED, GREEN, YELLOW, CYAN, BOLD, END = '\033[91m', '\033[92m', '\033[93m', '\033[96m', '\033[1m', '\033[0m'

class ProtocolHandlerBase:
    def __init__(self, target_ip, target_port, target_hostname, is_https, stats_manager, payload=None, proxies=None, payload_mode='random'):
        self.target_ip = target_ip
        self.target_port = target_port
        self.target_hostname = target_hostname
        self.is_https = is_https
        self.stats_manager = stats_manager
        self.payload_list = payload if isinstance(payload, list) else [payload]
        self.payload_mode = payload_mode
        self.payload_iterator = cycle(self.payload_list) if self.payload_list else None

        self.proxies = proxies
        self.running = True

    def stop(self):
        self.running = False

    def get_payload(self):
        if not self.payload_list or self.payload_list[0] is None:
            return None
        
        if self.payload_mode == 'sequential' and self.payload_iterator:
            return next(self.payload_iterator)
        else: 
            return random.choice(self.payload_list)

    def create_socket(self):
        raw_socket = None
        if self.proxies:
            proxy_address = random.choice(self.proxies).split(':')
            proxy_ip, proxy_port = proxy_address[0], int(proxy_address[1])
            raw_socket = socks.socksocket()
            try:
                raw_socket.set_proxy(socks.SOCKS5, proxy_ip, proxy_port)
            except socks.ProxyError as e:
                self.stats_manager.update_stats(False, 0, f"Proxy Error: {e}")
                return None
        else:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.is_https:
            context = ssl.create_default_context()
            return context.wrap_socket(raw_socket, server_hostname=self.target_hostname)
        else:
            return raw_socket
    
    def run(self):
        raise NotImplementedError

class HTTPHandler(ProtocolHandlerBase):
    def run(self):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        while self.running:
            s = self.create_socket()
            if not s: continue
            
            try:
                s.settimeout(10)
                s.connect((self.target_ip, self.target_port))
                
                payload = self.get_payload()
                request = ""

                if payload:
                    request_body = json.dumps(payload) if isinstance(payload, dict) else str(payload)
                    content_type = "application/json" if isinstance(payload, dict) else "application/x-www-form-urlencoded"
                    request = f"POST / HTTP/1.1\r\nHost: {self.target_hostname}\r\nUser-Agent: {user_agent}\r\nContent-Type: {content_type}\r\nContent-Length: {len(request_body)}\r\nConnection: close\r\n\r\n{request_body}"
                else:
                    random_path = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(8))
                    request = f"GET /?r={random_path} HTTP/1.1\r\nHost: {self.target_hostname}\r\nUser-Agent: {user_agent}\r\nConnection: close\r\n\r\n"
                
                s.sendall(request.encode())
                s.recv(4096)
                self.stats_manager.update_stats(True, len(request.encode()))
            except Exception as e:
                self.stats_manager.update_stats(False, 0, str(e))
            finally:
                s.close()
            time.sleep(random.uniform(0.01, 0.05)) 

class TCPHandler(ProtocolHandlerBase):
    def run(self):
        while self.running:
            s = self.create_socket()
            if not s: continue
            try:
                s.settimeout(5)
                s.connect((self.target_ip, self.target_port))
                data_to_send = str(self.get_payload() or random.randbytes(512)).encode()
                s.sendall(data_to_send)
                self.stats_manager.update_stats(True, len(data_to_send))
            except Exception as e:
                self.stats_manager.update_stats(False, 0, str(e))
            finally:
                s.close()
            time.sleep(random.uniform(0.01, 0.05))

class UDPHandler(ProtocolHandlerBase):
    def run(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data_to_send = str(self.get_payload() or random.randbytes(1024)).encode()
                s.sendto(data_to_send, (self.target_ip, self.target_port))
                s.close()
                self.stats_manager.update_stats(True, len(data_to_send))
            except Exception as e:
                self.stats_manager.update_stats(False, 0, str(e))
            time.sleep(0.001)

class StatsManager:
    def __init__(self, target_url):
        self.target_url = target_url
        self.stats = {
            'target': self.target_url,
            'start_time': time.time(),
            'end_time': None, 'duration': 0, 'total_requests': 0, 
            'successful': 0, 'failed': 0, 'total_bytes_sent': 0, 
            'avg_rps': 0, 'errors': {}
        }
        self.lock = threading.Lock()

    def update_stats(self, success, sent_bytes, error_msg=None):
        with self.lock:
            self.stats['total_requests'] += 1
            self.stats['total_bytes_sent'] += sent_bytes
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
                if error_msg:
                    self.stats['errors'][error_msg] = self.stats['errors'].get(error_msg, 0) + 1

    def print_live_stats(self):
        with self.lock:
            elapsed = time.time() - self.stats['start_time']
            rps = self.stats['total_requests'] / elapsed if elapsed > 0 else 0
            total_mb = self.stats['total_bytes_sent'] / (1024*1024)
            sys.stdout.write("\x1b[2J\x1b[H")
            print(f"{Colors.BOLD}--- Spax Live Test Results ---{Colors.END}")
            print(f"[*] {Colors.CYAN}Target:{Colors.END} {self.target_url}")
            print(f"[*] {Colors.CYAN}Status:{Colors.END} {Colors.GREEN}RUNNING{Colors.END}")
            print(f"[*] {Colors.CYAN}Duration:{Colors.END} {elapsed:.2f}s")
            print("------------------------------")
            print(f"[*] {Colors.CYAN}Requests:{Colors.END} {self.stats['total_requests']} (RPS: {rps:.2f})")
            print(f"[*] {Colors.CYAN}Data Sent:{Colors.END} {total_mb:.2f} MB")
            print(f"[*] {Colors.GREEN}Successful:{Colors.END} {self.stats['successful']}")
            print(f"[*] {Colors.RED}Failed:{Colors.END} {self.stats['failed']}")
            print("------------------------------")
            print(f"{Colors.YELLOW}[!] Top Errors:{Colors.END}")
            top_errors = sorted(self.stats['errors'].items(), key=lambda item: item[1], reverse=True)
            for msg, count in top_errors[:4]:
                print(f"  - {count}x: {msg[:70]}")
            sys.stdout.flush()

    def generate_report(self, report_file=None):
        self.stats['end_time'] = time.time()
        self.stats['duration'] = round(self.stats['end_time'] - self.stats['start_time'], 2)
        self.stats['avg_rps'] = round(self.stats['total_requests'] / self.stats['duration'] if self.stats['duration'] > 0 else 0, 2)
        
        print("\n\n--- Final Report ---")
        for key, value in self.stats.items():
            if key != 'errors':
                print(f"{Colors.CYAN}[*] {key.replace('_', ' ').title()}:{Colors.END} {value if isinstance(value, (int, float)) else value}")
        
        if report_file:
            if report_file.endswith('.json'):
                self._save_json_report(report_file)
            elif report_file.endswith('.html'):
                self._save_html_report(report_file)
            else:
                print(f"\n{Colors.YELLOW}[!] Unknown report format. Please use .json or .html{Colors.END}")

    def _save_json_report(self, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(self.stats, f, indent=4)
            print(f"\n{Colors.GREEN}[+] JSON report saved to {filename}{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}[-] Failed to save JSON report: {e}{Colors.END}")

    def _save_html_report(self, filename):
        html_content = f"""
        <html>
        <head><title>Spax Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }}
            h1 {{ color: #4a4a4a; }}
            .container {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .errors {{ margin-top: 20px; }}
            .errors li {{ background: #ffebee; padding: 8px; border-left: 4px solid #f44336; margin-bottom: 5px; }}
        </style>
        </head>
        <body>
            <div class="container">
                <h1>Spax Test Report</h1>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Target</td><td>{self.stats['target']}</td></tr>
                    <tr><td>Total Duration</td><td>{self.stats['duration']}s</td></tr>
                    <tr><td>Total Requests</td><td>{self.stats['total_requests']}</td></tr>
                    <tr><td>Average RPS</td><td>{self.stats['avg_rps']}</td></tr>
                    <tr><td>Successful Requests</td><td>{self.stats['successful']}</td></tr>
                    <tr><td>Failed Requests</td><td>{self.stats['failed']}</td></tr>
                    <tr><td>Total Data Sent</td><td>{self.stats['total_bytes_sent'] / (1024*1024):.2f} MB</td></tr>
                </table>
                <div class="errors">
                    <h2>Top Errors</h2>
                    <ul>{"".join(f"<li><b>{count}x:</b> {msg}</li>" for msg, count in sorted(self.stats['errors'].items(), key=lambda item: item[1], reverse=True)[:5])}</ul>
                </div>
            </div>
        </body>
        </html>
        """
        try:
            with open(filename, 'w') as f:
                f.write(html_content)
            print(f"\n{Colors.GREEN}[+] HTML report saved to {filename}{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}[-] Failed to save HTML report: {e}{Colors.END}")

class SpaxEngine:
    def __init__(self, args):
        self.args = args
        self.target_url = None
        self.target_ip = None
        self.target_hostname = None
        self.target_port = 80
        self.is_https = False
        self.protocol_handlers = []
        self.running = False
        self.proxies = []
        self.payload = self.load_payload(args.payload_file)
        self.stats_manager = None
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def load_file_lines(self, filename):
        if not filename: return []
        try:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            print(f"{Colors.GREEN}[+] Loaded {len(lines)} lines from {filename}{Colors.END}")
            return lines
        except Exception as e:
            print(f"{Colors.RED}[-] Could not read file {filename}: {e}{Colors.END}")
            return []

    def load_payload(self, filename):
        if not filename: return None
        try:
            with open(filename, 'r') as f:
                if filename.endswith('.json'):
                    data = json.load(f)
                    return data if isinstance(data, list) else [data]
                else:
                    return [f.read()]
        except Exception as e:
            print(f"{Colors.RED}[-] Could not read payload file: {e}{Colors.END}")
            return None
        
    def signal_handler(self, sig, frame):
        print(f"\n{Colors.YELLOW}[!] Stop signal received. Shutting down gracefully...{Colors.END}")
        self.stop()

    def parse_target(self):
        try:
            target = self.args.target
            if not re.match(r'http(s)?://', target):
                 target = 'http://' + target
            
            parsed = urlparse(target)
            if not parsed.hostname:
                raise ValueError("Hostname could not be determined from target.")

            self.target_url = target
            self.target_hostname = parsed.hostname
            self.is_https = parsed.scheme == 'https'
            self.target_port = parsed.port or (443 if self.is_https else 80)
            self.target_ip = socket.gethostbyname(self.target_hostname)
            self.stats_manager = StatsManager(self.target_url)
            return True
        except (socket.gaierror, ValueError) as e:
            print(f"{Colors.RED}[-] Failed to parse or resolve target: {e}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}[-] An unexpected error occurred during target parsing: {e}{Colors.END}")
            return False

    def start(self):
        if not self.parse_target(): return

        if self.args.proxy_file:
            self.proxies = self.load_file_lines(self.args.proxy_file)

        protocol_map = {'http': HTTPHandler, 'tcp': TCPHandler, 'udp': UDPHandler}
        protocol_class = protocol_map.get(self.args.protocol)
        if not protocol_class:
            print(f"{Colors.RED}[-] Invalid protocol: {self.args.protocol}{Colors.END}")
            return

        self.running = True
        print(f"{Colors.YELLOW}[*] Starting test with {self.args.threads} threads...{Colors.END}")
        
        if self.args.ramp_up:
            print(f"{Colors.CYAN}[*] Ramping up over {self.args.ramp_up} seconds...{Colors.END}")
        
        total_threads = self.args.threads
        ramp_up_time = self.args.ramp_up or 1
        
        for i in range(total_threads):
            if not self.running: break
            handler = protocol_class(
                self.target_ip, self.target_port, self.target_hostname, self.is_https,
                self.stats_manager, self.payload, self.proxies, self.args.payload_mode
            )
            t = threading.Thread(target=handler.run, daemon=True)
            t.start()
            self.protocol_handlers.append(handler)
            time.sleep(ramp_up_time / total_threads)

        try:
            while self.running:
                self.stats_manager.print_live_stats()
                time.sleep(1)
                if self.args.duration and (time.time() - self.stats_manager.stats['start_time']) > self.args.duration:
                    print(f"\n{Colors.YELLOW}[!] Duration of {self.args.duration}s reached. Stopping...{Colors.END}")
                    self.stop()
        except KeyboardInterrupt:
            self.stop()
        
        if self.running:
             self.stop()

    def stop(self):
        if not self.running: return
        self.running = False
        for handler in self.protocol_handlers:
            handler.stop()
        time.sleep(1)
        self.stats_manager.generate_report(self.args.report_file)

def main():
    parser = argparse.ArgumentParser(
        description='Spax - Advanced Traffic Generation & Load Testing Framework',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('target', help='Target URL (e.g., https://example.com)')
    parser.add_argument('-p', '--protocol', default='http', choices=['http', 'tcp', 'udp'], help='Protocol to use.')
    parser.add_argument('-t', '--threads', type=int, default=25, help='Total number of concurrent threads.')
    parser.add_argument('-d', '--duration', type=int, help='Total test duration in seconds.')
    parser.add_argument('--ramp-up', type=int, help='Time in seconds to gradually reach the full number of threads.')
    parser.add_argument('--proxy-file', help='Path to a text file containing proxies (IP:PORT).')
    parser.add_argument('--payload-file', help='Path to a file with data (JSON for http, raw for tcp/udp).')
    parser.add_argument('--payload-mode', default='random', choices=['random', 'sequential'], help='How to use payloads from the file.')
    parser.add_argument('--report-file', help='Path to save the final results (e.g., results.json or report.html).')
    
    args = parser.parse_args()
    
    global spax_engine
    spax_engine = SpaxEngine(args)
    spax_engine.start()

if __name__ == "__main__":
    main()

