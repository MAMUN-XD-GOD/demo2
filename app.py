from flask import Flask, render_template, request, jsonify
from PIL import Image
import numpy as np
import cv2
import io
import time

app = Flask(__name__)

def safe_int(x, a, b):
    return max(a, min(b, int(x)))

def analyze_chart(image_bytes, mode):
    start = time.time()

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = np.array(img)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # ----- Quality checks -----
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    clarity = "GOOD" if blur > 120 else "LOW"

    h, w = gray.shape

    # ----- Trend proxy -----
    left = np.mean(gray[:, :w//2])
    right = np.mean(gray[:, w//2:])
    trend = "UP" if right > left else "DOWN"

    # ----- Momentum / energy -----
    mid = gray[int(h*0.35):int(h*0.65), int(w*0.3):int(w*0.7)]
    energy = np.std(mid)

    # ----- Confidence calculation -----
    confidence = safe_int(energy / 2.5, 55, 88)

    if clarity == "LOW":
        confidence -= 10

    latency = round(time.time() - start, 2)

    if mode == "binary":
        return {
            "engine": "ChartMind AI",
            "market": "Binary",
            "direction": "CALL" if trend == "UP" else "PUT",
            "expiry": "Next 1–2 candle",
            "confidence": f"{confidence}%",
            "clarity": clarity,
            "note": "Late entry increases risk",
            "analysis_time": f"{latency}s"
        }

    else:
        return {
            "engine": "ChartMind AI",
            "market": "Forex / Crypto",
            "direction": "BUY" if trend == "UP" else "SELL",
            "entry_zone": "Near current structure",
            "tp_zone": "Next liquidity / structure",
            "sl_zone": "Beyond recent swing",
            "confidence": f"{confidence}%",
            "clarity": clarity,
            "analysis_time": f"{latency}s"
        }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("chart")
        mode = request.form.get("mode")

        if not file:
            return jsonify({"error": "No image uploaded"})

        try:
            result = analyze_chart(file.read(), mode)
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "engine": "ChartMind AI",
                "error": "Chart could not be analyzed safely"
            })

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
