from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from ocr_service import perform_ocr
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
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件部分'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '不支持的文件格式'}), 400

    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    timestamp = int(os.times().elapsed * 1000)
    filename = secure_filename(file.filename)
    unique_filename = f"{timestamp}_{file_id}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    file.save(file_path)

    # 判断文件类型
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
    """OCR识别API"""
    data = request.json

    if not data or 'filePath' not in data:
        return jsonify({'success': False, 'message': '缺少文件路径参数'}), 400

    file_path = data['filePath']

    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    try:
        text, confidence = perform_ocr(file_path)

        # 删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            'success': True,
            'text': text,
            'confidence': confidence,
            'message': 'OCR识别成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'OCR识别失败: {str(e)}'
        }), 500


@app.route('/api/translate', methods=['POST'])
def translate():
    """翻译API"""
    data = request.json

    if not data or 'text' not in data or 'sourceLang' not in data or 'targetLang' not in data:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400

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
            'message': f'翻译失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)