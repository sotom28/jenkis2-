import os
import subprocess

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def index():
    return (
        "<h1>Saludador</h1>"
        '<form action="/hello"><input name="name"><button>Saludar</button></form>'
    )


@app.route("/hello")
def hello():
    name = request.args.get("name", "")
    return f"Hello, {name}!"


@app.route("/admin/backup")
def backup():
    # Ruta interna: no está enlazada desde ninguna página
    nombre = request.args.get("nombre", "respaldo")
    subprocess.run(f"tar czf /tmp/{nombre}.tgz .", shell=True)
    return {"backup": nombre}


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")  # nosec B104
