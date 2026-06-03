# QuizMind Setup Checklist

## Before Running

- [ ] Clone/download the repository
- [ ] Navigate to the project directory: `cd /Users/yash/Downloads/quiz_app`
- [ ] Copy `.env.example` to `.env`: `cp .env.example .env`

## Configure Environment

Edit `.env` and add your API key:

```bash
# .env
GEMINI_API_KEY=sk_your_actual_key_here
FLASK_SECRET=some_random_secret_string
PORT=5000
```

**Get Gemini API Key:**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key to `.env`

## Install & Run

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Run the app
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Then open `http://localhost:5000` in your browser.

## First Run with Images

⚠️ **Note:** PaddleOCR downloads models (~100MB) on first use. This takes a few minutes. Subsequent runs are fast.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Port 5000 in use` | Set `PORT=5001` in `.env` or run `PORT=5001 python app.py` |
| `ModuleNotFoundError: paddleocr` | Run `python -m pip install paddleocr` |
| `No Gemini model available` | Check `GEMINI_API_KEY` in `.env` is not empty |
| Image upload fails | Try a clearer image with text; min 50 words recommended |

## File Structure

```
quiz_app/
├── .env                          # ← Add your API key here (create from .env.example)
├── .env.example                  # ← Template for .env
├── .github/
│   └── copilot-instructions.md   # AI agent guidance
├── app.py                        # Flask app + OCR + Gemini integration
├── requirements.txt              # Python dependencies
├── README.md                     # Full documentation
├── templates/
│   └── index.html                # Web UI
├── static/
│   ├── js/app.js                # Frontend logic
│   └── css/style.css            # Styling
└── .gitignore                    # Git ignore rules
```

## Key Features Added

✅ **Text Mode**: Paste paragraph → Generate quiz  
✅ **Image Mode**: Upload image → OCR extract text → Generate quiz  
✅ **Environment Variables**: All secrets in `.env`  
✅ **Error Handling**: Clear error messages for missing OCR, API keys, etc.  
✅ **Image Preview**: See selected image before upload  
✅ **Tab UI**: Switch between text and image input  

## Next Steps (Optional)

- Add tests: Create `tests/test_app.py` with pytest
- Deploy: Use Gunicorn + Nginx/Heroku for production
- Enhance: Add more languages for OCR, quiz customization, etc.

## Questions?

Check `README.md` for API examples and debugging tips.
