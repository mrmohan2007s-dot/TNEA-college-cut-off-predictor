from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# Use a valid API key or provide fallback
API_KEY = "AIzaSyB1-DVvo9aMjuEQ_xFD45dMkwKWThg9_qU"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory('static', filename)

@app.route("/api/departments")
def get_departments():
    try:
        # Try different possible paths
        json_paths = [
            'static/cutoff.json',
            './static/cutoff.json',
            '/home/rishi/VS Code/Python/TNEA/static/cutoff.json'
        ]
        
        data = None
        for path in json_paths:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    print(f"Successfully loaded cutoff.json from: {path}")
                    break
            except FileNotFoundError:
                continue
        
        if data is None:
            return jsonify({"error": "cutoff.json not found"}), 404
        
        # Get unique departments and sort them
        departments = sorted(list(set(item["Department"] for item in data if "Department" in item)))
        print(f"Found {len(departments)} departments")
        return jsonify({"departments": departments})
        
    except Exception as e:
        print(f"Error loading departments: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    url_with_key = f"{GEMINI_URL}?key={API_KEY}"
    
    try:
        response = requests.post(url_with_key, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"response": text})
    except requests.exceptions.HTTPError as e:
        print(f"Gemini API HTTP error: {e}")
        if response.status_code == 400:
            return jsonify({"error": "Invalid API key or quota exceeded"}), 400
        elif response.status_code == 429:
            return jsonify({"error": "API quota exceeded"}), 429
        else:
            return jsonify({"error": f"Gemini API error: {e}"}), 500
    except Exception as e:
        print(f"Gemini API error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)