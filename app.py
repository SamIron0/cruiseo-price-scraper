from flask import Flask, request, jsonify
from main import scraper as scraper_script
import os

app = Flask(__name__)

@app.route("/execute-script", methods=["POST"])
def execute_script():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data to the scraper_script
        result = scraper_script(origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Use os.environ.get to retrieve the port, defaulting to 5001
    port = int(os.environ.get("PORT", 5001))

    # Run the Flask app
    app.run(host="0.0.0.0", port=port, threaded=True)
