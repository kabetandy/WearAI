
from flask import Flask, request, jsonify
from flask_cors import CORS
import replicate
import tempfile
import os

app = Flask(__name__)
CORS(app)

REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

@app.route('/tryon', methods=['POST'])
def tryon():
    if 'user_image' not in request.files:
        return jsonify({'error': 'Missing user image'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as user_temp:
        user_path = user_temp.name
        request.files['user_image'].save(user_path)

    try:
        output = client.run(
            "stability-ai/sdxl:5f56db0d0dfb5f1741e5c7cfc7f1d0f8bbebd2f28dfbfb07c354a9cde292bcd2",
            input={{
                "prompt": "fashion photography, model wearing elegant clothing, full body",
                "image": open(user_path, "rb")
            }}
        )
        return jsonify({ 'result_url': output })
    except Exception as e:
        return jsonify({ 'error': str(e) }), 500
    finally:
        os.remove(user_path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
