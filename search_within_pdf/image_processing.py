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

    # Resize the image for better OCR performance
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)  # Changed ANTIALIAS to LANCZOS
    image = image.convert('L')  # Convert to grayscale

    # Increase contrast and apply thresholding
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)  # Increase contrast
    image = image.point(lambda p: p > 150 and 255)  # Apply binary threshold

    return image

def extract_text_from_image(image_path):
    """
    Extracts text from an image using pytesseract.
    """
    image = preprocess_image(image_path)

    # Use Tesseract configuration to improve accuracy
    custom_config = r'--oem 3 --psm 6'  # Default OCR Engine Mode and Page Segmentation Mode
    text = pytesseract.image_to_string(image, config=custom_config)

    return text.strip()
