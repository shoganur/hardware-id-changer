import os
import sys
import uuid
import subprocess
import platform
import json
from pathlib import Path
from datetime import datetime

class HardwareIDChanger:
    """কম্পিউটারের হার্ডওয়্যার আইডি এবং MAC অ্যাড্রেস পরিবর্তনের জন্য ক্লাস"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.is_admin = self.check_admin()
        self.backup_file = "hardware_backup.json"
        
    def check_admin(self):
        """Admin/Root অনুমতি চেক করা"""
        try:
            if self.os_type == "Windows":
                import ctypes
                return ctypes.windll.shell.IsUserAnAdmin()
            else:
                return os.getuid() == 0
        except:
            return False
    
    def get_current_hardware_id(self):
        """বর্তমান হার্ডওয়্যার আইডি পাওয়া"""
        try:
            if self.os_type == "Windows":
                result = subprocess.check_output("wmic csproduct get uuid", shell=True)
                uuid_value = result.decode().split('\n')[1].strip()
                return uuid_value
            elif self.os_type == "Linux":
                try:
                    result = subprocess.check_output("dmidecode -s system-uuid", shell=True)
                    return result.decode().strip()
                except:
                    return "পাওয়া যায়নি (root দরকার)"
            elif self.os_type == "Darwin":  # macOS
                result = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID", shell=True)
                return result.decode().strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_mac_addresses(self):
        """সকল MAC অ্যাড্রেস পাওয়া"""
        try:
            if self.os_type == "Windows":
                result = subprocess.check_output("getmac", shell=True)
                return result.decode()
            elif self.os_type == "Linux":
                result = subprocess.check_output("ip link show", shell=True)
                return result.decode()
            elif self.os_type == "Darwin":
                result = subprocess.check_output("ifconfig", shell=True)
                return result.decode()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def backup_current_ids(self):
        """বর্তমান আইডি ব্যাকআপ করা"""
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "hardware_id": self.get_current_hardware_id(),
            "mac_addresses": self.get_mac_addresses(),
            "os": self.os_type
        }
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=4, ensure_ascii=False)
        print(f"✓ ব্যাকআপ সফল: {self.backup_file}")
    
    def generate_new_hardware_id(self):
        """নতুন হার্ডওয়্যার আইডি তৈরি করা"""
        new_id = str(uuid.uuid4()).upper()
        return new_id
    
    def generate_new_mac_address(self):
        """নতুন MAC অ্যাড্রেস তৈরি করা"""
        import random
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))
    
    def change_hardware_id_windows(self, new_id):
        """Windows এ হার্ডওয়্যার আইডি পরিবর্তন"""
        try:
            print("⚠️ Windows এ হার্ডওয়্যার আইডি সরাসরি পরিবর্তন করা যায় না।")
            print("বিকল্প উপায়:")
            print("1. Registry এডিট করুন")
            print("2. Spoofing টুল ব্যবহার করুন")
            print(f"\n📌 নতুন ID: {new_id}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def change_hardware_id_linux(self, interface, new_mac):
        """Linux এ MAC অ্যাড্রেস পরিবর্তন"""
        try:
            if not self.is_admin:
                print("⚠️ Root/Sudo অনুমতি প্রয়োজন!")
                return False
            
            # নেটওয়ার্ক ইন্টারফেস বন্ধ করা
            subprocess.run(f"sudo ifconfig {interface} down", shell=True, check=True)
            print(f"✓ {interface} বন্ধ হয়েছে")
            
            # MAC অ্যাড্রেস পরিবর্তন
            subprocess.run(f"sudo ifconfig {interface} hw ether {new_mac}", shell=True, check=True)
            print(f"✓ MAC অ্যাড্রেস পরিবর্তিত: {new_mac}")
            
            # নেটওয়ার্ক ইন্টারফেস চালু করা
            subprocess.run(f"sudo ifconfig {interface} up", shell=True, check=True)
            print(f"✓ {interface} চালু হয়েছে")
            
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def change_mac_address_with_macchanger(self, interface):
        """macchanger টুল দিয়ে MAC পরিবর্তন (Linux)"""
        try:
            subprocess.run("which macchanger", shell=True, check=True)
            new_mac = self.generate_new_mac_address()
            subprocess.run(f"sudo macchanger -m {new_mac} {interface}", shell=True, check=True)
            print(f"✓ macchanger দিয়ে পরিবর্তিত MAC: {new_mac}")
            return True
        except:
            print("⚠️ macchanger ইনস্টল করুন: sudo apt-get install macchanger")
            return False
    
    def change_hardware_id_macos(self, new_id):
        """macOS এ হার্ডওয়্যার আইডি পরিবর্তন"""
        try:
            print("⚠️ macOS এ সিস্টেম হার্ডওয়্যার আইডি পরিবর্তন করতে:")
            print(f"1. Terminal এ: sudo nvram SystemUUID={new_id}")
            print("2. Reboot করুন")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def restore_from_backup(self):
        """ব্যাকআপ থেকে পুনরুদ্ধার করা"""
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            print("\n✓ ব্যাকআপ তথ্য:")
            print(json.dumps(backup_data, indent=2, ensure_ascii=False))
            return backup_data
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    def show_current_info(self):
        """বর্তমান সিস্টেম তথ্য দেখানো"""
        print("\n" + "="*60)
        print("📊 বর্তমান হার্ডওয়্যার তথ্য")
        print("="*60)
        print(f"অপারেটিং সিস্টেম: {self.os_type}")
        print(f"Admin/Root অনুমতি: {'হ্যাঁ ✓' if self.is_admin else 'না ✗'}")
        print(f"\nহার্ডওয়্যার আইডি:\n{self.get_current_hardware_id()}")
        print(f"\nMAC অ্যাড্রেস:\n{self.get_mac_addresses()}")
        print("="*60 + "\n")
    
    def interactive_menu(self):
        """ইন্টারঅ্যাক্টিভ মেনু"""
        while True:
            print("\n" + "="*60)
            print("🔧 হার্ডওয়্যার আইডি ও MAC অ্যাড্রেস চেঞ্জার")
            print("="*60)
            print("1. বর্তমান তথ্য দেখুন")
            print("2. হার্ডওয়্যার আইডি পরিবর্তন করুন")
            print("3. MAC অ্যাড্রেস পরিবর্তন করুন (Linux)")
            print("4. ব্যাকআপ তৈরি করুন")
            print("5. ব্যাকআপ থেকে পুনরুদ্ধার করুন")
            print("6. নতুন আইডি জেনারেট করুন")
            print("0. বেরিয়ে যান")
            print("="*60)
            
            choice = input("অপশন নির্বাচন করুন (0-6): ").strip()
            
            if choice == "1":
                self.show_current_info()
            
            elif choice == "2":
                if self.os_type == "Windows":
                    new_id = self.generate_new_hardware_id()
                    print(f"\n🆕 নতুন Hardware ID: {new_id}")
                    self.change_hardware_id_windows(new_id)
                elif self.os_type == "Linux":
                    print("Linux সিস্টেম ডিটেক্ট হয়েছে - MAC পরিবর্তন অপশন ব্যবহার করুন")
                elif self.os_type == "Darwin":
                    new_id = self.generate_new_hardware_id()
                    print(f"\n🆕 নতুন Hardware ID: {new_id}")
                    self.change_hardware_id_macos(new_id)
            
            elif choice == "3":
                if self.os_type == "Linux":
                    interfaces = input("নেটওয়ার্ক ইন্টারফেস (eth0/wlan0): ").strip()
                    new_mac = self.generate_new_mac_address()
                    print(f"🆕 নতুন MAC: {new_mac}")
                    self.change_hardware_id_linux(interfaces, new_mac)
                else:
                    print("⚠️ এই ফিচার শুধুমাত্র Linux এ উপলব্ধ")
            
            elif choice == "4":
                self.backup_current_ids()
            
            elif choice == "5":
                self.restore_from_backup()
            
            elif choice == "6":
                print(f"\n🆕 নতুন Hardware ID: {self.generate_new_hardware_id()}")
                print(f"🆕 নতুন MAC Address: {self.generate_new_mac_address()}")
            
            elif choice == "0":
                print("\n✓ প্রোগ্রাম বন্ধ হচ্ছে...")
                break
            
            else:
                print("❌ অবৈধ পছন্দ")

def main():
    print("\n" + "="*60)
    print("⚠️  হার্ডওয়্যার আইডি ও MAC চেঞ্জার - প্রয়োজনীয় নোটিস")
    print("="*60)
    print("এই প্রোগ্রাম হার্ডওয়্যার আইডি পরিবর্তন করে।")
    print("• Windows: Registry এডিট প্রয়োজন")
    print("• Linux: root/sudo অনুমতি প্রয়োজন")
    print("• macOS: sudo অনুমতি প্রয়োজন")
    print("\n⚠️ সতর্কতা: আপনার সিস্টেম রক্ষা করতে পূর্বে ব্যাকআপ তৈরি করুন!")
    print("="*60 + "\n")
    
    changer = HardwareIDChanger()
    
    if not changer.is_admin and changer.os_type in ["Linux", "Darwin"]:
        print("⚠️ সতর্কতা: Admin/Root অনুমতি নেই। কিছু ফিচার কাজ নাও করতে পারে।\n")
    
    changer.interactive_menu()

if __name__ == "__main__":
    main()
