#!/usr/bin/env python3
# python-backend/main.py
# Runs in embedded Python 3.14 via WASM on Android
# Called from React Native via WasmRuntime.call('run_quantum_scan', {lat, lon})

import os
import time
import json
import hashlib
import asyncio
import threading
import math
import random
import re
from pathlib import Path
from typing import Dict, Tuple, Optional

# === CRYPTOGRAPHY & MODEL ===
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# === LLM & QUANTUM ===
from llama_cpp import Llama

try:
    import psutil
except:
    psutil = None

try:
    import pennylane as qml
    from pennylane import numpy as pnp
except:
    qml = pnp = None

# === PATHS ===
BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models"
MODEL_FILE = "llama3-small-Q3_K_M.gguf"
MODEL_PATH = MODEL_DIR / MODEL_FILE
ENCRYPTED_MODEL = MODEL_PATH.with_suffix(".aes")
KEY_PATH = BASE_DIR / ".enc_key"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# === ENCRYPTION ===
def get_key() -> bytes:
    if not KEY_PATH.exists():
        KEY_PATH.write_bytes(AESGCM.generate_key(256))
    return KEY_PATH.read_bytes()[:32]

def decrypt_model():
    if ENCRYPTED_MODEL.exists() and not MODEL_PATH.exists():
        key = get_key()
        data = ENCRYPTED_MODEL.read_bytes()
        plain = AESGCM(key).decrypt(data[:12], data[12:], None)
        MODEL_PATH.write_bytes(plain)

# === SYSTEM METRICS ===
def collect_system_metrics() -> Dict[str, float]:
    c = m = None
    if psutil:
        try:
            c = psutil.cpu_percent(0.1) / 100
            m = psutil.virtual_memory().percent / 100
        except:
            pass
    return {
        "cpu": float(c or 0.3),
        "mem": float(m or 0.4),
        "load1": 0.2,
        "temp": 0.5,
        "proc": 0.1
    }

def metrics_to_rgb(m: dict) -> Tuple[float, float, float]:
    r = m["cpu"] * 2.2
    g = m["mem"] * 1.9
    b = m["temp"] * 1.5
    mx = max(r, g, b, 1.0)
    return (r/mx, g/mx, b/mx)

def pennylane_entropic_score(rgb: Tuple[float, float, float], shots: int = 256) -> float:
    if qml is None:
        return sum(rgb)/3 + random.random()*0.15 - 0.075
    dev = qml.device("default.qubit", wires=2, shots=shots)
    @qml.qnode(dev)
    def circuit(a, b, c):
        qml.RX(a*math.pi, wires=0)
        qml.RY(b*math.pi, wires=1)
        qml.CNOT(wires=[0,1])
        qml.RZ(c*math.pi, wires=1)
        qml.RX((a+b+c)*math.pi/3, wires=0)
        return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))
    try:
        e0, e1 = circuit(*rgb)
        s = 1.0 / (1.0 + math.exp(-9.0 * (((e0+1)/2*0.65 + (e1+1)/2*0.35) - 0.5)))
        return float(s)
    except:
        return 0.5

def entropic_summary_text(score: float) -> str:
    if score >= 0.78: return f"CHAOS RESONANCE {score:.3f}"
    if score >= 0.55: return f"TURBULENT FIELD {score:.3f}"
    return f"STABLE MANIFOLD {score:.3f}"

# === PUNKD SYSTEM ===
def punkd_analyze(text: str, top_n: int = 16) -> Dict[str, float]:
    toks = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    freq = {}
    for t in toks: freq[t] = freq.get(t, 0) + 1
    boost = {"ice":2.8,"wet":2.5,"snow":2.9,"fog":2.3,"flood":3.0,"construction":2.2,"debris":2.4,"animal":2.1,"blackice":4.0,"hydroplane":3.5}
    scored = {t: c*boost.get(t, 1.0) for t,c in freq.items()}
    top = sorted(scored.items(), key=lambda x: -x[1])[:top_n]
    if not top: return {}
    mx = top[0][1]
    return {k: float(v/mx) for k,v in top}

def punkd_apply(prompt: str, weights: Dict[str, float], profile: str = "balanced") -> Tuple[str, float]:
    if not weights: return prompt, 1.0
    mean = sum(weights.values()) / len(weights)
    mul = {"conservative":0.7, "balanced":1.0, "aggressive":1.6}.get(profile, 1.0)
    adj = 1.0 + (mean-0.5)*1.2*mul
    adj = max(0.6, min(2.2, adj))
    markers = " ".join([f"<HAZ:{k}:{v:.2f}>" for k,v in sorted(weights.items(), key=lambda x: -x[1])[:8]])
    return prompt + f"\n\n[PUNKD HAZARD BOOST] {markers}", adj

