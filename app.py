import json
import random
from difflib import get_close_matches
from flask import Flask, render_template, request, jsonify

# Load preprocessed training data
def load_training_data(input_file="brain.json"):
    with open(input_file, "r", encoding="utf-8") as json_file:
        return json.load(json_file)

# Fuzzy match to find the best response, with randomization
def find_best_response(user_input, input_output_pairs):
    user_input = user_input.lower()
    possible_responses = []

    # Handle specific protocol responses
    if user_input == "f":
        return "m"
    elif user_input == "m":
        return "f"
    elif user_input == "f or m":
        return random.choice(["m", "f"])
    elif "are you a bot" in user_input or "are you a robot" in user_input:
        return "lemme hope you're not a bot"
    elif "do you hate humans" in user_input:
        return "why would I hate myself"

    # Direct match
    for question, answer in input_output_pairs:
        if user_input == question:
            possible_responses.append(answer)

    # Fuzzy match
    questions = [q for q, _ in input_output_pairs]
    closest_matches = get_close_matches(user_input, questions, n=1, cutoff=0.5)
    if closest_matches:
        match = closest_matches[0]
        for question, answer in input_output_pairs:
            if question == match:
                possible_responses.append(answer)

    # Return a random response from possible ones
    if possible_responses:
        return random.choice(possible_responses)

    return None

# Generate a response using context
def get_response(user_input, input_output_pairs, conversation_history, sent_responses):
    # Update conversation history
    conversation_history.append(f"You: {user_input}")
    
    # Check for a relevant response
    response = find_best_response(user_input, input_output_pairs)
    
    # If a response is found, ensure it hasn't been sent already
    while response in sent_responses:
        response = find_best_response(user_input, input_output_pairs)
        if not response:  # If no response is found, break to prevent infinite loop
            break
    
    if response:
        conversation_history.append(f"Stranger: {response}")
        sent_responses.add(response)  # Add to sent responses set
        return response

    # If no match, use context to craft a response
    if len(conversation_history) > 1:
        last_stranger_response = conversation_history[-2]
        response = f"Based on what we were discussing earlier: {last_stranger_response.split('Stranger: ')[-1]}."
        conversation_history.append(f"Stranger: {response}")
        sent_responses.add(response)  # Add to sent responses set
        return response

    # Fallback response
    fallback_response = "I'm not sure about that, can you explain more?"
    conversation_history.append(f"Stranger: {fallback_response}")
    sent_responses.add(fallback_response)  # Add to sent responses set
    return fallback_response

# Flask setup
app = Flask(__name__, template_folder='templates')  # Fixed the issue here

conversation_history = []  # Memory to store conversation
input_output_pairs = load_training_data("brain.json")
sent_responses = set()  # Track sent responses

@app.route('/')
def index():
    return render_template('io.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if user_input:
        response = get_response(user_input, input_output_pairs, conversation_history, sent_responses)
        return jsonify({'response': response})
    return jsonify({'response': "I'm not sure about that, can you explain more?"})

# Save conversation history to file
@app.route('/save', methods=['POST'])
def save_conversation():
    with open("conversation_history.json", "w", encoding="utf-8") as json_file:
        json.dump(conversation_history, json_file, ensure_ascii=False, indent=4)
    return jsonify({"status": "Conversation saved."})

if __name__ == '__main__':
    app.run(debug=True)
