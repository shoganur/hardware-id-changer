@echo off
REM =====================================================
REM Android Device Transformer - Full Cleanup
REM ফোনের সম্পূর্ণ ক্লিনআপ স্ক্রিপ্ট
REM =====================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

cls
echo.
echo ============================================================
echo.
echo   🔐 Android Device Transformer - Full Cleanup
echo   📱 সম্পূর্ণ ডিভাইস ক্লিনআপ এবং রিফ্রেশ
echo.
echo ============================================================
echo.

REM =====================================================
REM ১. Python চেক করা
REM =====================================================

echo [1/5] Python চেক করছে...
python --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo ❌ Python ইনস্টল করা নেই!
    echo.
    echo 📥 Python ডাউনলোড করছে...
    echo.
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe', 'python-installer.exe')}"
    
    if exist python-installer.exe (
        echo ⚙️ Python ইনস্টল করছে...
        python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
        del python-installer.exe
        echo ✓ Python ইনস্টল সম্পন্ন
    ) else (
        echo ⚠️ Python ডাউনলোড ব্যর্থ। ম্যানুয়ালি ইনস্টল করুন: https://python.org
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✓ Python পাওয়া গেছে: !PYTHON_VERSION!
)

echo.

REM =====================================================
REM २. প্যাকেজ ইনস্টল করা
REM =====================================================

echo [2/5] প্রয়োজনীয় প্যাকেজ ইনস্টল করছে...
echo.

python -m pip install --upgrade pip >nul 2>&1
python -m pip install requests ppadb >nul 2>&1

if errorlevel 1 (
    echo.
    echo ⚠️ প্যাকেজ ইনস্টল করতে ইন্টারনেট সংযোগ প্রয়োজন
    echo ⚠️ আবার চেষ্টা করুন: python -m pip install requests ppadb
    pause
    exit /b 1
) else (
    echo ✓ সব প্যাকেজ ইনস্টল হয়েছে
)

echo.

REM =====================================================
REM ३. কনফিগ ফাইল চেক করা
REM =====================================================

echo [3/5] কনফিগ ফাইল যাচাই করছে...

if not exist "cleanup_config.json" (
    echo ⚠️ cleanup_config.json পাওয়া যায়নি
    echo ℹ️ ডিফল্ট কনফিগ ব্যবহার করছে
) else (
    echo ✓ কনফিগ ফাইল পাওয়া গেছে
)

echo.

REM =====================================================
REM ४. স্ক্রিপ্ট ডাউনলোড করা
REM =====================================================

echo [4/5] স্ক্রিপ্ট ডাউনলোড/যাচাই করছে...

if not exist "android_device_transformer.py" (
    echo ⬇️ GitHub থেকে স্ক্রিপ্ট ডাউনলোড করছে...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://raw.githubusercontent.com/shoganur/hardware-id-changer/main/android_device_transformer.py', 'android_device_transformer.py')}"
    
    if exist "android_device_transformer.py" (
        echo ✓ স্ক্রিপ্ট ডাউনলোড সম্পন্ন
    ) else (
        echo ❌ স্ক্রিপ্ট ডাউনলোড ব্যর্থ
        echo ℹ️ অফলাইন মোড চালু করছে...
    )
) else (
    echo ✓ স্ক্রিপ্ট পাওয়া গেছে
)

echo.

REM =====================================================
REM ५. স্ক্রিপ্ট চালানো
REM =====================================================

echo [5/5] স্ক্রিপ্ট চালু করছে...
echo.
echo ============================================================
echo.
echo 📱 নিশ্চিত করুন:
echo    ✓ ফোন USB cable দিয়ে সংযুক্ত আছে
echo    ✓ Developer Mode চালু আছে
echo    ✓ USB Debugging সক্রিয় আছে
echo.
echo ⏳ অপেক্ষা করুন, স্ক্রিপ্ট চালু হচ্ছে...
echo.

python android_device_transformer.py

echo.
echo ============================================================
echo ✓ সেশন সম্পন্ন হয়েছে
echo ============================================================
echo.

pause
