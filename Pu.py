import os
import sys
import socket
import random

# =========================
# AUTO INSTALL (SEGURADO)
# =========================
try:
    from flask import Flask, render_template_string, request
    from flask_socketio import SocketIO, emit
    from pynput.mouse import Controller, Button
except:
    print("📦 Instalando dependências...")
    os.system("pip install flask flask-socketio pynput")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# =========================
# APP
# =========================
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

mouse = Controller()

PASSWORD = str(random.randint(1000, 9999))
clients = set()

# =========================
# IP LOCAL
# =========================
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

# =========================
# FRONTEND SIMPLES
# =========================
@app.route("/")
def home():
    ip = get_ip()

    return render_template_string(f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Mouse Remote</title>

        <style>
            body {{
                margin:0;
                background:black;
                color:#00ff88;
                font-family:monospace;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                height:100vh;
            }}

            #btn {{
                width:220px;
                height:220px;
                border-radius:50%;
                border:none;
                background:#00ff88;
                font-size:20px;
                font-weight:bold;
            }}

            #btn:active {{
                transform:scale(0.95);
            }}

            #info {{
                position:absolute;
                top:10px;
                font-size:12px;
                opacity:0.8;
            }}
        </style>
    </head>

    <body>

        <div id="info">
            IP: {ip}:5000 | SENHA: {PASSWORD}
        </div>

        <button id="btn">TOQUE</button>

        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>

        <script>
            const socket = io();
            let last = 0;

            socket.emit("auth", {{password:"{PASSWORD}"}});

            document.getElementById("btn").onclick = () => {{
                let now = Date.now();

                if(now - last < 300) {{
                    socket.emit("click");
                }} else {{
                    socket.emit("move", {{x: 25, y: 0}});
                }}

                last = now;
            }};
        </script>

    </body>
    </html>
    """)

# =========================
# AUTH
# =========================
@socketio.on("auth")
def auth(data):
    if data.get("password") == PASSWORD:
        clients.add(request.sid)
        emit("ok")

# =========================
# MOVE
# =========================
@socketio.on("move")
def move(data):
    if request.sid in clients:
        mouse.move(float(data.get("x", 0)), float(data.get("y", 0)))

# =========================
# CLICK
# =========================
@socketio.on("click")
def click():
    if request.sid in clients:
        mouse.click(Button.left, 1)

# =========================
# START
# =========================
if __name__ == "__main__":
    ip = get_ip()
    print("\n🚀 SERVIDOR INICIADO")
    print(f"🌐 Abra no celular: http://{ip}:5000")
    print(f"🔐 Senha: {PASSWORD}\n")

    socketio.run(app, host="0.0.0.0", port=5000)
