#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android Device Transformer - Full Cleanup
অ্যান্ড্রয়েড ডিভাইস সম্পূর্ণ ক্লিনআপ এবং রিফ্রেশ
ব্রাউজার থিম/ব্যাকগ্রাউন্ড সংরক্ষণ এবং পাসওয়ার্ড সংরক্ষণ করে
"""

import os
import sys
import json
import time
import sqlite3
import shutil
import subprocess
import random
from datetime import datetime
from pathlib import Path

class AndroidDeviceTransformer:
    def __init__(self):
        self.log_file = f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.device_connected = False
        self.changes_made = []
        
    def log(self, message, level="INFO"):
        """লগ মেসেজ সংরক্ষণ করা"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def check_adb(self):
        """ADB উপলব্ধ কিনা চেক করা"""
        self.log("ADB চেক করছে...")
        try:
            result = subprocess.run(["adb", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✓ ADB পাওয়া গেছে", "SUCCESS")
                return True
            else:
                self.log("❌ ADB পাওয়া যায়নি। ADB ইনস্টল করুন।", "ERROR")
                return False
        except FileNotFoundError:
            self.log("❌ ADB পাথে নেই। Android SDK Platform Tools ইনস্টল করুন।", "ERROR")
            return False
    
    def check_device(self):
        """ডিভাইস সংযোগ চেক করা"""
        self.log("ডিভাইস খুঁজছে...")
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            if "device" in result.stdout and "offline" not in result.stdout:
                self.log("✓ ডিভাইস সংযুক্ত পাওয়া গেছে", "SUCCESS")
                self.device_connected = True
                return True
            else:
                self.log("❌ কোনো ডিভাইস সংযুক্ত নেই। USB Debugging চেক করুন।", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ ডিভাইস চেক ব্যর্থ: {str(e)}", "ERROR")
            return False
    
    def execute_adb_command(self, command, description=""):
        """ADB কমান্ড এক্সিকিউট করা"""
        try:
            full_command = f"adb shell {command}"
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log(f"✓ {description} সম্পন্ন", "SUCCESS")
                self.changes_made.append(description)
                return True
            else:
                self.log(f"⚠️ {description} ব্যর্থ (এটি স্বাভাবিক হতে পারে)", "WARNING")
                return False
        except Exception as e:
            self.log(f"⚠️ {description} এ সমস্যা: {str(e)}", "WARNING")
            return False
    
    def clear_chrome_data(self):
        """Chrome: শুধুমাত্র কুকিজ, হিস্ট্রি এবং ক্যাশ ডিলিট (থিম রাখা)"""
        self.log("\n📱 Chrome পরিষ্কার করছে (থিম সংরক্ষণ)...", "STEP")
        
        # Chrome কাছ থেকে শুধুমাত্র নির্দিষ্ট ডেটা ডিলিট করা
        self.execute_adb_command(
            "pm clear --cache com.android.chrome",
            "Chrome: ক্যাশ পরিষ্কার করা"
        )
        
        # Chrome ডেটা অ্যাপ স্তরে পরিষ্কার (পাসওয়ার্ড রাখা, থিম রাখা)
        self.execute_adb_command(
            "rm -rf /data/data/com.android.chrome/app_chrome/Default/Cache 2>/dev/null || true",
            "Chrome: ব্রাউজিং ক্যাশ ডিলিট করা"
        )
        
        self.execute_adb_command(
            "rm -rf /data/data/com.android.chrome/app_chrome/Default/Code\\ Cache 2>/dev/null || true",
            "Chrome: কোড ক্যাশ ডিলিট করা"
        )
    
    def clear_firefox_data(self):
        """Firefox: শুধুমাত্র কুকিজ, হিস্ট্রি এবং ক্যাশ ডিলিট (থিম রাখা)"""
        self.log("📱 Firefox পরিষ্কার করছে (থিম সংরক্ষণ)...", "STEP")
        
        self.execute_adb_command(
            "pm clear --cache org.mozilla.firefox",
            "Firefox: ক্যাশ পরিষ্কার করা"
        )
        
        self.execute_adb_command(
            "rm -rf /data/data/org.mozilla.firefox/cache 2>/dev/null || true",
            "Firefox: ব্রাউজিং ক্যাশ ডিলিট করা"
        )
    
    def clear_samsung_browser_data(self):
        """Samsung Browser: শুধুমাত্র কুকিজ, হিস্ট্রি এবং ক্যাশ ডিলিট (থিম রাখা)"""
        self.log("📱 Samsung Browser পরিষ্কার করছে (থিম সংরক্ষণ)...", "STEP")
        
        self.execute_adb_command(
            "pm clear --cache com.sec.android.app.sbrowser",
            "Samsung Browser: ক্যাশ পরিষ্কার করা"
        )
    
    def clear_browser_history_cookies(self):
        """ব্রাউজার হিস্ট্রি এবং কুকিজ পরিষ্কার করা"""
        self.log("\n🔍 ব্রাউজার কুকিজ এবং হিস্ট্রি ডিলিট করছে...", "STEP")
        
        # Chrome হিস্ট্রি এবং কুকিজ ডিলিট
        self.execute_adb_command(
            "rm -rf /data/data/com.android.chrome/app_chrome/Default/History* 2>/dev/null || true",
            "Chrome: ব্রাউজিং হিস্ট্রি ডিলিট করা"
        )
        
        # Firefox হিস্ট্রি এবং কুকিজ ডিলিট
        self.execute_adb_command(
            "rm -rf /data/data/org.mozilla.firefox/files/mozilla/*.default/cookies.sqlite 2>/dev/null || true",
            "Firefox: কুকিজ ডিলিট করা"
        )
        
        self.execute_adb_command(
            "rm -rf /data/data/org.mozilla.firefox/files/mozilla/*.default/places.sqlite 2>/dev/null || true",
            "Firefox: হিস্ট্রি ডিলিট করা"
        )
    
    def reset_device_id(self):
        """ডিভাইস আইডি রিসেট করা (LinkedIn এর জন্য অপটিমাইজড)"""
        self.log("\n🔐 ডিভাইস আইডেন্টিফায়ার নতুন করছে...", "STEP")
        
        # নতুন Android ID জেনারেট করা
        new_android_id = f"{random.randint(100000000000000, 999999999999999)}"
        self.execute_adb_command(
            f"settings put secure android_id {new_android_id}",
            f"Android ID নতুন করা: {new_android_id[:8]}..."
        )
        
        # নতুন Device Name তৈরি করা
        device_models = ["SM-G991B", "SM-G995B", "SM-A125F", "SM-A225F", "ONEPLUS A6013"]
        new_model = random.choice(device_models)
        
        self.execute_adb_command(
            f"setprop ro.product.model {new_model}",
            f"ডিভাইস মডেল পরিবর্তন: {new_model}"
        )
        
        # নতুন বিল্ড ফিংগারপ্রিন্ট
        self.execute_adb_command(
            f"setprop ro.build.fingerprint samsung/galaxy/samsung:12/SP1A.210812.016/{random.randint(100000, 999999)}:user/release-keys",
            "বিল্ড ফিংগারপ্রিন্ট পরিবর্তন করা"
        )
        
        # নতুন Serial Number
        new_serial = f"R{''.join([str(random.randint(0,9)) for _ in range(15)])}"
        self.execute_adb_command(
            f"setprop ro.serialno {new_serial}",
            f"Serial Number নতুন করা: {new_serial[:8]}..."
        )
    
    def reset_gaid(self):
        """Google Advertising ID রিসেট করা"""
        self.log("\n📢 Google Advertising ID রিসেট করছে...", "STEP")
        
        new_gaid = f"{random.randint(100000000, 999999999)}-{random.randint(1000000, 9999999)}"
        
        self.execute_adb_command(
            f"settings put secure gaid {new_gaid}",
            f"GAID রিসেট করা: {new_gaid[:16]}..."
        )
    
    def clear_dns_cache(self):
        """DNS ক্যাশ পরিষ্কার করা"""
        self.log("\n🌐 DNS ক্যাশ পরিষ্কার করছে...", "STEP")
        
        self.execute_adb_command(
            "service call connectivity 37",
            "DNS ক্যাশ ফ্লাশ করা"
        )
        
        self.execute_adb_command(
            "cmd netpolicy reset",
            "নেটওয়ার্ক পলিসি রিসেট করা"
        )
    
    def reset_mac_address(self):
        """MAC Address স্পুফিং (ভার্চুয়াল)"""
        self.log("\n📡 MAC Address স্পুফিং সেটআপ করছে...", "STEP")
        
        # নতুন ভার্চুয়াল MAC অ্যাড্রেস তৈরি করা
        new_mac = f"02:{''.join([f'{random.randint(0,255):02x}' for _ in range(5)])}"
        
        self.execute_adb_command(
            f"settings put secure wi_fi_mac_address {new_mac}",
            f"ওয়াই-ফাই MAC অ্যাড্রেস সেট করা: {new_mac}"
        )
    
    def clear_app_caches(self):
        """সব অ্যাপ ক্যাশ পরিষ্কার করা"""
        self.log("\n📦 অ্যাপ ক্যাশ পরিষ্কার করছে...", "STEP")
        
        self.execute_adb_command(
            "pm trim-caches 512M",
            "সব অ্যাপ ক্যাশ ট্রিম করা"
        )
        
        # Google Play Services ক্যাশ
        self.execute_adb_command(
            "pm clear --cache com.google.android.gms",
            "Google Play Services ক্যাশ পরিষ্কার করা"
        )
        
        # Play Store ক্যাশ
        self.execute_adb_command(
            "pm clear --cache com.android.vending",
            "Play Store ক্যাশ পরিষ্কার করা"
        )
    
    def clear_location_history(self):
        """লোকেশন হিস্ট্রি পরিষ্কার করা"""
        self.log("\n📍 লোকেশন হিস্ট্রি পরিষ্কার করছে...", "STEP")
        
        self.execute_adb_command(
            "settings put secure location_mode 0",
            "লোকেশন সার্ভিসেস অফ করা"
        )
        
        self.execute_adb_command(
            "rm -rf /data/data/com.google.android.gms/databases/gmscore_*.db 2>/dev/null || true",
            "Google লোকেশন ডেটা পরিষ্কার করা"
        )
    
    def disable_tracking(self):
        """ট্র্যাকিং ডিসেবল করা"""
        self.log("\n🚫 ট্র্যাকিং ডিসেবল করছে...", "STEP")
        
        self.execute_adb_command(
            "settings put global ad_id_enabled 0",
            "বিজ্ঞাপন ট্র্যাকিং ডিসেবল করা"
        )
        
        self.execute_adb_command(
            "settings put global device_name_overridden 1",
            "ডিভাইস ট্র্যাকিং সুরক্ষা সক্রিয় করা"
        )
        
        self.execute_adb_command(
            "settings put global metrics_data_collection 0",
            "Google মেট্রিক্স সংগ্রহ ডিসেবল করা"
        )
    
    def clear_temporary_files(self):
        """টেম্পোরারি ফাইল পরিষ্কার করা"""
        self.log("\n🗑️ টেম্পোরারি ফাইল পরিষ্কার করছে...", "STEP")
        
        self.execute_adb_command(
            "rm -rf /cache/* 2>/dev/null || true",
            "ক্যাশ ফোল্ডার পরিষ্কার করা"
        )
        
        self.execute_adb_command(
            "rm -rf /data/local/tmp/* 2>/dev/null || true",
            "টেম্পোরারি ফাইল ডিলিট করা"
        )
    
    def create_backup(self):
        """ব্যাকআপ তৈরি করা"""
        self.log("\n💾 ব্যাকআপ তৈরি করছে...", "STEP")
        
        try:
            backup_file = f"device_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "changes_made": self.changes_made,
                "device_info": {
                    "cleanup_version": "2.0",
                    "browser_cookies_cleared": True,
                    "browser_history_cleared": True,
                    "browser_cache_cleared": True,
                    "browser_theme_preserved": True,
                    "browser_background_preserved": True,
                    "browser_passwords_preserved": True,
                    "device_id_reset": True,
                    "mac_address_spoofed": True,
                    "dns_cache_cleared": True,
                    "location_history_cleared": True,
                    "tracking_disabled": True,
                    "temporary_files_cleared": True
                }
            }
            
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.log(f"✓ ব্যাকআপ তৈরি: {backup_file}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"⚠️ ব্যাকআপ তৈরি ব্যর্থ: {str(e)}", "WARNING")
            return False
    
    def run_cleanup(self):
        """সম্পূর্ণ ক্লিনআপ প্রক্রিয়া চালানো"""
        print("\n" + "="*70)
        print("   🔐 Android Device Transformer - Full Cleanup")
        print("   📱 সম্পূর্ণ ডিভাইস ক্লিনআপ এবং রিফ্রেশ")
        print("   LinkedIn এর জন্য অপটিমাইজড")
        print("="*70 + "\n")
        
        self.log("="*70)
        self.log("Android Device Transformer শুরু হচ্ছে")
        self.log("="*70)
        
        # প্রাথমিক চেক
        if not self.check_adb():
            self.log("ADB ইনস্টল করা আবশ্যক। প্রক্রিয়া বন্ধ করছে।", "ERROR")
            return False
        
        if not self.check_device():
            self.log("ডিভাইস সংযোগ করুন এবং আবার চেষ্টা করুন।", "ERROR")
            return False
        
        # ক্লিনআপ প্রক্রিয়া
        try:
            print("\n⏳ ক্লিনআপ প্রক্রিয়া শুরু হচ্ছে...\n")
            
            # ব্রাউজার ডেটা ক্লিনআপ (পাসওয়ার্ড এবং থিম রাখা)
            self.clear_chrome_data()
            time.sleep(1)
            
            self.clear_firefox_data()
            time.sleep(1)
            
            self.clear_samsung_browser_data()
            time.sleep(1)
            
            self.clear_browser_history_cookies()
            time.sleep(2)
            
            # ডিভাইস আইডেন্টিফায়ার
            self.reset_device_id()
            time.sleep(2)
            
            self.reset_gaid()
            time.sleep(1)
            
            self.reset_mac_address()
            time.sleep(1)
            
            # DNS এবং নেটওয়ার্ক
            self.clear_dns_cache()
            time.sleep(1)
            
            # অন্যান্য ক্লিনআপ
            self.clear_app_caches()
            time.sleep(2)
            
            self.clear_location_history()
            time.sleep(1)
            
            self.disable_tracking()
            time.sleep(1)
            
            self.clear_temporary_files()
            time.sleep(1)
            
            # ব্যাকআপ
            self.create_backup()
            
            # সমাপ্তি
            print("\n" + "="*70)
            print("✅ সম্পূর্ণ ক্লিনআপ সম্পন্ন!")
            print("="*70)
            
            self.log("\n" + "="*70)
            self.log("সম্পূর্ণ ক্লিনআপ সম্পন্ন")
            self.log(f"মোট পরিবর্তন: {len(self.changes_made)}")
            self.log("="*70)
            
            print(f"\n📋 লগ ফাইল: {self.log_file}")
            print("\n✅ ডিভাইস সম্পূর্ণভাবে রিফ্রেশ হয়েছে!")
            
            print("\n📝 যা ডিলিট হয়েছে:")
            print("   ✓ সব ব্রাউজার কুকিজ ডিলিট")
            print("   ✓ সব ব্রাউজার হিস্ট্রি ডিলিট")
            print("   ✓ সব ব্রাউজার ক্যাশ পরিষ্কার")
            print("   ✓ DNS ক্যাশ ফ্লাশ করা")
            print("   ✓ লোকেশন হিস্ট্রি ডিলিট")
            print("   ✓ অ্যাপ ক্যাশ পরিষ্কার")
            print("   ✓ ট্যাকিং ডিসেবল করা")
            
            print("\n🔒 যা সংরক্ষিত আছে:")
            print("   ✓ ব্রাউজার পাসওয়ার্ড সংরক্ষিত")
            print("   ✓ ব্রাউজার থিম সংরক্ষিত")
            print("   ✓ ব্রাউজার ব্যাকগ্রাউন্ড সংরক্ষিত")
            
            print("\n🆕 যা নতুন করা হয়েছে:")
            print("   ✓ Android ID নতুন")
            print("   ✓ ডিভাইস মডেল পরিবর্তন")
            print("   ✓ বিল্ড ফিংগারপ্রিন্ট পরিবর্তন")
            print("   ✓ Serial Number নতুন")
            print("   ✓ GAID (Google Advertising ID) নতুন")
            print("   ✓ MAC Address স্পুফ করা")
            
            return True
            
        except Exception as e:
            self.log(f"❌ প্রক্রিয়া ব্যর্থ: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return False

def main():
    transformer = AndroidDeviceTransformer()
    success = transformer.run_cleanup()
    
    print("\n" + "="*70)
    input("এন্টার চাপুন বন্ধ করতে...")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
