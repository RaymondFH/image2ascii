import logging
from flask import Flask, request, jsonify, render_template
from PIL import Image
import io

app = Flask(__name__)

ASCII_CHARS = "@%#*+=-:. "
WIDTH = 100  # Desired width of ASCII art

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def image_to_ascii(image):
    try:
        image = image.convert("L")
        aspect_ratio = image.height / image.width
        new_height = int(aspect_ratio * WIDTH)
        image = image.resize((WIDTH, new_height))
        pixels = image.getdata()
        ascii_str = "".join([ASCII_CHARS[pixel_value // 32] for pixel_value in pixels])
        ascii_img = "\n".join([ascii_str[i:i + WIDTH] for i in range(0, len(ascii_str), WIDTH)])
        return ascii_img
    except Exception as e:
        logger.error(f"Error converting image to ASCII: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            logger.warning("No image part in the request files")
            return jsonify({"error": "No image uploaded"}), 400
        image_file = request.files['image']
        if image_file.filename == '':
            logger.warning("No selected file")
            return jsonify({"error": "No selected file"}), 400
        image = Image.open(io.BytesIO(image_file.read()))
        ascii_art = image_to_ascii(image)
        return jsonify({"ascii_art": ascii_art})
    except IOError:
        logger.error("Invalid image file")
        return jsonify({"error": "Invalid image file"}), 400
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
