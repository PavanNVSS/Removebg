import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io
import requests
from io import BytesIO

app = Flask(__name__)
CORS(app)

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    try:
        print(f"Request files: {request.files}")
        print(f"Request form data: {request.form}")

        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            print(f"Received file: {file.filename}")
            input_image = Image.open(file)

        elif 'url' in request.form:
            url = request.form['url']
            print(f"Received URL: {url}")
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                input_image = Image.open(BytesIO(response.content))
            except requests.exceptions.RequestException as e:
                return jsonify({'error': 'Failed to fetch image from the provided URL', 'details': str(e)}), 400
            except IOError as e:
                return jsonify({'error': 'Invalid image format from the URL', 'details': str(e)}), 400

        else:
            return jsonify({'error': 'No file or URL provided'}), 400

        # Remove background from the input image
        output_image = remove(input_image)

        # Save the result to a BytesIO stream
        output_stream = io.BytesIO()
        output_image.save(output_stream, format="PNG")
        output_stream.seek(0)

        return send_file(output_stream, mimetype='image/png', as_attachment=True, download_name='result.png')

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

