import wcocr
import os
import uuid
import base64
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins="*")

wcocr.init("/app/wx/opt/wechat/wxocr", "/app/wx/opt/wechat")

@app.route('/', methods=['GET'])
def index():
    curl_example = """ curl --location 'http(s)://APP_HOST/file-ocr' --form 'image=@"/tmp/file.png"' -s | awk -F'\t\t' '{print $1}'"""
    return jsonify({
        "ussage": [
            { "method": "POST", "url": "/ocr", "body": { "image": "base64_image_string" }},
            { "method": "POST", "url": "/file-ocr", "form-field": { "image": "image_file_data" }, "example": curl_example },
        ]
    }), 200


def write_to_file(image_bytes: bytes):
    if image_bytes is None:
        return None
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Generate unique filename and save image
    filename = os.path.join(temp_dir, f"{str(uuid.uuid4())}")
    try:
        # image_bytes = base64.b64decode(image_data)
        with open(filename, 'wb') as f:
            f.write(image_bytes)
        return filename
    except:
        return None

@app.route('/file-ocr', methods=['POST'])
def ocr_file():
    filename = None
    content = '\t\t'.join(['text', 'rate', 'top', 'left', 'right', 'bottom']) + '\n'
    try:
        file = request.files.get('image')
        filename = write_to_file(file.read())
        if filename is None:
            return make_response(content, 200)
        # Process image with OCR
        result = dict(wcocr.ocr(filename))
        ocr_response = result.get('ocr_response', [])
        text = ""
        for item in ocr_response:
            datas = [item["text"], item["rate"], item['top'], item["left"], item["right"], item["bottom"]]
            line = '\t\t'.join([str(x) for x in datas]) + '\n'
            content += line + '\n'
            text += item["text"]
        return make_response(text + '\n' + content, 200)
    except Exception as e:
        return make_response(content, 200)

    finally:
        # Clean up temp file
        if filename is not None and os.path.exists(filename):
            os.remove(filename)


@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        # Get base64 image from request
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Create temp directory if not exists
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Generate unique filename and save image
        filename = None
        try:
            image_bytes = base64.b64decode(image_data)
            filename = write_to_file(image_bytes)
            if filename is None:
                return jsonify({'error': 'Save file failed.'}), 500
            # Process image with OCR
            result = wcocr.ocr(filename)
            return jsonify({'result': result})

        finally:
            # Clean up temp file
            if filename is not None and os.path.exists(filename):
                os.remove(filename)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)