import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

ASCII_CHARS = "@%#*+=-:. "
WIDTH = 100  # Desired width of ASCII art

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set maximum allowed payload to 3 MB
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 MB in bytes

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

@app.route('/api/upload', methods=['POST'])
def upload_image():
    try:
        logger.info("Received upload request")
        if 'image' not in request.files:
            logger.warning("No image part in the request files")
            return jsonify({"error": "No image uploaded"}), 400
        image_file = request.files['image']
        if image_file.filename == '':
            logger.warning("No selected file")
            return jsonify({"error": "No selected file"}), 400
        logger.info(f"Processing file: {image_file.filename}")
        image = Image.open(io.BytesIO(image_file.read()))
        ascii_art = image_to_ascii(image)
        logger.info("ASCII art generated successfully")
        return jsonify({"ascii_art": ascii_art})
    except IOError as e:
        logger.error(f"Invalid image file: {e}")
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 3 MB."}), 413