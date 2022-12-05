from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
from pathlib import Path
from db import get_db, close_db
import sqlalchemy
from logger import log


app = Flask(__name__)
app.teardown_appcontext(close_db)
cors = CORS(app, send_wildcard=True)
CHATS_DIRECTORY = app.config.get("CHATS_DIRECTORY", "./chats/")


@app.route("/save", methods=["POST"])
def save():
    body = json.loads(request.data)["body"]
    filename = int(datetime.now().timestamp())
    with open(f"{CHATS_DIRECTORY}{filename}", "w") as fp:
        fp.write(body)
    return jsonify({"msg": f"wrote file: {filename}"})


def parse(filename):
    # Parse the HTML using BeautifulSoup
    path = Path("./", filename).absolute()
    with open(path, "r") as fp:
        text = fp.read()
        return text


@app.route("/chat/<timestamp>")
def show_chat(timestamp):
    path = Path(CHATS_DIRECTORY, timestamp).absolute()
    return parse(path)


@app.route("/parse")
def parse_latest():
    # Get a list of all the files in the directory
    files = os.listdir(CHATS_DIRECTORY)
    # Initialize a variable to keep track of the most recently modified file
    most_recent_file = None
    # Iterate over the list of files
    for file in files:
        # Get the full path of the current file
        file_path = os.path.join(CHATS_DIRECTORY, file)

        if most_recent_file is None or os.path.getmtime(
            file_path
        ) > os.path.getmtime(  # noqa: E501
            most_recent_file
        ):
            # If the current file is more recently modified, store
            # its path as the
            # most recently modified file
            most_recent_file = file_path
    parsed = parse(most_recent_file)
    return render_template("parsed.html", parsed=parsed)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    log.info("Checking /health")
    db = get_db()
    health = "BAD"
    try:
        result = db.execute("SELECT NOW()")
        result = result.one()
        health = "OK"
        log.info(f"/health reported OK including database connection: {result}")
    except sqlalchemy.exc.OperationalError as e:
        msg = f"sqlalchemy.exc.OperationalError: {e}"
        log.error(msg)
    except Exception as e:
        msg = f"Error performing healthcheck: {e}"
        log.error(msg)

    return health
