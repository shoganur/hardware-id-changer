@echo off
REM =====================================================
REM LinkedIn Device Transformer - Automatic Setup
REM প্রথমবার চালানোর জন্য সেটআপ স্ক্রিপ্ট
REM =====================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

cls
echo.
echo ============================================================
echo.
echo   🔐 LinkedIn Device Transformer - Automatic Setup
echo.
echo ============================================================
echo.

REM =====================================================
REM ১. Python চেক করা
REM =====================================================

echo [1/4] Python চেক করছে...
python --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo ❌ Python ইনস্টল করা নেই!
    echo.
    echo 📥 Python ডাউনলোড করছে...
    echo.
    
    REM Python ডাউনলোড এবং ইনস্টল করা
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

echo [2/4] প্রয়োজনীয় প্যাকেজ ইনস্টল করছে...
echo.

python -m pip install --upgrade pip >nul 2>&1
python -m pip install selenium webdriver-manager fake-useragent >nul 2>&1

if errorlevel 1 (
    echo.
    echo ⚠️ প্যাকেজ ইনস্টল করতে ইন্টারনেট সংযোগ প্রয়োজন
    echo ⚠️ আবার চেষ্টা করুন: python -m pip install selenium webdriver-manager fake-useragent
    pause
    exit /b 1
) else (
    echo ✓ সব প্যাকেজ ইনস্টল হয়েছে
)

echo.

REM =====================================================
REM ३. স্ক্রিপ্ট ডাউনলোড করা
REM =====================================================

echo [3/4] স্ক্রিপ্ট ডাউনলোড/যাচাই করছে...

if not exist "post_signup_device_transform.py" (
    echo ⬇️ GitHub থেকে স্ক্রিপ্ট ডাউনলোড করছে...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://raw.githubusercontent.com/shoganur/hardware-id-changer/main/post_signup_device_transform.py', 'post_signup_device_transform.py')}"
    
    if exist "post_signup_device_transform.py" (
        echo ✓ স্ক্রিপ্ট ডাউনলোড সম্পন্ন
    ) else (
        echo ❌ স্ক্রিপ্ট ডাউনলোড ব্যর্থ
        pause
        exit /b 1
    )
) else (
    echo ✓ স্ক্রিপ্ট পাওয়া গেছে
)

echo.

REM =====================================================
REM ४. স্ক্রিপ্ট চালানো
REM =====================================================

echo [4/4] স্ক্রিপ্ট চালু করছে...
echo.
echo ============================================================
echo.

python post_signup_device_transform.py

echo.
echo ============================================================
echo ✓ সেশন সম্পন্ন হয়েছে
echo ============================================================
echo.

pause
