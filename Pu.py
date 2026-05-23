
import os
import sys
import socket
import random
import qrcode
from io import BytesIO
import base64

VENV = "venv"

if not os.path.exists(VENV):
    print("📦 Criando venv...")
    os.system("python3 -m venv venv")

if sys.prefix == sys.base_prefix:
    print("📦 Instalando dependências...")
    os.system(f"{VENV}/bin/pip install --upgrade pip")
    os.system(f"{VENV}/bin/pip install flask flask-socketio pynput qrcode pillow")
    print("🚀 Reiniciando no venv...\n")
    os.execv(f"{VENV}/bin/python", [f"{VENV}/bin/python"] + sys.argv)

from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from pynput.mouse import Controller, Button

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

mouse = Controller()
clients = set()

PASSWORD = str(random.randint(1000, 9999))
SENS = 2.4

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def make_qr(data):
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@app.route("/")
def home():
    ip = get_ip()
    url = f"http://{ip}:5000"
    qr = make_qr(url)

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>REMOTE</title>
        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{
                background: #000;
                color: #00ff9d;
                font-family: 'Courier New', monospace;
                overflow: hidden;
                height: 100vh;
                touch-action: none;
            }}
            .top-info {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(0,0,0,0.9);
                padding: 10px;
                text-align: center;
                z-index: 10;
                font-size: 13px;
                border-bottom: 1px solid #00ff9d;
            }}
            #pad {{
                position: absolute;
                top: 55px;
                left: 0;
                right: 0;
                bottom: 0;
                background: #000;
            }}
            .connect-btn {{
                position: absolute;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                background: #00ff9d;
                color: #000;
                border: none;
                padding: 15px 40px;
                border-radius: 50px;
                font-size: 18px;
                font-weight: bold;
                box-shadow: 0 0 25px #00ff9d;
                z-index: 20;
            }}
        </style>
    </head>
    <body>
        <div class="top-info">
            Senha: <b>{PASSWORD}</b> | IP: {ip}:5000
            <br>
            <img src="data:image/png;base64,{qr}" width="90">
        </div>

        <div id="pad"></div>

        <button class="connect-btn" onclick="connect()">CONECTAR</button>

        <script>
            let socket;
            let connected = false;
            let lx = 0, ly = 0;

            function connect() {{
                const pass = prompt("Digite a senha:", "");
                if (!pass) return;

                socket = io();
                socket.emit("auth", {{ password: pass }});

                socket.on("ok", () => {{
                    connected = true;
                    alert("✅ Conectado! Tela preta pronta pra mexer...");
                }));

                socket.on("fail", () => alert("❌ Senha errada!"));
            }}

            const pad = document.getElementById("pad");

            pad.addEventListener("touchstart", e => {{
                if (!connected) return;
                const t = e.touches[0];
                lx = t.clientX;
                ly = t.clientY;
            }});

            pad.addEventListener("touchmove", e => {{
                if (!connected) return;
                e.preventDefault();

                const t = e.touches[0];
                const dx = (t.clientX - lx) * {SENS};
                const dy = (t.clientY - ly) * {SENS};

                lx = t.clientX;
                ly = t.clientY;

                socket.emit("move", {{ x: dx, y: dy }});
            }});

            // Toque longo = clique esquerdo
            let timer;
            pad.addEventListener("touchstart", () => {{
                timer = setTimeout(() => {{
                    if (connected && socket) socket.emit("click");
                }}, 500);
            }});

            pad.addEventListener("touchend", () => clearTimeout(timer));
        </script>
    </body>
    </html>
    """)

@socketio.on("auth")
def auth(data):
    if data.get("password") == PASSWORD:
        clients.add(request.sid)
        emit("ok")
        print("💚 Conectado")
    else:
        emit("fail")

@socketio.on("move")
def move(data):
    if request.sid not in clients: return
    mouse.move(float(data.get("x", 0)), float(data.get("y", 0)))

@socketio.on("click")
def click():
    if request.sid in clients:
        mouse.click(Button.left, 1)

if __name__ == "__main__":
    print("🚀 Modo Minimalista - Tela Preta + 1 Botão")
    print(f"🔐 Senha: {PASSWORD}")
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
