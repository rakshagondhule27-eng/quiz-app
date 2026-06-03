# QuizMind – AI-Powered Quiz Generator

Generate interactive quizzes from text or images using Google's Gemini API and PaddleOCR for text extraction.

## Features

- 📝 **Text Input**: Paste any paragraph to generate quizzes
- 📸 **Image Input**: Upload images containing text (OCR-powered text extraction)
- 🤖 **AI-Powered**: Uses Google Gemini to generate intelligent quiz questions
- 🎯 **Mixed Question Types**: Generates both MCQ and True/False questions
- 💾 **Session Storage**: Quiz state persists across requests

## Setup

### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API key:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_SECRET=your_flask_secret_key_here
PORT=5000
MAX_IMAGE_SIZE=10
```

**Getting a Gemini API Key:**
- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create a new API key
- Paste it into `.env`

### 3. Run the App

```bash
python app.py
```

The app will start on `http://localhost:5000` (or the port specified in `.env`).

## Usage

### Text Mode
1. Open the app in your browser
2. Click "📝 Paste Text"
3. Paste a paragraph (minimum ~50 words recommended)
4. Click "Generate Quiz ⚡"
5. Answer the questions

### Image Mode
1. Click "📸 Upload Image"
2. Choose an image containing text (JPG, PNG, GIF, BMP)
3. The app will:
   - Extract text from the image using PaddleOCR
   - Generate quiz questions from the extracted text
4. Answer the questions

## API Endpoints

### POST `/generate`
Generate quiz from text.
```bash
curl -s -X POST http://127.0.0.1:5000/generate \
  -H 'Content-Type: application/json' \
  -d '{"paragraph":"Your paragraph text here..."}'
```

### POST `/upload-image`
Upload an image and generate quiz from OCR-extracted text.
```bash
curl -s -X POST http://127.0.0.1:5000/upload-image \
  -F 'image=@path/to/image.jpg'
```

### GET `/question/<index>`
Fetch a specific question by index.
```bash
curl http://127.0.0.1:5000/question/0
```

### POST `/answer`
Submit an answer and get correctness feedback.
```bash
curl -s -X POST http://127.0.0.1:5000/answer \
  -H 'Content-Type: application/json' \
  -d '{"index": 0, "answer": "A. your answer"}'
```

## Architecture

```
app.py
├── generate_questions(paragraph)    # Uses Gemini to create quiz from text
├── extract_text_from_image(bytes)   # Uses PaddleOCR to extract text from images
├── /generate (POST)                  # Text-to-quiz endpoint
├── /upload-image (POST)              # Image-to-quiz endpoint
├── /question/<index> (GET)           # Fetch question
└── /answer (POST)                    # Submit and check answer

templates/index.html                  # Single-page app UI
static/js/app.js                      # Frontend logic & API calls
static/css/style.css                  # Styling (dark mode, animations)
```

## Troubleshooting

**Port already in use?**
```bash
PORT=5001 python app.py
```

**PaddleOCR download slow?**
PaddleOCR downloads models on first run (~100MB). This is normal; subsequent runs are fast.

**Image not recognized?**
- Ensure the image is clear and well-lit
- Text should be at least 50-100 words
- Supported formats: JPG, PNG, GIF, BMP

**Gemini API errors?**
- Verify `GEMINI_API_KEY` is correct in `.env`
- Check your API quota at [Google AI Studio](https://aistudio.google.com)

## Development

### Run in Production Mode

```bash
# Set Flask environment
export FLASK_ENV=production
# Use a WSGI server like Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Debugging

Enable verbose logging:
```python
# In app.py, before app.run():
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

- **flask** – Web framework
- **google-generativeai** / **google-genai** – Gemini API client
- **paddleocr** – OCR for text extraction
- **opencv-python** – Image processing
- **Pillow** – Image handling
- **python-dotenv** – Environment variable management

## License

MIT

## Support

For issues or feature requests, check the GitHub Issues page.
