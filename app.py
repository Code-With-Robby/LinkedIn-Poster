%%writefile app.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

client = OpenAI(
    api_key=os.environ.get('GEMINI_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

app = Flask(__name__)

def generate_x_post(topic: str) -> str:
    prompt = f"""
    You are an expert social media manager, and you excel at crafting viral, educational and highly engaging posts for Linkedin.
    Your task is to generate a post that is concise, valuable in terms of educational, impactful, and tailored to the topic provided by the user.
    Avoid using hashtags and lots of emojis (a few emojis are fine, but not too many).

    Keep the post short, structure it in a clean, readable way, using line breaks and empty lines to enhance readability.

    Here's the topic provided by the user for which you need to generate a post:
    <topic>
    {topic}
    </topic>


"""
    response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )

    post = response.choices[0].message.content
    return post or "Sorry, I couldn't generate a post for that topic."


@app.route('/generate_x_post', methods=['POST'])
def generate_x_post_endpoint():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    topic = data['topic']
    post = generate_x_post(topic)
    return jsonify({"x_post": post})

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the LinkedIn Post Generator! Send a POST request to /generate_x_post"
