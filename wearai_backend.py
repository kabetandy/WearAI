from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route("/test", methods=["GET"])
def test():
    # Always healthy
    return jsonify({"ok": True}), 200

@app.route("/tryon", methods=["POST"])
def tryon():
    """
    Demo stub: ignores the upload and returns a placeholder image.
    Swap this URL out later for your real AI-generated image endpoint.
    """
    if "user_image" not in request.files:
        return jsonify({"error": "Missing user_image"}), 400

    # (Optionally save it if you want to inspect uploads)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        request.files["user_image"].save(tmp.name)

    # Return a fixed demo image URL
    placeholder = "https://via.placeholder.com/512x512.png?text=WearAI+Demo"
    return jsonify({"result_url": placeholder})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
