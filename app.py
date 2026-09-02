from flask import Flask, render_template, abort, redirect, send_file
from pathlib import Path
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

PAGE_DIR = BASE_DIR / "page"
ICON_DIR = BASE_DIR / "icons"
SCREENSHOT_DIR = BASE_DIR / "screenshots"


# =========================
# CARREGAR APLICATIVOS
# =========================

def carregar_apps():

    apps = []

    for arquivo in PAGE_DIR.glob("*.json"):

        try:

            dados = json.loads(
                arquivo.read_text(
                    encoding="utf-8"
                )
            )

            for app_id, info in dados.items():

                app_data = dict(info)

                app_data["id"] = app_id
                app_data["_arquivo"] = arquivo

                apps.append(app_data)

        except Exception as e:

            print(
                f"Erro ao carregar {arquivo}: {e}"
            )

    return apps


def pegar_app(app_id):

    for app in carregar_apps():

        if app["id"] == app_id:
            return app

    return None


# =========================
# HELPERS
# =========================

@app.context_processor
def helpers():

    def icon_url(app):

        nome = Path(
            app.get(
                "icon",
                f"{app['id']}.png"
            )
        ).name

        return f"/icons/{nome}"

    return {
        "icon_url": icon_url
    }


# =========================
# HOME
# =========================

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")

@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")
@app.route("/")
def home():

    apps = carregar_apps()

    populares = sorted(
        apps,
        key=lambda x: float(
            x.get("rating", 0)
        ),
        reverse=True
    )[:6]

    ultimos = sorted(
        apps,
        key=lambda x: x["_arquivo"].stat().st_mtime,
        reverse=True
    )[:10]

    return render_template(
        "index.html",
        page="home",
        populares=populares,
        ultimos=ultimos
    )


# =========================
# PÁGINA DO APP
# =========================

@app.route("/app/<app_id>")
def pagina_app(app_id):

    app_data = pegar_app(app_id)

    if not app_data:
        abort(404)

    return render_template(
        "index.html",
        page="app",
        app=app_data
    )


# =========================
# PÁGINA DE DOWNLOAD
# =========================

@app.route("/download/<app_id>")
def pagina_download(app_id):

    app_data = pegar_app(app_id)

    if not app_data:
        abort(404)

    # Verifica se existe um link configurado
    download_url = app_data.get("download", "").strip()

    return render_template(
        "index.html",
        page="download",
        app=app_data,
        apk_exists=bool(download_url)
    )


# =========================
# REDIRECIONAR PARA MEDIAFIRE
# =========================

@app.route("/get/<app_id>")
def baixar_apk(app_id):

    app_data = pegar_app(app_id)

    if not app_data:
        abort(404)

    download_url = app_data.get(
        "download",
        ""
    ).strip()

    if not download_url:
        abort(
            404,
            description="Link de download não configurado."
        )

    return redirect(
        download_url,
        code=302
    )


# =========================
# ÍCONES
# =========================

@app.route("/icons/<filename>")
def icone(filename):

    filename = Path(filename).name

    arquivo = ICON_DIR / filename

    if not arquivo.is_file():
        abort(404)

    return send_file(arquivo)


# =========================
# SCREENSHOTS
# =========================

@app.route("/screenshots/<path:filename>")
def screenshot(filename):

    arquivo = (
        SCREENSHOT_DIR / filename
    ).resolve()

    try:

        arquivo.relative_to(
            SCREENSHOT_DIR.resolve()
        )

    except ValueError:

        abort(404)

    if not arquivo.is_file():
        abort(404)

    return send_file(arquivo)


# =========================
# SERVIDOR
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
