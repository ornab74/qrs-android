[app]

# Title shown on Android home screen & Play Store
title = QRS — Quantum Road Scanner

# Final Play Store package ID → com.chaosresonance.qrs
package.name = qrs
package.domain = com.chaosresonance

# Version in Play Store
version = 7.7.7

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,gguf,aes,db,txt

# Requirements (tested working combo for llama.cpp + pennylane on Android)
requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.2.0,llama-cpp-python==0.2.85,pyjnius,psutil,pennylane,pennylane-lightning,httpx,aiosqlite,cryptography,numpy,pillow,android

# Visuals
orientation = portrait
fullscreen = 0

# Android target
android.api = 34
android.minapi = 24
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE

# Build settings
p4a.branch = develop
android.accept_sdk_license = True
android.private_storage = False

# Optional but recommended
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
