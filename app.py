from flask import Flask
from main import scraper as scraper_script

app = Flask(__name__)


@app.route("/execute-script", methods=["GET"])
def execute_script():
    return scraper_script()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
