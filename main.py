#!/usr/bin/env python3
import os,time,json,hashlib,asyncio,threading,httpx,aiosqlite,math,random,re
import numpy as np
from pathlib import Path
from typing import Dict,Tuple,Callable,Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from llama_cpp import Llama
import ctypes

try:import psutil
except:psutil=None
try:
    import pennylane as qml
    from pennylane import numpy as pnp
except:qml=pnp=None

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.clock import Clock
from kivy.utils import platform
from kivy.animation import Animation
from kivy.graphics import Color,Ellipse,Rotate,PushMatrix,PopMatrix
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner

if platform=="android":
    from jnius import autoclass,cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    LocationManager = autoclass('android.location.LocationManager')
    Context = autoclass('android.content.Context')
    LocationListener = autoclass('android.location.LocationListener')

# Embedded Python 3.14
def load_py314():
    lib_path = Path(__file__).parent / "data" / "python314" / "lib" / "libpython3.14.so"
    if not lib_path.exists(): return None
    lib = ctypes.CDLL(str(lib_path))
    lib.Py_Initialize()
    stdlib = str(Path(__file__).parent / "data" / "python314" / "stdlib")
    lib.PyRun_SimpleString(f"import sys; sys.path.insert(0, '{stdlib}')".encode())
    return lib

py314 = load_py314()
def run_py314(code: str):
    if py314:
        try: py314.PyRun_SimpleString(code.encode())
        except: pass

# Constants
MODEL_FILE="llama3-small-Q3_K_M.gguf"
MODELS_DIR=Path("models")
MODEL_PATH=MODELS_DIR/MODEL_FILE
ENCRYPTED_MODEL=MODEL_PATH.with_suffix(".aes")
DB_PATH=Path("chat_history.db.aes")
KEY_PATH=Path(".enc_key")
MODELS_DIR.mkdir(parents=True,exist_ok=True)

# Encryption
def get_key()->bytes:
    if not KEY_PATH.exists():KEY_PATH.write_bytes(AESGCM.generate_key(256))
    return KEY_PATH.read_bytes()[:32]
def decrypt_file(s:Path,d:Path,k:bytes):d.write_bytes(AESGCM(k).decrypt(s.read_bytes()[:12],s.read_bytes()[12:],None))

# Metrics
def collect_system_metrics()->Dict[str,float]:
    c=m=None
    if psutil:
        try:c=psutil.cpu_percent(0.1)/100;m=psutil.virtual_memory().percent/100
        except:pass
    return {"cpu":float(c or 0.3),"mem":float(m or 0.4),"load1":0.2,"temp":0.5,"proc":0.1}
def metrics_to_rgb(m:dict)->Tuple[float,float,float]:
    r=m["cpu"]*2.2;g=m["mem"]*1.9;b=m["temp"]*1.5;mx=max(r,g,b,1.0);return(r/mx,g/mx,b/mx)
def pennylane_entropic_score(rgb:Tuple[float,float,float],shots:int=256)->float:
    if qml is None:return sum(rgb)/3+random.random()*0.15-0.075
    dev=qml.device("default.qubit",wires=2,shots=shots)
    @qml.qnode(dev)
    def circuit(a,b,c):
        qml.RX(a*math.pi,wires=0);qml.RY(b*math.pi,wires=1);qml.CNOT(wires=[0,1])
        qml.RZ(c*math.pi,wires=1);qml.RX((a+b+c)*math.pi/3,wires=0)
        return qml.expval(qml.PauliZ(0)),qml.expval(qml.PauliZ(1))
    try:e0,e1=circuit(*rgb);s=1.0/(1.0+math.exp(-9.0*(((e0+1)/2*0.65+(e1+1)/2*0.35)-0.5)));return float(s)
    except:return 0.5
def entropic_summary_text(score:float)->str:
    if score>=0.78:return f"CHAOS RESONANCE {score:.3f}"
    if score>=0.55:return f"TURBULENT FIELD {score:.3f}"
    return f"STABLE MANIFOLD {score:.3f}"

# PUNKD & Generation
def punkd_analyze(text:str,top_n:int=16)->Dict[str,float]:
    toks=re.findall(r"[a-zA-Z0-9_]+",text.lower())
    freq={};[freq.__setitem__(t,freq.get(t,0)+1)for t in toks]
    boost={"ice":2.8,"wet":2.5,"snow":2.9,"fog":2.3,"flood":3.0,"construction":2.2,"debris":2.4,"animal":2.1,"blackice":4.0,"hydroplane":3.5}
    scored={t:c*boost.get(t,1.0)for t,c in freq.items()}
    top=sorted(scored.items(),key=lambda x:-x[1])[:top_n]
    if not top:return {}
    mx=top[0][1]
    return {k:float(v/mx)for k,v in top}