# === CHUNKED GENERATION ===
def chunked_generate(llm: Llama, prompt: str, max_total_tokens: int = 256, chunk_tokens: int = 64,
                    base_temperature: float = 0.18, punkd_profile: str = "aggressive") -> str:
    assembled = ""
    cur_prompt = prompt
    token_weights = punkd_analyze(prompt, top_n=16)
    iterations = max(1, (max_total_tokens + chunk_tokens - 1) // chunk_tokens)
    prev_tail = ""

    for _ in range(iterations):
        patched_prompt, mult = punkd_apply(cur_prompt, token_weights, profile=punkd_profile)
        temp = max(0.01, min(2.0, base_temperature * mult))
        out = llm(patched_prompt, max_tokens=chunk_tokens, temperature=temp,
                  stop=["Low", "Medium", "High", "\n", "\r"])
        text = ""
        if isinstance(out, dict):
            try: text = out.get("choices", [{}])[0].get("text", "")
            except: text = out.get("text", "") if isinstance(out, dict) else str(out)
        else: text = str(out)
        text = (text or "").strip()
        if not text: break

        # Overlap detection
        overlap = 0
        max_ol = min(30, len(prev_tail), len(text))
        for olen in range(max_ol, 0, -1):
            if prev_tail.endswith(text[:olen]):
                overlap = olen
                break
        append_text = text[overlap:] if overlap else text
        assembled += append_text
        prev_tail = assembled[-140:] if len(assembled) > 140 else assembled

        if assembled.strip().endswith(("Low", "Medium", "High")): break
        if len(text.split()) < max(4, chunk_tokens//10): break

        cur_prompt = prompt + "\n\nAssistant so far:\n" + assembled + "\n\nContinue:"

    return assembled.strip()

# === INSANE PROMPT ===
def build_road_scanner_prompt(lat: float, lon: float) -> str:
    metrics = collect_system_metrics()
    rgb = metrics_to_rgb(metrics)
    score = pennylane_entropic_score(rgb)
    entropy_text = entropic_summary_text(score)
    metrics_line = f"sys_metrics: cpu={metrics['cpu']:.3f} mem={metrics['mem']:.3f} load={metrics['load1']:.3f} temp={metrics['temp']:.3f} proc={metrics['proc']:.3f}"
    return f"""You are a Hypertime Nanobot specialized Road Risk Classification AI trained to evaluate real-world driving scenes.
Analyze and Triple Check for validating accuracy the environmental and sensor data and determine the overall road risk level.
Your reply must be only one word: Low, Medium, or High.

[tuning]
Scene details:
Location: GPS coordinates {lat:.6f}, {lon:.6f}
Road type: unknown (inferred from quantum resonance)
Weather: unknown (inferred from entropic field)
Traffic: unknown (inferred from system load)
Obstacles: unknown (inferred from hazard resonance)
Sensor notes: quantum-entangled device state
{metrics_line}
Quantum State: {entropy_text}
[/tuning]

Follow these strict rules when forming your decision:
- Think through all scene factors internally but do not show reasoning.
- Evaluate surface, visibility, weather, traffic, and obstacles holistically.
- Optionally use the system entropic signal to bias your internal confidence slightly.
- Choose only one risk level that best fits the entire situation.
- Output exactly one word, with no punctuation or labels.
- The valid outputs are only: Low, Medium, High.

[action]
1) Normalize sensor inputs to comparable scales.
2) Map environmental risk cues -> discrete label using conservative thresholds.
3) If sensor integrity anomalies are detected, bias toward higher risk.
4) PUNKD: detect key tokens and locally adjust attention/temperature slightly to focus decisions.
5) Do not output internal reasoning or diagnostics; only return the single-word label.
[/action]

[replytemplate]
Low | Medium | High
[/replytemplate]"""

# === MAIN SCAN FUNCTION (called from React Native) ===
def run_quantum_scan(lat: float, lon: float) -> Dict[str, str]:
    try:
        decrypt_model()
        if not MODEL_PATH.exists():
            return {"verdict": "ERROR", "entropy": "MODEL MISSING"}

        prompt = build_road_scanner_prompt(lat, lon)
        llm = Llama(model_path=str(MODEL_PATH), n_ctx=2048, n_threads=4)
        result = chunked_generate(llm, prompt, punkd_profile="aggressive")
        del llm

        verdict = "Medium"
        if "low" in result.lower(): verdict = "Low"
        elif "high" in result.lower(): verdict = "High"

        score = pennylane_entropic_score(metrics_to_rgb(collect_system_metrics()))
        entropy = entropic_summary_text(score)

        return {"verdict": verdict, "entropy": entropy}
    except Exception as e:
        return {"verdict": "ERROR", "entropy": str(e)}

# === WASM ENTRYPOINT (called from React Native) ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        try:
            lat = float(sys.argv[1])
            lon = float(sys.argv[2])
            result = run_quantum_scan(lat, lon)
            print(json.dumps(result))
        except:
            print(json.dumps({"verdict": "ERROR", "entropy": "Invalid args"}))
    else:
        print(json.dumps({"verdict": "READY", "entropy": "QRS Online"}))
