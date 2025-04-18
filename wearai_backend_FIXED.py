from flask import Flask, request, jsonify
from flask_cors import CORS
import replicate
import tempfile
import os

# ─── App & CORS ────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ─── Replicate Client ─────────────────────────────────────────────────────────
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# ─── Health‑check Endpoint ────────────────────────────────────────────────────
@app.route('/test', methods=['GET'])
def test():
    """
    Verifies that your API key works by listing available models.
    Returns {"ok": True, "available_models": N} on success.
    """
    try:
        models = client.models.list()
        return jsonify({"ok": True, "available_models": len(models)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ─── Try‑On Endpoint ───────────────────────────────────────────────────────────
@app.route('/tryon', methods=['POST'])
def tryon():
    if 'user_image' not in request.files:
        return jsonify({'error': 'Missing user_image'}), 400

    # Save the uploaded image to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp_path = tmp.name
        request.files['user_image'].save(tmp_path)

    try:
        # Call the free openjourney model
        output = client.run(
            "prompthero/openjourney:dbb9d49c279e7ad6550a9d8e6d4c13877b0be67cc2b0d7f6518c3fb42a50f0dd",
            input={
                "prompt": "a fashion model wearing a stylish outfit, photo",
                "image": open(tmp_path, "rb")
            }
        )
        # output is a list of URLs
        return jsonify({'result_url': output[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(tmp_path)

# ─── Main Entrypoint ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
