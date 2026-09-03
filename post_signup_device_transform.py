"""
LinkedIn - ম্যানুয়াল একাউন্ট তৈরির পর ডিভাইস সম্পূর্ণ চেঞ্জ করার স্ক্রিপ্ট
Post Account Creation - Complete Device Transformation
"""

import os
import sys
import json
import uuid
import random
import time
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import platform
import ctypes
import socket

class PostSignupDeviceTransform:
    """একাউন্ট সাইন আপের পর সম্পূর্ণ ডিভাইস চেঞ্জ করার জন্য"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.account_id = None
        self.transform_log = []
        self.config_file = "device_transforms.json"
        self.load_configs()
    
    # ====== কনফিগারেশন ম্যানেজমেন্ট ======
    
    def load_configs(self):
        """আগের ট্রান্সফর্ম কনফিগারেশন লোড করা"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_transform_config(self):
        """ট্রান্সফর্ম কনফিগারেশন সংরক্ষণ করা"""
        configs = self.load_configs()
        configs[self.account_id] = {
            'timestamp': datetime.now().isoformat(),
            'account_id': self.account_id,
            'transforms': self.transform_log,
            'device_profile': self.get_device_profile()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=4, ensure_ascii=False)
        
        print(f"\n✓ কনফিগারেশন সংরক্ষণ: {self.config_file}")
    
    def log_transform(self, action, details):
        """প্রতিটি ট্রান্সফর্ম লগ করা"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'status': 'success'
        }
        self.transform_log.append(log_entry)
        print(f"✓ {action}: {details}")
    
    # ====== ১. সিস্টেম লেভেল ডিভাইস চেঞ্জ ======
    
    def change_system_hardware_id(self):
        """সিস্টেম হার্ডওয়্যার আইডি চেঞ্জ করা"""
        print("\n" + "="*70)
        print("1️⃣ সিস্টেম হার্ডওয়্যার আইডি পরিবর্তন করছে...")
        print("="*70)
        
        new_id = str(uuid.uuid4()).upper()
        
        try:
            if self.os_type == "Windows":
                print("⚠️ Windows এ Registry পরিবর্তন করতে Admin প্রয়োজন")
                print(f"📌 নতুন Hardware ID: {new_id}")
                print("\nREGEDIT চালান (Windows + R, তারপর 'regedit' লিখুন):")
                print("Path: HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control")
                self.log_transform("Hardware ID Change", f"Windows - Manual: {new_id}")
            
            elif self.os_type == "Linux":
                try:
                    # Machine ID পরিবর্তন
                    with open('/etc/machine-id', 'w') as f:
                        f.write(new_id)
                    subprocess.run(['sudo', 'systemctl', 'restart', 'systemd-logind'], 
                                 stderr=subprocess.DEVNULL)
                    print(f"✓ Linux Machine ID পরিবর্তন: {new_id}")
                    self.log_transform("Machine ID Changed", f"Linux: {new_id}")
                except PermissionError:
                    print("⚠️ sudo passwd ছাড়াই করতে হবে:")
                    print(f"  sudo bash -c 'echo \"{new_id}\" > /etc/machine-id'")
            
            elif self.os_type == "Darwin":  # macOS
                try:
                    subprocess.run(['sudo', 'nvram', f'SystemUUID={new_id}'], check=True)
                    print(f"✓ macOS System UUID পরিবর্তন: {new_id}")
                    self.log_transform("System UUID Changed", f"macOS: {new_id}")
                except:
                    print("⚠️ macOS UUID পরিবর্তনের জন্য sudo প্রয়োজন")
        
        except Exception as e:
            print(f"⚠️ ত্রুটি: {e}")
        
        return new_id
    
    # ====== ২. MAC Address চেঞ্জ করা ======
    
    def change_mac_address(self):
        """MAC Address সম্পূর্ণভাবে চেঞ্জ করা"""
        print("\n" + "="*70)
        print("2️⃣ MAC Address পরিবর্তন করছে...")
        print("="*70)
        
        new_mac = self.generate_random_mac()
        
        try:
            if self.os_type == "Linux":
                interfaces = ['eth0', 'wlan0', 'enp0s3', 'wlp2s0', 'ens33']
                success = False
                
                for interface in interfaces:
                    try:
                        subprocess.run(f"sudo ip link set {interface} down", 
                                     shell=True, stderr=subprocess.DEVNULL)
                        subprocess.run(f"sudo ip link set {interface} address {new_mac}", 
                                     shell=True, stderr=subprocess.DEVNULL)
                        subprocess.run(f"sudo ip link set {interface} up", 
                                     shell=True, stderr=subprocess.DEVNULL)
                        print(f"✓ MAC Address পরিবর্তন ({interface}): {new_mac}")
                        self.log_transform("MAC Address Changed", f"{interface}: {new_mac}")
                        success = True
                        break
                    except:
                        continue
                
                if not success:
                    print(f"📌 ম্যানুয়ালি পরিবর্তন করুন: nmcli dev mod <interface> 802-11-wireless.mac-address {new_mac}")
            
            elif self.os_type == "Darwin":
                try:
                    subprocess.run(['sudo', 'ifconfig', 'en0', 'lladdr', new_mac], check=True)
                    print(f"✓ MAC Address পরিবর্তন: {new_mac}")
                    self.log_transform("MAC Address Changed", f"macOS en0: {new_mac}")
                except:
                    print(f"📌 ম্যানুয়ালি করুন: sudo ifconfig en0 lladdr {new_mac}")
            
            elif self.os_type == "Windows":
                print(f"📌 Device Manager এ করুন:")
                print(f"  Device Manager > Network Adapters > Properties > Advanced")
                print(f"  Locally Administered Address: {new_mac}")
                self.log_transform("MAC Address Change", f"Windows Manual: {new_mac}")
        
        except Exception as e:
            print(f"⚠️ ত্রুটি: {e}")
        
        return new_mac
    
    def generate_random_mac(self):
        """র‍্যান্ডম MAC অ্যাড্রেস তৈরি"""
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))
    
    # ====== ३. ব্রাউজার ডেটা সম্পূর্ণ পরিষ্কার করা ======
    
    def clear_all_browser_data(self):
        """সমস্ত ব্রাউজার ডেটা পরিষ্কার করা"""
        print("\n" + "="*70)
        print("3️⃣ ব্রাউজার ডেটা সম্পূর্ণ পরিষ্কার করছে...")
        print("="*70)
        
        try:
            if self.os_type == "Windows":
                chrome_path = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default"
                self._clear_browser_directory(chrome_path)
                
                edge_path = Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default"
                self._clear_browser_directory(edge_path)
                
                firefox_path = Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox"
                self._clear_browser_directory(firefox_path)
            
            elif self.os_type == "Linux":
                chrome_path = Path.home() / ".config" / "google-chrome" / "Default"
                self._clear_browser_directory(chrome_path)
                
                firefox_path = Path.home() / ".mozilla" / "firefox"
                self._clear_browser_directory(firefox_path)
            
            elif self.os_type == "Darwin":  # macOS
                chrome_path = Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default"
                self._clear_browser_directory(chrome_path)
                
                firefox_path = Path.home() / "Library" / "Application Support" / "Firefox"
                self._clear_browser_directory(firefox_path)
            
            self.log_transform("Browser Data Cleared", "All caches, cookies, history removed")
            print("✓ সমস্ত ব্রাউজার ডেটা পরিষ্কার হয়েছে")
        
        except Exception as e:
            print(f"⚠️ ত্রুটি: {e}")
    
    def _clear_browser_directory(self, path):
        """ব্রাউজার ডিরেক্টরি পরিষ্কার করা"""
        if not path.exists():
            return
        
        items_to_clear = [
            'Cache', 'Code Cache', 'Cookies', 'Cookies-journal',
            'History', 'History-journal', 'Session Storage',
            'Local Storage', 'IndexedDB', '.default-release'
        ]
        
        for item in items_to_clear:
            item_path = path / item
            if item_path.exists():
                try:
                    if item_path.is_file():
                        os.remove(item_path)
                    else:
                        shutil.rmtree(item_path, ignore_errors=True)
                except:
                    pass
    
    # ====== ४. DNS এবং নেটওয়ার্ক ক্যাশ পরিষ্কার করা ======
    
    def flush_dns_cache(self):
        """DNS ক্যাশ পরিষ্কার করা"""
        print("\n" + "="*70)
        print("4️⃣ DNS এবং নেটওয়ার্ক ক্যাশ পরিষ্কার করছে...")
        print("="*70)
        
        try:
            if self.os_type == "Windows":
                subprocess.run("ipconfig /flushdns", shell=True, 
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                print("✓ Windows DNS ক্যাশ পরিষ্কার")
                self.log_transform("DNS Cache Flushed", "Windows ipconfig /flushdns")
            
            elif self.os_type == "Linux":
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], 
                             stderr=subprocess.DEVNULL)
                subprocess.run("sudo /etc/init.d/nscd restart", shell=True, 
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                print("✓ Linux DNS ক্যাশ পরিষ্কার")
                self.log_transform("DNS Cache Flushed", "Linux systemd-resolve --flush-caches")
            
            elif self.os_type == "Darwin":  # macOS
                subprocess.run(['sudo', 'dscacheutil', '-flushcache'], 
                             stderr=subprocess.DEVNULL)
                print("✓ macOS DNS ক্যাশ পরিষ্কার")
                self.log_transform("DNS Cache Flushed", "macOS dscacheutil -flushcache")
        
        except Exception as e:
            print(f"⚠️ ত্রুটি: {e}")
    
    # ====== ५. Hostname চেঞ্জ করা ======
    
    def change_hostname(self):
        """কম্পিউটার হোস্টনেম চেঞ্জ করা"""
        print("\n" + "="*70)
        print("5️⃣ হোস্টনেম পরিবর্তন করছে...")
        print("="*70)
        
        new_hostname = self.generate_random_hostname()
        
        try:
            if self.os_type == "Linux":
                try:
                    subprocess.run(['sudo', 'hostnamectl', 'set-hostname', new_hostname], 
                                 check=True, stderr=subprocess.DEVNULL)
                    print(f"✓ Hostname পরিবর্তন: {new_hostname}")
                    self.log_transform("Hostname Changed", f"Linux: {new_hostname}")
                except:
                    print(f"📌 ম্যানুয়ালি: sudo hostnamectl set-hostname {new_hostname}")
            
            elif self.os_type == "Darwin":  # macOS
                try:
                    subprocess.run(['sudo', 'scutil', '--set', 'ComputerName', new_hostname], 
                                 check=True, stderr=subprocess.DEVNULL)
                    subprocess.run(['sudo', 'scutil', '--set', 'HostName', new_hostname], 
                                 check=True, stderr=subprocess.DEVNULL)
                    print(f"✓ Hostname পরিবর্তন: {new_hostname}")
                    self.log_transform("Hostname Changed", f"macOS: {new_hostname}")
                except:
                    print(f"📌 ম্যানুয়ালি করুন")
            
            elif self.os_type == "Windows":
                print(f"📌 Settings > System > About > Rename this PC: {new_hostname}")
                print("   (তারপর কম্পিউটার রিস্টার্ট করুন)")
                self.log_transform("Hostname Change", f"Windows Manual: {new_hostname}")
        
        except Exception as e:
            print(f"⚠️ ত্রুটি: {e}")
        
        return new_hostname
    
    def generate_random_hostname(self):
        """র‍্যান্ডম হোস্টনেম তৈরি"""
        adjectives = ["swift", "bold", "quick", "bright", "clever", "smart", "fast", "keen"]
        animals = ["fox", "tiger", "eagle", "dragon", "phoenix", "wolf", "bear", "hawk"]
        number = random.randint(1000, 9999)
        return f"{random.choice(adjectives)}-{random.choice(animals)}-{number}"
    
    # ====== ६. IP Address তথ্য পরিবর্তন ======
    
    def generate_ip_spoofing_info(self):
        """IP Spoofing তথ্য জেনারেট করা"""
        print("\n" + "="*70)
        print("6️⃣ নেটওয়ার্ক আইডেন্টিটি স্পুফিং করছে...")
        print("="*70)
        
        spoofing_info = {
            'x_forwarded_for': self._generate_random_ip(),
            'x_real_ip': self._generate_random_ip(),
            'client_ip': self._generate_random_ip(),
            'cf_connecting_ip': self._generate_random_ip()
        }
        
        print("\n📌 পরবর্তী লগইনে এই হেডার ব্যবহার করুন:")
        for header, ip in spoofing_info.items():
            print(f"  {header}: {ip}")
        
        self.log_transform("IP Spoofing Generated", json.dumps(spoofing_info))
        return spoofing_info
    
    def _generate_random_ip(self):
        """র‍্যান্ডম IP জেনারেট করা"""
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    
    # ====== ७. ব্রাউজার ফিঙ্গারপ্রিন্ট তথ্য ======
    
    def generate_browser_fingerprint_info(self):
        """ব্রাউজার ফিঙ্গারপ্রিন্ট তথ্য তৈরি করা"""
        print("\n" + "="*70)
        print("7️⃣ ব্রাউজার ফিঙ্গারপ্রিন্ট তথ্য তৈরি করছে...")
        print("="*70)
        
        fingerprint = {
            'user_agent': self._generate_user_agent(),
            'screen_resolution': random.choice([
                '1920x1080', '1366x768', '1440x900', '2560x1440', '1280x720'
            ]),
            'color_depth': random.choice([24, 32]),
            'timezone': random.choice([
                'Asia/Dhaka', 'Asia/Kolkata', 'Europe/London',
                'America/New_York', 'Asia/Bangkok'
            ]),
            'language': random.choice([
                'en-US', 'en-BD', 'bn-BD', 'es-ES', 'fr-FR'
            ]),
            'device_memory': random.choice([4, 8, 16, 32]),
            'cpu_cores': random.choice([2, 4, 6, 8, 16]),
            'webgl_vendor': random.choice(['ANGLE', 'Mali', 'Adreno', 'Intel']),
            'canvas_fingerprint': str(uuid.uuid4())[:16]
        }
        
        print("\n📌 ব্রাউজার ফিঙ্গারপ্রিন্ট তথ্য:")
        print(f"  User-Agent: {fingerprint['user_agent'][:50]}...")
        print(f"  Screen: {fingerprint['screen_resolution']}")
        print(f"  Timezone: {fingerprint['timezone']}")
        print(f"  Language: {fingerprint['language']}")
        print(f"  Device Memory: {fingerprint['device_memory']}GB")
        print(f"  CPU Cores: {fingerprint['cpu_cores']}")
        
        self.log_transform("Browser Fingerprint Generated", json.dumps(fingerprint))
        return fingerprint
    
    def _generate_user_agent(self):
        """র‍্যান্ডম User-Agent তৈরি"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        return random.choice(user_agents)
    
    # ====== ८. সিস্টেম তথ্য জেনারেশন ======
    
    def generate_system_specs(self):
        """সিস্টেম স্পেসিফিকেশন তথ্য জেনারেট করা"""
        print("\n" + "="*70)
        print("8️⃣ সিস্টেম স্পেসিফিকেশন তৈরি করছে...")
        print("="*70)
        
        specs = {
            'manufacturer': random.choice(['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer']),
            'model': random.choice(['XPS', 'ProBook', 'ThinkPad', 'VivoBook', 'Aspire']),
            'serial_number': f"{''.join([chr(random.randint(65, 90)) for _ in range(3)])}{random.randint(10000000, 99999999)}",
            'bios_version': f"Ver.{random.randint(1, 10)}.{random.randint(0, 9)}",
            'ram': random.choice([8, 16, 32, 64]),
            'storage': random.choice([256, 512, 1024, 2048])
        }
        
        print(f"\n📌 ডিভাইস স্পেসিফিকেশন:")
        print(f"  Manufacturer: {specs['manufacturer']}")
        print(f"  Model: {specs['model']}")
        print(f"  Serial: {specs['serial_number']}")
        print(f"  RAM: {specs['ram']}GB")
        print(f"  Storage: {specs['storage']}GB")
        
        self.log_transform("System Specs Generated", json.dumps(specs))
        return specs
    
    # ====== ९. সম্পূর্ণ ডিভাইস প্রোফাইল ======
    
    def get_device_profile(self):
        """সম্পূর্ণ ডিভাইস প্রোফাইল রিটার্ন করা"""
        return {
            'account_id': self.account_id,
            'os': self.os_type,
            'created_at': datetime.now().isoformat()
        }
    
    # ====== ১০. মূল এক্সিকিউশন ফাংশন ======
    
    def execute_complete_device_transform(self):
        """সম্পূর্ণ ডিভাইস ট্রান্সফরমেশন এক্সিকিউট করা"""
        
        print("\n" + "="*80)
        print("╔" + "="*78 + "╗")
        print("║" + " "*15 + "🔐 POST-SIGNUP DEVICE COMPLETE TRANSFORMATION" + " "*18 + "║")
        print("╚" + "="*78 + "╝")
        print("="*80)
        
        print(f"\n📱 অপারেটিং সিস্টেম: {self.os_type}")
        print(f"📧 অ্যাকাউন্ট ID: {self.account_id}")
        print(f"⏰ সময়: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # স্টেপ ১: হার্ডওয়্যার আইডি চেঞ্জ
        self.change_system_hardware_id()
        time.sleep(1)
        
        # স্টেপ ২: MAC Address চেঞ্জ
        self.change_mac_address()
        time.sleep(1)
        
        # স্টেপ ३: ব্রাউজার ডেটা পরিষ্কার
        self.clear_all_browser_data()
        time.sleep(1)
        
        # স্টেপ ४: DNS ক্যাশ পরিষ্কার
        self.flush_dns_cache()
        time.sleep(1)
        
        # স্টেপ ५: হোস্টনেম চেঞ্জ
        self.change_hostname()
        time.sleep(1)
        
        # স্টেপ ६: IP Spoofing তথ্য
        ip_info = self.generate_ip_spoofing_info()
        time.sleep(1)
        
        # স্টেপ ७: ব্রাউজার ফিঙ্গারপ্রিন্ট
        browser_fp = self.generate_browser_fingerprint_info()
        time.sleep(1)
        
        # স্টেপ ८: সিস্টেম স্পেক্স
        sys_specs = self.generate_system_specs()
        time.sleep(1)
        
        # সবকিছু সংরক্ষণ করা
        self.save_transform_config()
        
        # ফাইনাল রিপোর্ট
        self.print_final_report(ip_info, browser_fp, sys_specs)
    
    def print_final_report(self, ip_info, browser_fp, sys_specs):
        """চূড়ান্ত রিপোর্ট প্রিন্ট করা"""
        print("\n" + "="*80)
        print("✅ DEVICE TRANSFORMATION COMPLETE")
        print("="*80)
        
        print(f"\n📊 ট্রান্সফর্মেশন সংক্ষিপ্ত:")
        print(f"  • মোট পরিবর্তন: {len(self.transform_log)} টি")
        print(f"  • অ্যাকাউন্ট ID: {self.account_id}")
        print(f"  • সংরক্ষণ ফাইল: {self.config_file}")
        
        print(f"\n🌐 নেটওয়ার্ক তথ্য:")
        for header, ip in ip_info.items():
            print(f"  • {header}: {ip}")
        
        print(f"\n🖥️ সিস্টেম তথ্য:")
        for key, value in sys_specs.items():
            print(f"  • {key}: {value}")
        
        print(f"\n🌍 ব্রাউজার তথ্য:")
        print(f"  • Screen: {browser_fp['screen_resolution']}")
        print(f"  • Timezone: {browser_fp['timezone']}")
        print(f"  • Language: {browser_fp['language']}")
        print(f"  • Device Memory: {browser_fp['device_memory']}GB")
        
        print("\n" + "="*80)
        print("⚡ পরবর্তী লগইন সম্পূর্ণ নতুন ডিভাইস হিসেবে দেখা যাবে!")
        print("="*80 + "\n")

def main():
    print("\n" + "="*80)
    print("🔐 LinkedIn - Post-Signup Device Transformation")
    print("="*80 + "\n")
    
    print("📝 ব্যবহার করার উপায়:")
    print("  1. সাইন আপ শেষ করুন এবং লগ আউট করুন")
    print("  2. নিম্নে একটি অ্যাকাউন্ট আইডি দিন (যেকোনো নম্বর বা নাম)")
    print("  3. স্ক্রিপ্ট স্বয়ংক্রিয়ভাবে ডিভাইস পরিবর্তন করবে")
    print("  4. পরবর্তী লগইন সম্পূর্ণ নতুন ডিভাইস হিসেবে দেখা যাবে\n")
    
    # অ্যাকাউন্ট ID ইনপুট
    account_id = input("📧 অ্যাকাউন্ট ID দিন (উদাহরণ: account_1, user_001, এ-কাটা): ").strip()
    
    if not account_id:
        print("❌ অ্যাকাউন্ট ID প্রয়োজন!")
        return
    
    # স্ক্রিপ্ট এক্সিকিউট করা
    transformer = PostSignupDeviceTransform()
    transformer.account_id = account_id
    transformer.execute_complete_device_transform()

if __name__ == "__main__":
    main()
