import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to load training data
def load_training_data(filepath):
    try:
        with open(filepath, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}.")
        return []

# Load the training data
input_output_pairs = load_training_data("brain.json")

@app.route("/")
def home():
    return "Flask App Running"

@app.route("/respond", methods=["POST"])
def respond():
    user_input = request.json.get("input", "")
    for pair in input_output_pairs:
        if pair.get("input").lower() == user_input.lower():
            return jsonify({"response": pair.get("output")})
    return jsonify({"response": "I don't understand that."})

if __name__ == "__main__":
    app.run()
