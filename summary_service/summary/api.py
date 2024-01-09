import hashlib
from datetime import datetime

import openai
from flask import Flask, request, jsonify

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Version number for the service
SERVICE_VERSION = "1.0"


# Load the prompt template from a file or database
def get_prompt_template():
    """
    This function retrieves a prompt template that iterates three times
    to refine the summary of an article based on key concepts extracted
    in each iteration.
    """
    return (
        "1. Identify the key concepts of the following article:\n\n"
        "{article}\n\n"
        "2. Based on these key concepts, provide a brief summary of the article.\n\n"
        "3. Refine the summary by focusing on the most important aspects:\n\n"
        "{summary_step_1}\n\n"
        "4. Further refine the summary to be concise and clear, emphasizing critical points:\n\n"
        "{summary_step_2}"
    )


def generate_hash(article):
    # This function generates a SHA256 hash of the article
    return hashlib.sha256(article.encode()).hexdigest()


@app.route('/template', methods=['GET'])
def template():
    return jsonify({"template": get_prompt_template()})


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    article = data['article']
    prompt = get_prompt_template() + "\n\n" + article

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )

    summary = response.choices[0].text.strip()
    current_date = datetime.now().strftime("%Y-%m-%d")
    article_hash = generate_hash(article)

    return jsonify({
        "summary": summary,
        "date": current_date,
        "version": SERVICE_VERSION,
        "article_hash": article_hash
    })


if __name__ == '__main__':
    app.run(debug=True)
