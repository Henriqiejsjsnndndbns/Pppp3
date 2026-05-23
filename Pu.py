from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from pynput.mouse import Controller, Button
import socket
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

mouse = Controller()

PASSWORD = str(random.randint(1000, 9999))
clients = set()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


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
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                color:#0f0;
                font-family:monospace;
                flex-direction:column;
            }}

            #btn {{
                width:180px;
                height:180px;
                border-radius:50%;
                background:#00ff88;
                border:none;
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

            socket.emit("auth", {{password: "{PASSWORD}"}});

            document.getElementById("btn").addEventListener("click", () => {{
                let now = Date.now();

                if(now - last < 300) {{
                    socket.emit("click");
                }} else {{
                    socket.emit("move", {{x: 20, y: 0}});
                }}

                last = now;
            }});
        </script>

    </body>
    </html>
    """)


@socketio.on("auth")
def auth(data):
    if data.get("password") == PASSWORD:
        clients.add(request.sid)
        emit("ok")


@socketio.on("move")
def move(data):
    if request.sid in clients:
        mouse.move(float(data["x"]), float(data["y"]))


@socketio.on("click")
def click():
    if request.sid in clients:
        mouse.click(Button.left, 1)


if __name__ == "__main__":
    print("Servidor rodando")
    print("Senha:", PASSWORD)
    socketio.run(app, host="0.0.0.0", port=5000)
