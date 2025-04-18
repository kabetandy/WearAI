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
    Verifies your API key by listing available models.
    Returns {"ok": true, "available_models": N} on success.
    """
    try:
        models = client.models.list()
        return jsonify({"ok": True, "available_models": len(models)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ─── Try‑On Endpoint ───────────────────────────────────────────────────────────
@app.route('/tryon', methods=['POST'])
def tryon():
    """
    Runs a Stable Diffusion img2img demo on the uploaded photo.
    Returns {"result_url": "<generated image URL>"}.
    """
    if 'user_image' not in request.files:
        return jsonify({'error': 'Missing user_image'}), 400

    # Save the uploaded photo to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp_path = tmp.name
        request.files['user_image'].save(tmp_path)

    try:
        output = client.run(
            "stability-ai/stable-diffusion:db21e6c9bfcaf1ddd0c9d4e3a4858be58f13a72688f6242382d8b7391c0b17e4",
            input={
                "prompt": "a fashion model wearing a stylish outfit,
