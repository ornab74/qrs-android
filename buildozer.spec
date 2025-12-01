[app]

# ────────────────────────────── APP INFO ──────────────────────────────
title = QRS — Quantum Road Scanner
package.name = qrs
package.domain = com.chaosresonance

# Google Play requires numeric versionCode (format: MNN00 for vM.NN)
version = 7.7.7
android.numeric_version = 777

# ─────────────────────────── SOURCE FILES ────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,otf,kv,atlas,gguf,aes,db,txt,md,json,wav
source.exclude_dirs = .git, .buildozer, bin, __pycache__, .github, .venv
source.exclude_patterns = *.pyc, *.pyo, *.log, tmp.db, *.bak

# ─────────────────────────── REQUIREMENTS ────────────────────────────
# Tested combo for Dec 2025 (GitHub Actions + local; avoids numpy/pennylane ARM issues)
requirements = python3==3.11.9,\
kivy==2.3.0,\
kivymd==1.2.0,\
numpy==1.26.4,\
pyjnius,\
android,\
psutil,\
httpx,\
aiosqlite,\
cryptography==42.0.8,\
pennylane==0.36.0,\
pennylane-lightning==0.36.0,\
llama-cpp-python==0.2.85

# Pre-install heavy deps to skip compilation (saves ~20 min)
android.pip_install_pre = cryptography==42.0.8,pennylane-lightning==0.36.0

# ────────────────────────────── VISUAL ───────────────────────────────
orientation = portrait
fullscreen = 0
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

# ───────────────────────── ANDROID TARGET ────────────────────────────
android.api = 35  # Android 15 (required for new Play uploads in 2025)
android.minapi = 24
android.sdk = 35
android.ndk = 27c  # LTS stable (Dec 2025); fixes download errors vs. 25b
android.release_artifact = aab  # Mandatory for Google Play
android.archs = arm64-v8a, armeabi-v7a

# ─────────────────────────── PERMISSIONS ─────────────────────────────
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_DATA_SYNC

# ──────────────────────── BUILDOZER / P4A FIXES ──────────────────────
p4a.branch = develop

# Ignore broken patches (e.g., 3.14_armv7l_fix) for Python 3.11+
p4a.patch_ignore_errors = True
p4a.setup_py_ignore_patch_errors = True

android.accept_sdk_license = True
android.private_storage = False
android.allow_backup = False
android.extra_args = --enable-preview --ignore-setup-py-errors

# ───────────────────────────── LOGGING ───────────────────────────────
log_level = 2
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
