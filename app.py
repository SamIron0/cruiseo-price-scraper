from flask import Flask
from main import scraper as scraper_script
import os

app = Flask(__name__)


@app.route("/execute-script", methods=["GET"])
def execute_script():
    return scraper_script()


if __name__ == "__main__":
    # Use os.environ.get to retrieve the port, defaulting to 5001
    port = int(os.environ.get("PORT", 5001))

    # Run the Flask app
    app.run(host="0.0.0.0", port=port, threaded=True)
