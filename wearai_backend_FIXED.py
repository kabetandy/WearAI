
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
        output_url = client.run(
            "stability-ai/stable-diffusion-img2img:27b3ac62c86054f60e2e5f1c2a88a7a08991e283ce26b3fc16e2c5bf3b807c2b",
            input={
                "image": open(user_path, "rb"),
                "prompt": "fashion model wearing elegant clothing, full body, photo",
                "strength": 0.6,
                "guidance_scale": 7.5,
                "num_outputs": 1
            }
        )
        return jsonify({'result_url': output_url[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(user_path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
