from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from ocr_service import perform_ocr, perform_ocr_from_bytes, init_ocr
from translate_service import translate_text

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件API"""
    file = request.files.get('file') or request.files.get('image')

    if not file:
        return jsonify({'success': False, 'error_code': 'NO_FILE', 'message': '没有文件部分'}), 400

    if file.filename == '':
        return jsonify({'success': False, 'error_code': 'EMPTY_FILENAME', 'message': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error_code': 'INVALID_FORMAT', 'message': '不支持的文件格式'}), 400

    file_id = str(uuid.uuid4())
    timestamp = int(os.times().elapsed * 1000)
    filename = secure_filename(file.filename)
    unique_filename = f"{timestamp}_{file_id}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    file.save(file_path)

    file_ext = filename.rsplit('.', 1)[1].lower()
    file_type = 'pdf' if file_ext == 'pdf' else 'image'

    return jsonify({
        'success': True,
        'fileId': file_id,
        'fileName': filename,
        'filePath': file_path,
        'fileType': file_type,
        'message': '文件上传成功'
    })


@app.route('/api/ocr', methods=['POST'])
def ocr():
    """OCR识别API - 接受图片上传"""
    file = request.files.get('file') or request.files.get('image')

    if not file:
        return jsonify({
            'success': False,
            'error_code': 'NO_FILE',
            'message': '缺少图片文件，请通过form-data上传文件'
        }), 400

    if file.filename == '':
        return jsonify({
            'success': False,
            'error_code': 'EMPTY_FILENAME',
            'message': '没有选择文件'
        }), 400

    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in {'png', 'jpg', 'jpeg'}:
        return jsonify({
            'success': False,
            'error_code': 'INVALID_FORMAT',
            'message': '不支持的文件格式，仅支持PNG和JPG图片'
        }), 400

    try:
        image_bytes = file.read()

        if len(image_bytes) == 0:
            return jsonify({
                'success': False,
                'error_code': 'EMPTY_FILE',
                'message': '文件内容为空'
            }), 400

        text, confidence = perform_ocr_from_bytes(image_bytes)

        return jsonify({
            'success': True,
            'text': text,
            'confidence': confidence,
            'message': 'OCR识别成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'OCR_FAILED',
            'message': f'OCR识别失败: {str(e)}'
        }), 500


@app.route('/api/translate', methods=['POST'])
def translate():
    """翻译API"""
    data = request.json

    if not data or 'text' not in data or 'sourceLang' not in data or 'targetLang' not in data:
        return jsonify({
            'success': False,
            'error_code': 'MISSING_PARAMS',
            'message': '缺少必要参数'
        }), 400

    text = data['text']
    source_lang = data['sourceLang']
    target_lang = data['targetLang']

    try:
        translated_text = translate_text(text, source_lang, target_lang)

        return jsonify({
            'success': True,
            'originalText': text,
            'translatedText': translated_text,
            'sourceLang': source_lang,
            'targetLang': target_lang,
            'message': '翻译成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'TRANSLATE_FAILED',
            'message': f'翻译失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    init_ocr()
    app.run(debug=True, port=5000)