from PIL import Image, ImageEnhance
import pytesseract
from contra_engine import analyze_text
import logging

# Explicitly configure the Tesseract executable path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image: Image.Image) -> str:
    """
    Extracts text from a given image using Tesseract OCR with preprocessing.
    """
    try:
        # 1. Convert image to RGB (to ensure consistent behavior if image has alpha)
        processed = image.convert("RGB")
        
        # 2. Convert to grayscale
        processed = processed.convert("L")
        
        # 3. Upscale the image 3x
        # We use LANCZOS for high quality resampling
        processed = processed.resize(
            (processed.width * 3, processed.height * 3), 
            Image.Resampling.LANCZOS
        )
        
        # 4. Improve contrast
        enhancer = ImageEnhance.Contrast(processed)
        processed = enhancer.enhance(2.0)
        
        # 5. Apply threshold/binarization
        threshold = 128
        processed = processed.point(lambda p: 255 if p > threshold else 0)
        
        # 6. Run Tesseract with page segmentation mode 6
        extracted_text = pytesseract.image_to_string(processed, config="--psm 6")
        
        return extracted_text.strip()
    except Exception as e:
        if "is not installed" in str(e) or "tesseract" in str(e).lower() or isinstance(e, pytesseract.pytesseract.TesseractNotFoundError):
            return "ERROR_TESSERACT_MISSING"
        logging.error(f"Tesseract OCR Error: {e}")
        return ""

def normalize_ocr_text(text: str) -> str:
    """
    Normalizes OCR text (often lists of keys and values) into readable sentences
    that the text contradiction engine can easily parse.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    normalized_sentences = []
    current_key = None
    current_values = []
    
    for line in lines:
        if line.endswith(':'):
            if current_key and current_values:
                val_str = " and ".join(current_values)
                normalized_sentences.append(f"{current_key} is {val_str}.")
            current_key = line[:-1].strip()
            current_values = []
        elif ':' in line:
            if current_key and current_values:
                val_str = " and ".join(current_values)
                normalized_sentences.append(f"{current_key} is {val_str}.")
                current_key = None
                current_values = []
                
            parts = line.split(':', 1)
            k = parts[0].strip()
            v = parts[1].strip()
            normalized_sentences.append(f"{k} is {v}.")
        else:
            if current_key:
                current_values.append(line)
            else:
                if not line.endswith('.'):
                    normalized_sentences.append(f"{line}.")
                else:
                    normalized_sentences.append(line)
                    
    if current_key and current_values:
        val_str = " and ".join(current_values)
        normalized_sentences.append(f"{current_key} is {val_str}.")
        
    return " ".join(normalized_sentences)

def analyze_image(image: Image.Image) -> dict:
    """
    Extracts text from an image and runs it through the ContraCheck text engine.
    """
    extracted_text = extract_text_from_image(image)
    
    if extracted_text == "ERROR_TESSERACT_MISSING":
        return {"error": "Tesseract OCR is not installed or configured."}
        
    if not extracted_text.strip():
        return {
            "extracted_text": "",
            "analysis": None
        }
        
    normalized_text = normalize_ocr_text(extracted_text)
    analysis = analyze_text(normalized_text)
    
    return {
        "extracted_text": extracted_text, # Return original raw text for the UI preview
        "analysis": analysis
    }
