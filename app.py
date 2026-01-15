import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, Response # Added Response

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

def generate_x_post_stream(topic: str):
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
    stream = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ],
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', post='')

@app.route('/generate_ui_post', methods=['POST'])
def generate_ui_post():
    topic = request.form['topic']
    generated_post = generate_x_post(topic)
    return render_template('index.html', topic=topic, post=generated_post)

@app.route('/generate_x_post', methods=['POST'])
def generate_x_post_endpoint():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    topic = data['topic']
    post = generate_x_post(topic)
    return jsonify({"x_post": post})

@app.route('/stream_linkedin_post', methods=['POST']) # New streaming endpoint
def stream_linkedin_post():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    topic = data['topic']
    return Response(generate_x_post_stream(topic), mimetype='text/event-stream')
