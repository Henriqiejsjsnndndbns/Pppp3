from flask import Flask, render_template_string, request
from flask_socketio import SocketIO
from pynput.mouse import Controller, Button
import socket

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

mouse = Controller()
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Remote Mouse</title>

        <style>
            body {{
                margin:0;
                background:black;
                height:100vh;
                display:flex;
            }}

            button {{
                width:100%;
                height:100vh;
                background:#000;
                color:#00ff88;
                font-size:40px;
                border:none;
                font-family:monospace;
            }}

            button:active {{
                background:#00ff88;
                color:black;
            }}

            #info {{
                position:absolute;
                top:10px;
                left:10px;
                color:#00ff88;
                font-size:12px;
                font-family:monospace;
            }}
        </style>
    </head>

    <body>

        <div id="info">
            {ip}:5000
        </div>

        <button id="btn">TOCAR</button>

        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>

        <script>
            const socket = io();

            socket.emit("auth", {{"password":"1234"}});

            document.getElementById("btn").onclick = () => {{
                socket.emit("click");
            }};
        </script>

    </body>
    </html>
    """)

@socketio.on("auth")
def auth(data):
    clients.add(request.sid)

@socketio.on("click")
def click():
    if request.sid in clients:
        mouse.click(Button.left, 1)

if __name__ == "__main__":
    print("Servidor rodando em http://0.0.0.0:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
