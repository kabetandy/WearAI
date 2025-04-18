
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
    if 'user_image' not in request.files or 'cloth_image' not in request.files:
        return jsonify({'error': 'Missing images'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as user_temp:
        user_path = user_temp.name
        request.files['user_image'].save(user_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as cloth_temp:
        cloth_path = cloth_temp.name
        request.files['cloth_image'].save(cloth_path)

    try:
        output = client.run(
            "prompthero/openjourney",
            input={
                "prompt": "realistic person wearing outfit",
                "image": open(user_path, "rb")
            }
        )
        return jsonify({'result_url': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(user_path)
        os.remove(cloth_path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
