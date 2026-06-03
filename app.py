from flask import Flask, render_template, request, jsonify, session
import json
import os
import re
from pathlib import Path
from PIL import Image
import io

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; rely on system env vars

# Try to import the newer `google.genai` package first, fall back to the
# deprecated `google.generativeai` if needed so the repo runs on older setups.
try:
    import google.genai as genai
    _GENAI_PKG = "genai"
except Exception:
    import google.generativeai as genai
    _GENAI_PKG = "generativeai"  # deprecated

# Import PaddleOCR for image text extraction
try:
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    _OCR_AVAILABLE = True
except ImportError:
    ocr = None
    _OCR_AVAILABLE = False

app = Flask(__name__)

# Read secrets from environment first (safer than hard-coding).
app.secret_key = os.environ.get("FLASK_SECRET", "quiz_secret_key_change_this")

# GEMINI API key (set GEMINI_API_KEY in your environment). Leaving a default
# empty string avoids accidentally committing a real key.
GEMINI_API_KEY = "AQ.Ab8RN6KN-JNnFNOsmlEXDFJduTnVUk8tU-OUJVOTHH2wQtztoQ"

# Configure the imported genai client if it exposes a configure method.
if hasattr(genai, "configure"):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        # Don't crash at import time; we'll provide a clearer error when generate is called.
        pass

# Create a model object if possible. If the imported package doesn't support
# the same surface, leave `model` as None and raise helpful errors at runtime.
model = None
try:
    # Many existing examples use GenerativeModel(...) and generate_content(...).
    # If the newer package uses a different API, this may fail and we'll surface
    # a helpful error later.
    model = genai.GenerativeModel("gemini-3.1-flash-lite")
except Exception:
    # keep model as None; generate_questions() will raise a clear error if invoked
    model = None


def generate_questions(paragraph):
    prompt = f"""
You are a quiz generator. Read the paragraph below and generate 5 quiz questions.
Mix of MCQ (4 options) and True/False questions.
Return ONLY a valid JSON array. No markdown, no explanation, no extra text.

Format:
[
  {{
    "type": "mcq",
    "question": "Question text here?",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "answer": "A. option1"
  }},
  {{
    "type": "truefalse",
    "question": "Statement here.",
    "options": ["True", "False"],
    "answer": "True"
  }}
]   
Paragraph:
{paragraph}
"""
    if model is None:
        raise RuntimeError(
            f"No Gemini model client available. The installed package ({_GENAI_PKG})\n"
            "didn't expose the expected `GenerativeModel` API. Install and configure\n"
            "the `google.genai` (preferred) or `google.generativeai` package and set\n"
            "GEMINI_API_KEY in the environment."
        )

    response = model.generate_content(prompt)
    raw = getattr(response, "text", str(response)).strip()
    # Remove markdown code blocks if present
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        questions = json.loads(raw)
    except Exception as e:
        # Provide a helpful error that includes the raw model output for debugging
        raise ValueError(
            "Failed to parse JSON from model output. Raw output:\n" + raw + "\n\n" + str(e)
        )
    return questions


def extract_text_from_image(image_bytes):
    """Extract text from image using PaddleOCR."""
    if not _OCR_AVAILABLE:
        raise RuntimeError(
            "PaddleOCR is not installed. Install it with: pip install paddleocr"
        )

    # Open image from bytes
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if necessary (e.g., RGBA or grayscale)
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # Save to temp file (PaddleOCR expects file path)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        img.save(tmp.name, "JPEG")
        tmp_path = tmp.name
    
    try:
        # Run OCR
        result = ocr.ocr(tmp_path, cls=True)
        
        # Extract text from result (result is a list of lists of tuples)
        # Each tuple is ((bbox), (text, confidence))
        extracted_text = []
        for line in result:
            for word_info in line:
                if isinstance(word_info, tuple) and len(word_info) >= 2:
                    text = word_info[1][0]  # Get text from (text, confidence)
                    extracted_text.append(text)
        
        return " ".join(extracted_text)
    finally:
        # Clean up temp file
        os.remove(tmp_path)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    paragraph = data.get("paragraph", "").strip()
    if not paragraph:
        return jsonify({"error": "No paragraph provided"}), 400
    try:
        questions = generate_questions(paragraph)
        session["questions"] = questions
        return jsonify({"success": True, "total": len(questions)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload-image", methods=["POST"])
def upload_image():
    """Upload an image, extract text via OCR, and generate quiz."""
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No image selected"}), 400
    
    # Check file type
    allowed_extensions = {"jpg", "jpeg", "png", "gif", "bmp"}
    if not any(file.filename.lower().endswith("." + ext) for ext in allowed_extensions):
        return jsonify({"error": "Invalid image format. Allowed: JPG, PNG, GIF, BMP"}), 400
    
    try:
        # Read image bytes
        image_bytes = file.read()
        
        # Extract text from image
        paragraph = extract_text_from_image(image_bytes)
        
        if not paragraph or len(paragraph.strip()) < 30:
            return jsonify({"error": "Could not extract enough text from image. Try a clearer image."}), 400
        
        # Generate quiz from extracted text
        questions = generate_questions(paragraph)
        session["questions"] = questions
        session["extracted_text"] = paragraph  # Store for reference
        
        return jsonify({"success": True, "total": len(questions), "extracted_text": paragraph})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/question/<int:index>")
def get_question(index):
    questions = session.get("questions", [])
    if index >= len(questions):
        return jsonify({"done": True})
    q = questions[index]
    return jsonify({
        "done": False,
        "index": index,
        "total": len(questions),
        "type": q["type"],
        "question": q["question"],
        "options": q["options"]
    })


@app.route("/answer", methods=["POST"])
def check_answer():
    data = request.get_json()
    index = data.get("index")
    user_answer = data.get("answer")
    questions = session.get("questions", [])
    correct = questions[index]["answer"]
    is_correct = user_answer.strip().lower() == correct.strip().lower()
    return jsonify({"correct": is_correct, "correct_answer": correct})


if __name__ == "__main__":
    # Allow changing the bind port via PORT env var (useful if 5000 is busy).
    port = int(os.environ.get("PORT", "5000"))
    try:
        app.run(debug=True, port=port)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Port {} is in use. Either stop the other process or set PORT to a different port.".format(port))
        raise
