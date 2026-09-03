from flask import Flask, render_template, abort, redirect, send_file, send_from_directory
from pathlib import Path
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

PAGE_DIR = BASE_DIR / "page"
ICON_DIR = BASE_DIR / "icons"
SCREENSHOT_DIR = BASE_DIR / "screenshots"

# categoria.json fica em ~/categoria.json
CATEGORY_FILE = BASE_DIR / "categoria.json"


# =========================
# CATEGORIAS
# =========================

def carregar_categorias():

    if not CATEGORY_FILE.is_file():
        print(f"Arquivo de categorias não encontrado: {CATEGORY_FILE}")
        return {}

    try:

        dados = json.loads(
            CATEGORY_FILE.read_text(
                encoding="utf-8"
            )
        )

        categorias = {}

        for nome, numero in dados.items():

            try:

                categorias[str(nome)] = int(numero)

            except (ValueError, TypeError):

                print(
                    f"Categoria inválida: {nome} = {numero}"
                )

        return categorias

    except Exception as e:

        print(
            f"Erro ao carregar categorias: {e}"
        )

        return {}


def pegar_nome_categoria(numero):

    try:
        numero = int(numero)

    except (ValueError, TypeError):

        return None

    categorias = carregar_categorias()

    for nome, categoria_id in categorias.items():

        if categoria_id == numero:

            return nome

    return None


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

                if not isinstance(info, dict):
                    continue

                app_data = dict(info)

                app_data["id"] = app_id
                app_data["_arquivo"] = arquivo

                # Normaliza a categoria
                if "Categoria" in app_data:

                    try:

                        app_data["Categoria"] = int(
                            app_data["Categoria"]
                        )

                    except (ValueError, TypeError):

                        app_data["Categoria"] = None

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

    def icon_url(app_data):

        nome = Path(
            app_data.get(
                "icon",
                f"{app_data['id']}.png"
            )
        ).name

        return f"/icons/{nome}"


    def category_name(app_data):

        categoria = app_data.get(
            "Categoria"
        )

        if categoria is None:

            return "Sem categoria"

        nome = pegar_nome_categoria(
            categoria
        )

        if nome:

            return nome

        return "Categoria desconhecida"


    def category_url(app_data):

        categoria = app_data.get(
            "Categoria"
        )

        try:

            categoria = int(categoria)

        except (ValueError, TypeError):

            return "#"

        if pegar_nome_categoria(categoria):

            return f"/categoria/{categoria}"

        return "#"


    return {
        "icon_url": icon_url,
        "category_name": category_name,
        "category_url": category_url
    }


# =========================
# SITEMAP
# =========================
@app.route("/ads.txt")
def ads_txt():

    return send_from_directory(
        BASE_DIR,
        "ads.txt"
    )

@app.route("/favicon.png")
def favicon():

    return send_file(
        BASE_DIR / "favicon.png"
    )

@app.route("/sitemap.xml")
def sitemap():

    return send_from_directory(
        BASE_DIR,
        "sitemap.xml"
    )


# =========================
# ROBOTS
# =========================

@app.route("/robots.txt")
def robots():

    return send_from_directory(
        BASE_DIR,
        "robots.txt"
    )


# =========================
# HOME
# =========================

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
# TODAS AS CATEGORIAS
# =========================

@app.route("/categorias")
def categorias():

    categorias = carregar_categorias()

    categorias = sorted(
        categorias.items(),
        key=lambda item: item[1]
    )

    return render_template(
        "index.html",
        page="categories",
        categorias=categorias
    )


# =========================
# UMA CATEGORIA
# =========================

@app.route("/categoria/<int:categoria_id>")
def categoria(categoria_id):

    categoria_nome = pegar_nome_categoria(
        categoria_id
    )

    if not categoria_nome:

        abort(404)

    apps = carregar_apps()

    apps_categoria = []

    for app_data in apps:

        categoria = app_data.get(
            "Categoria"
        )

        if categoria == categoria_id:

            apps_categoria.append(
                app_data
            )

    return render_template(
        "index.html",
        page="category",
        categoria_id=categoria_id,
        categoria_nome=categoria_nome,
        apps_categoria=apps_categoria
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

    download_url = app_data.get(
        "download",
        ""
    ).strip()

    return render_template(
        "index.html",
        page="download",
        app=app_data,
        apk_exists=bool(download_url)
    )


# =========================
# DOWNLOAD
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
