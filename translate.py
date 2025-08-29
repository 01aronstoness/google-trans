import sys
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import html
import urllib.parse as parse
from enum import Enum
from googletrans import Translator, LANGUAGES

# Monkey patch for googletrans in Python 3.11+
if sys.version_info >= (3, 11):
    import googletrans
    import googletrans.gtoken
    googletrans.gtoken.html = html
    googletrans.gtoken.parse = parse

app = FastAPI(title="Translation API", description="Auto-detect language and translate to selected target language")

# Initialize Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Initialize translator
translator = Translator()

# Step 1: Define Enum for language codes
class LanguageEnum(str, Enum):
    # This uses all known languages
    locals().update({code: code for code in LANGUAGES})

@app.post("/translate")
async def translate_text(
    text: str = Form(..., description="Text to translate"),
    dest_language: LanguageEnum = Form(..., description="Target language code")
):
    """
    Translate text from auto-detected language to target language
    
    - **text**: Input text to translate (auto-detects source language)
    - **dest_language**: Target language code (dropdown in Swagger UI)
    
    Returns JSON with translation results including detected source language.
    """
    try:
        detected = translator.detect(text)
        translation = translator.translate(text, dest=dest_language.value)

        return {
            "original_text": text,
            "translated_text": translation.text,
            "source_language": detected.lang,
            "source_language_name": LANGUAGES.get(detected.lang, "Unknown"),
            "target_language": dest_language.value,
            "target_language_name": LANGUAGES.get(dest_language.value, "Unknown"),
            "confidence": detected.confidence
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/languages")
async def get_languages():
    """
    Returns a dictionary of language codes and their names.
    """
    return LANGUAGES

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request): # Add Request here
    """
    Serves the main HTML page for the translation UI from an external file.
    """
    return templates.TemplateResponse("./index.html", {"request": request}) # Render the template

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3216)
