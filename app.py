import requests
from flask import Flask, render_template, request, jsonify
import openai
from exceptions import GPT4QueryError, OverpassAPIError
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def convert_nl_to_overpass_query(nl_query):
    try:
        response = openai.Completion.create(
            engine="text-davinci-codex-002",
            prompt=f"Translate the following natural language query to an Overpass query: {nl_query}",
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )

        overpass_query = response.choices[0].text.strip()
        return overpass_query
    except Exception as e:
        raise GPT4QueryError(str(e))

def run_overpass_query(overpass_query):
    overpass_url = "http://overpass-api.de/api/interpreter"
    try:
        response = requests.get(overpass_url, params={"data": overpass_query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise OverpassAPIError(str(e))

def get_bounds(data):
    min_lat, max_lat, min_lon, max_lon = 90, -90, 180, -180
    for element in data["elements"]:
        if "lat" in element and "lon" in element:
            min_lat = min(min_lat, element["lat"])
            max_lat = max(max_lat, element["lat"])
            min_lon = min(min_lon, element["lon"])
            max_lon = max(max_lon, element["lon"])
    return [[min_lat, min_lon], [max_lat, max_lon]]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    nl_query = request.form.get("query", "")
    try:
        overpass_query = convert_nl_to_overpass_query(nl_query)
        print(f"Overpass query generated: {overpass_query}")
        data = run_overpass_query(overpass_query)
        print(f"Overpass API response: {data}")
        bounds = get_bounds(data)
        return jsonify({"data": data, "bounds": bounds})
    except (GPT4QueryError, OverpassAPIError) as e:
        return jsonify({"error": str(e), "data": None, "bounds": None})

if __name__ == "__main__":
    app.run(debug=True)

