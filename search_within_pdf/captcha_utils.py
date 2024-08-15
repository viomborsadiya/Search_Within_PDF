from captcha.image import ImageCaptcha
import random
import string
import io

def generate_captcha_code():
    characters = string.ascii_letters + string.digits
    captcha_code = ''.join(random.choice(characters) for _ in range(6))
    return captcha_code

def generate_captcha_image(captcha_code):
    image_captcha = ImageCaptcha(width=150, height=60)  # Reduced size
    captcha_image = image_captcha.generate_image(captcha_code)
    buf = io.BytesIO()
    captcha_image.save(buf, format='PNG')
    buf.seek(0)
    return buf
