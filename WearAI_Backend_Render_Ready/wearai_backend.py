from flask import Flask, request, jsonify
from flask_cors import CORS
import replicate
import tempfile
import os

app = Flask(__name__)
CORS(app)

# Replicate client
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

@app.route("/test", methods=["GET"])
def test():
    """Health‑check: lists models to verify your token"""
    try:
        models = client.models.list()
        return jsonify({"ok": True, "available_models": len(models)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/tryon", methods=["POST"])
def tryon():
    """Runs a public Stable Diffusion img2img on your upload."""
    if "user_image" not in request.files:
        return jsonify({"error": "Missing user_image"}), 400

    # save upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp_path = tmp.name
        request.files["user_image"].save(tmp_path)

    try:
        output = client.run(
            "stability-ai/stable-diffusion:db21e6c9bfcaf1ddd0c9d4e3a4858be58f13a72688f6242382d8b7391c0b17e4",
            input={
                "prompt": "a fashion model wearing a stylish outfit, professional studio photo",
                "image": open(tmp_path, "rb"),
                "strength": 0.7,
                "guidance_scale": 7.5,
                "num_outputs": 1
            }
        )
        # output is a list; return the first URL
        return jsonify({"result_url": output[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
