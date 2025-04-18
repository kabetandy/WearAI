
from flask import Flask, request, jsonify
import replicate
from flask_cors import CORS
import tempfile
import os

app = Flask(__name__)
CORS(app)
REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]
replicate.Client(api_token=REPLICATE_API_TOKEN)

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
        output = replicate.run(
            "valayob/tryiton:dbb9d49c279e7ad6550a9d8e6d4c13877b0be67cc2b0d7f6518c3fb42a50f0dd",
            input={
                "person_image": open(user_path, "rb"),
                "cloth_image": open(cloth_path, "rb")
            }
        )
        return jsonify({'result_url': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(user_path)
        os.remove(cloth_path)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

