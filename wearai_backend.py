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
    """
    Minimal example using the default Stable Diffusion text-to-image model.
    Expects a 'user_image' file but ignores it for now—just generates a demo image.
    """
    if 'user_image' not in request.files:
        return jsonify({"error": "Missing user_image"}), 400

    # Save the uploaded file (even if we won't use it)
    user_file = request.files['user_image']
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp_path = tmp.name
        user_file.save(tmp_path)

    try:
        # Run a public Stable Diffusion text-to-image demo
        output = client.run(
    "stability-ai/stable-diffusion:b3d14e1c",
    input={
        "prompt": "a fashion model wearing stylish clothes, studio photo",
        "num_outputs": 1
    }
)
        # `output` is a list of URLs
        return jsonify({"result_url": output[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(tmp_path)

# ─── Main Entrypoint ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
