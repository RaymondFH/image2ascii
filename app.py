from flask import Flask, request, jsonify, render_template
from PIL import Image
import io

app = Flask(__name__)

ASCII_CHARS = "@%#*+=-:. "
WIDTH = 100  # Desired width of ASCII art

def image_to_ascii(image):
    # Convert image to grayscale
    image = image.convert("L")
    
    # Resize image maintaining the aspect ratio
    aspect_ratio = image.height / image.width
    new_height = int(aspect_ratio * WIDTH)
    image = image.resize((WIDTH, new_height))

    # Map pixels to ASCII characters
    pixels = image.getdata()
    ascii_str = ""
    for pixel_value in pixels:
        ascii_str += ASCII_CHARS[pixel_value // 32]  # 255/8 = ~32

    # Split string into multiple lines
    ascii_str_len = len(ascii_str)
    ascii_img = "\n".join([ascii_str[i:i + WIDTH] for i in range(0, ascii_str_len, WIDTH)])
    return ascii_img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))

    ascii_art = image_to_ascii(image)
    return jsonify({"ascii_art": ascii_art})

if __name__ == '__main__':
    app.run(debug=True)
