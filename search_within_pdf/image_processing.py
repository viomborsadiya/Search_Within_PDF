from PIL import Image, ImageEnhance
import pytesseract

# Specify the path to the Tesseract executable if it's not in your PATH
# Update the path below if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # For Windows

def preprocess_image(image_path):
    """
    Preprocesses the image to improve OCR accuracy.
    """
    image = Image.open(image_path)
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # Increase contrast
    image = image.point(lambda p: p > 128 and 255)
    return image

def extract_text_from_image(image_path):
    """
    Extracts text from an image using pytesseract.
    """
    image = preprocess_image(image_path)
    text = pytesseract.image_to_string(image)
    return text.strip()