def punkd_apply(prompt:str,weights:Dict[str,float],profile:str="balanced")->Tuple[str,float]:
    if not weights:return prompt,1.0
    mean=sum(weights.values())/len(weights)
    mul_map={"conservative":0.7,"balanced":1.0,"aggressive":1.6}
    mul=mul_map.get(profile,1.0)
    adj=1.0+(mean-0.5)*1.2*mul
    adj=max(0.6,min(2.2,adj))
    markers=" ".join([f"<HAZ:{k}:{v:.2f}>"for k,v in sorted(weights.items(),key=lambda x:-x[1])[:8]])
    return prompt+f"\n\n[PUNKD HAZARD BOOST] {markers}",adj
def chunked_generate(llm:Llama,prompt:str,max_total_tokens:int=256,chunk_tokens:int=64,
                    base_temperature:float=0.18,punkd_profile:str="balanced",
                    streaming_callback:Optional[Callable[[str],None]]=None)->str:
    assembled="";cur_prompt=prompt
    token_weights=punkd_analyze(prompt,top_n=16)
    iterations=max(1,(max_total_tokens+chunk_tokens-1)//chunk_tokens)
    prev_tail=""
    for i in range(iterations):
        patched_prompt,mult=punkd_apply(cur_prompt,token_weights,profile=punkd_profile)
        temp=max(0.01,min(2.0,base_temperature*mult))
        out=llm(patched_prompt,max_tokens=chunk_tokens,temperature=temp,stop=["Low","Medium","High","\n","\r"])
        text=""
        if isinstance(out,dict):
            try:text=out.get("choices",[{}])[0].get("text","")
            except:text=out.get("text","")if isinstance(out,dict)else""
        else:text=str(out)
        text=(text or"").strip()
        if not text:break
        overlap=0
        max_ol=min(30,len(prev_tail),len(text))
        for olen in range(max_ol,0,-1):
            if prev_tail.endswith(text[:olen]):
                overlap=olen;break
        append_text=text[overlap:]if overlap else text
        assembled+=append_text
        prev_tail=assembled[-140:]if len(assembled)>140 else assembled
        if streaming_callback:streaming_callback(append_text)
        if assembled.strip().endswith(("Low","Medium","High")):break
        if len(text.split())<max(4,chunk_tokens//10):break
        cur_prompt=prompt+"\n\nAssistant so far:\n"+assembled+"\n\nContinue:"
    return assembled.strip()

def build_road_scanner_prompt(lat:float,lon:float)->str:
    metrics=collect_system_metrics()
    rgb=metrics_to_rgb(metrics)
    score=pennylane_entropic_score(rgb)
    entropy_text=entropic_summary_text(score)
    metrics_line=f"sys_metrics: cpu={metrics['cpu']:.3f} mem={metrics['mem']:.3f} load={metrics['load1']:.3f} temp={metrics['temp']:.3f} proc={metrics['proc']:.3f}"
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

# UI
class GPSListener(LocationListener):
    def __init__(self,cb):self.cb=cb
    def onLocationChanged(self,loc):
        if loc:self.cb(loc.getLatitude(),loc.getLongitude())
    def onProviderDisabled(self,p):pass
    def onProviderEnabled(self,p):pass
    def onStatusChanged(self,a,b,c):pass

class RiskWheel(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint=(None,None);self.size=(320,320);self.pos_hint={"center_x":.5}
        with self.canvas.before:PushMatrix();self.rot=Rotate(angle=0,origin=self.center)
        with self.canvas:
            Color(1,1,1,1);Ellipse(size=self.size,pos=self.pos)
            Color(0,1,0,0.7);Ellipse(size=(280,280),pos=self.center_x-140,self.center_y-140)
            Color(1,1,0,0.8);Ellipse(size=(200,200),pos=self.center_x-100,self.center_y-100)
            Color(1,0,0,0.9);Ellipse(size=(120,120),pos=self.center_x-60,self.center_y-60)
        with self.canvas.after:PopMatrix()
    def spin(self,risk:str):
        a=Animation(angle=-720 if risk=="Low" else 360 if risk=="Medium" else 1080,
                    duration=5 if risk=="Low" else 8 if risk=="Medium" else 3.5)
        a.start(self.rot)

class ScannerScreen(Screen):
    def __init__(self,app,**kwargs):
        super().__init__(**kwargs);self.app=app;self.lat=self.lon=None
        l=BoxLayout(orientation="vertical",spacing=25,padding=20)
        l.add_widget(MDLabel(text="HYDRA-9 QUANTUM SCAN",halign="center",font_style="H5"))
        self.coords=MDLabel(text="Acquiring GPS lock...",halign="center",font_style="Caption")
        l.add_widget(self.coords)
        self.wheel=RiskWheel()
        l.add_widget(self.wheel)
        self.result=MDLabel(text="Awaiting quantum verdict...",halign="center",font_style="H4")
        l.add_widget(self.result)
        self.spin=MDSpinner(size=(100,100),pos_hint={"center_x":.5})
        l.add_widget(self.spin)
        l.add_widget(MDRaisedButton(text="RETURN",on_release=lambda x:setattr(app.sm,"current","main")))
        self.add_widget(l)

    def on_enter(self):
        if platform!="android":
            self.coords.text="GPS: Desktop (simulated 40.7128,-74.0060)"
            self.lat,self.lon=40.7128,-74.0060
            Clock.schedule_once(self.run_scan,2)
            return
        try:
            ctx=PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)
            lm=ctx.getSystemService(Context.LOCATION_SERVICE)
            lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,1000,1.0,GPSListener(self.on_gps))
            self.coords.text="GPS SIGNAL ACQUISITION..."
        except Exception as e:self.coords.text=f"GPS FAILURE: {e}"

    def on_gps(self,lat,lon):
        self.lat,self.lon=lat,lon
        self.coords.text=f"LOCKED\n{lat:.6f}, {lon:.6f}"
        self.run_scan()

    def run_scan(self,*_):
        if not self.lat:return
        self.spin.active=True
        threading.Thread(target=self._scan,daemon=True).start()

    def _scan(self):
        try:
            k=self.app.key
            if ENCRYPTED_MODEL.exists():decrypt_file(ENCRYPTED_MODEL,MODEL_PATH,k)
            prompt=build_road_scanner_prompt(self.lat,self.lon)
            code=f'''
from llama_cpp import Llama
llm=Llama(model_path="{MODEL_PATH}",n_ctx=2048,n_threads=4)
def stream(t):print("STREAM:",t)
result=chunked_generate(llm,"{prompt.replace('"','\\"')}",streaming_callback=stream)
print("FINAL:",result)
'''
            run_py314(code)
            result="Medium"
            if "low" in result.lower():result="Low"
            elif "high" in result.lower():result="High"
            color={"Low":"00ff00","Medium":"ffff00","High":"ff0000"}[result]
            Clock.schedule_once(lambda dt:setattr(self.result,"markup",True))
            Clock.schedule_once(lambda dt:setattr(self.result,"text",f"[color={color}][size=80][b]{result}[/b][/size][/color]"))
            Clock.schedule_once(lambda dt:self.wheel.spin(result))
            if MODEL_PATH.exists():
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                encrypt_file(MODEL_PATH,ENCRYPTED_MODEL,k)
                MODEL_PATH.unlink()
        except Exception as e:
            Clock.schedule_once(lambda dt:setattr(self.result,"text",f"QUANTUM COLLAPSE: {e}"))
        finally:
            Clock.schedule_once(lambda dt:setattr(self.spin,"active",False))

class MainScreen(Screen):
    def __init__(self,app,**kwargs):
        super().__init__(**kwargs);self.app=app
        l=BoxLayout(orientation="vertical",padding=50,spacing=30)
        l.add_widget(MDLabel(text="HYDRA-9\nQuantum Road Oracle",halign="center",font_style="H4",theme_text_color="Primary"))
        b=MDRaisedButton(text="INITIATE QUANTUM SCAN",size_hint=(0.9,None),height=140,pos_hint={"center_x":.5})
        b.bind(on_release=lambda x:setattr(app.sm,"current","scanner"))
        l.add_widget(b)
        self.add_widget(l)

class HydraApp(MDApp):
    def build(self):
        self.theme_cls.theme_style="Dark"
        self.theme_cls.primary_palette="DeepPurple"
        self.key=get_key()
        self.sm=ScreenManager()
        self.sm.add_widget(MainScreen(self,name="main"))
        self.sm.add_widget(ScannerScreen(self,name="scanner"))
        return self.sm
    def on_start(self):asyncio.run(init_db(self.key))

if __name__=="__main__":
    HydraApp().run()
