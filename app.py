import os
import re
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
memory = {"user_name": ""}

OLLAMA_API_URL = "http://localhost:11434/api/generate"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    lowered = user_input.lower()

    if lowered in ["hi", "hello", "hey"]:
        return jsonify({"response": "Yo yo yo what up biatch? 😎"})

    # Better name detection using regex
    if any(phrase in lowered for phrase in ["my name is", "i am", "i'm"]):
        match = re.search(r"(my name is|i am|i'm) ([a-zA-Z ]+)", lowered)
        if match:
            name = match.group(2).strip().title()
            memory["user_name"] = name
            return jsonify({"response": f"Got it! I'll remember your name is {name}. 😊"})
        else:
            return jsonify({"response": "I didn't catch your name. Try saying 'my name is [your name]'."})

    if "your name" in lowered:
        return jsonify({"response": "I'm test_8.2. biatch 🤖."})

    if "say my name" in lowered or "who am i" in lowered:
        name = memory.get("user_name", "")
        if name:
            return jsonify({"response": f"You're {name}."})
        else:
            return jsonify({"response": "I didn't catch your name. Try saying 'my name is [your name]'."})

    # General chat using Ollama model
    user_name = memory.get("user_name", "User")
    prompt = f"{user_name}: {user_input}\nAI:"
    return jsonify({"response": query_ollama(prompt)})

def query_ollama(prompt):
    payload = {
        "model": "phi",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 100,
        "stop": ["\n"]
    }
    try:
        r = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        if r.status_code == 200:
            response_text = ""
            for line in r.iter_lines():
                if line:
                    data = line.decode("utf-8")
                    if data.startswith("data: "):
                        data = data[6:]
                    if '"response":' in data:
                        import json
                        chunk = json.loads(data)
                        response_text += chunk.get("response", "")
            return response_text.strip() or "🤖 Didn’t get a response."
        else:
            return f"⚠️ Error: {r.status_code} - {r.text}"
    except Exception as e:
        return f"❌ Request failed: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
