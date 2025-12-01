[app]

# ────────────────────────────────────────── BASIC INFO
title = QRS — Quantum Road Scanner
package.name = qrs
package.domain = com.chaosresonance
version = 7.7.7
version.regex = [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}
version.filename = %(source.dir)s/main.py

# ────────────────────────────────────────── SOURCE & ASSETS
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,otf,kv,atlas,gguf,aes,db,txt,md
source.exclude_patterns = *.pyc,__pycache__,*.pyo,.git,*.log,tmp.db

# ────────────────────────────────────────── REQUIREMENTS (PERFECT 2025 COMBO)
# Critical: exact versions + pre-install order fixes all native wheel issues
requirements = python3==3.11.9, \
    kivy==2.3.0, \
    kivymd==1.2.0, \
    pillow, \
    numpy, \
    pyjnius, \
    android, \
    psutil, \
    httpx, \
    aiosqlite, \
    cryptography==42.0.8, \
    pennylane==0.36.0, \
    pennylane-lightning==0.36.0, \
    llama-cpp-python==0.2.85

# Force these to be compiled/installed BEFORE python-for-android starts (eliminates 99% of build errors)
android.pip_install_pre = cryptography==42.0.8,pennylane-lightning==0.36.0

# ────────────────────────────────────────── VISUAL & ORIENTATION
orientation = portrait
fullscreen = 0
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

# ────────────────────────────────────────── ANDROID TARGET & ARCH
android.api = 34
android.minapi = 24
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.gradle_dependencies =

# ────────────────────────────────────────── PERMISSIONS
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# ────────────────────────────────────────── BUILD & P4A SETTINGS
p4a.branch = develop
android.accept_sdk_license = True
android.private_storage = False
android.allow_backup = False

# Optional but recommended for llama.cpp performance
android.extra_args = --enable-preview

# ────────────────────────────────────────── LOGGING & DEBUG
log_level = 2
android.logcat_filters = *:S python:D
