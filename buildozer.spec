[app]
title = QRS — Quantum Road Scanner
package.name = qrs
package.domain = com.chaosresonance
version = 7.7.7
android.numeric_version = 777

source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,otf,kv,atlas,gguf,aes,db,txt,md,json,wav
source.exclude_dirs = .git,.buildozer,bin,__pycache__,.github,.venv

# Latest cryptography (unpinned = 42.0.8+) + deps
requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.2.0,numpy,pyjnius,android,psutil,httpx,aiosqlite,cryptography,pennylane==0.36.0,pennylane-lightning==0.36.0,llama-cpp-python==0.2.85

# P4A develop branch: Essential for latest NDK + cryptography extraction
p4a.branch = develop
p4a.fork = kivy

# STRICT 64-bit only
android.archs = arm64-v8a

# LATEST/HIGHER API SETUP (API 35 = Android 15)
android.ndk_api = 35      # Highest supported; modern toolchain, no legacy warnings
android.minapi = 24       # Min supported (Android 7.0; 90%+ device coverage)
android.api = 35          # Target SDK (matches NDK API)
android.sdk = 35          # SDK version
android.ndk = 27          # Latest NDK (r27c; full Rust/Clang support for cryptography)

# Output AAB for Play Store
android.release_artifact = aab

# Permissions & security
android.permissions = ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_DATA_SYNC
android.block_network_permissions = True

# KivyMD + sensor fix
orientation = portrait
fullscreen = 0
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png
android.add_compile_options = -DSDL_SENSOR_DISABLED=1

# Misc
android.accept_sdk_license = True
android.private_storage = False
android.allow_backup = False

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
