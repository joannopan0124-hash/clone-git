from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
from werkzeug.utils import secure_filename
from ocr_service import perform_ocr, perform_ocr_from_bytes, init_ocr
from translate_service import translate_text
from glossary_service import (
    get_glossary_list,
    add_glossary_term,
    update_glossary_term,
    delete_glossary_term,
    import_glossary,
    export_glossary
)
from speech_service import (
    init_speech_translator,
    start_realtime_translation,
    stop_realtime_translation
)

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
    """翻译API（支持术语表）"""
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
    use_glossary = data.get('useGlossary', True)

    try:
        result = translate_text(text, source_lang, target_lang, use_glossary)

        return jsonify({
            'success': True,
            'originalText': text,
            'translatedText': result['translation'],
            'sourceLang': source_lang,
            'targetLang': target_lang,
            'glossaryMatches': result['glossary_matches'],
            'message': '翻译成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'TRANSLATE_FAILED',
            'message': f'翻译失败: {str(e)}'
        }), 500


# ==================== 术语表管理API ====================

@app.route('/api/glossary', methods=['GET'])
def get_glossary():
    """获取术语表列表"""
    source_lang = request.args.get('sourceLang')
    target_lang = request.args.get('targetLang')

    try:
        glossary = get_glossary_list(source_lang, target_lang)

        return jsonify({
            'success': True,
            'glossary': glossary,
            'count': len(glossary),
            'message': '获取术语表成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'GET_GLOSSARY_FAILED',
            'message': f'获取术语表失败: {str(e)}'
        }), 500


@app.route('/api/glossary', methods=['POST'])
def add_glossary():
    """添加术语"""
    data = request.json

    if not data or 'sourceTerm' not in data or 'targetTerm' not in data or 'sourceLang' not in data or 'targetLang' not in data:
        return jsonify({
            'success': False,
            'error_code': 'MISSING_PARAMS',
            'message': '缺少必要参数: sourceTerm, targetTerm, sourceLang, targetLang'
        }), 400

    try:
        term = add_glossary_term(
            source_term=data['sourceTerm'],
            target_term=data['targetTerm'],
            source_lang=data['sourceLang'],
            target_lang=data['targetLang'],
            description=data.get('description', ''),
            case_sensitive=data.get('caseSensitive', False),
            priority=data.get('priority', 0)
        )

        return jsonify({
            'success': True,
            'term': term,
            'message': '添加术语成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'ADD_GLOSSARY_FAILED',
            'message': f'添加术语失败: {str(e)}'
        }), 500


@app.route('/api/glossary/<term_id>', methods=['PUT'])
def update_glossary(term_id):
    """更新术语"""
    data = request.json

    if not data:
        return jsonify({
            'success': False,
            'error_code': 'MISSING_PARAMS',
            'message': '缺少更新参数'
        }), 400

    try:
        term = update_glossary_term(
            term_id=term_id,
            source_term=data.get('sourceTerm'),
            target_term=data.get('targetTerm'),
            source_lang=data.get('sourceLang'),
            target_lang=data.get('targetLang'),
            description=data.get('description'),
            case_sensitive=data.get('caseSensitive'),
            priority=data.get('priority')
        )

        if term:
            return jsonify({
                'success': True,
                'term': term,
                'message': '更新术语成功'
            })
        else:
            return jsonify({
                'success': False,
                'error_code': 'TERM_NOT_FOUND',
                'message': '术语不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'UPDATE_GLOSSARY_FAILED',
            'message': f'更新术语失败: {str(e)}'
        }), 500


@app.route('/api/glossary/<term_id>', methods=['DELETE'])
def delete_glossary(term_id):
    """删除术语"""
    try:
        success = delete_glossary_term(term_id)

        if success:
            return jsonify({
                'success': True,
                'message': '删除术语成功'
            })
        else:
            return jsonify({
                'success': False,
                'error_code': 'TERM_NOT_FOUND',
                'message': '术语不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'DELETE_GLOSSARY_FAILED',
            'message': f'删除术语失败: {str(e)}'
        }), 500


@app.route('/api/glossary/import', methods=['POST'])
def import_glossary_api():
    """批量导入术语"""
    data = request.json

    if not data or 'terms' not in data:
        return jsonify({
            'success': False,
            'error_code': 'MISSING_PARAMS',
            'message': '缺少术语列表'
        }), 400

    try:
        count = import_glossary(data['terms'])

        return jsonify({
            'success': True,
            'importedCount': count,
            'message': f'成功导入 {count} 个术语'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'IMPORT_GLOSSARY_FAILED',
            'message': f'导入术语失败: {str(e)}'
        }), 500


@app.route('/api/glossary/export', methods=['GET'])
def export_glossary_api():
    """导出术语表"""
    source_lang = request.args.get('sourceLang')
    target_lang = request.args.get('targetLang')

    try:
        glossary = export_glossary(source_lang, target_lang)

        return jsonify({
            'success': True,
            'glossary': glossary,
            'count': len(glossary),
            'message': '导出术语表成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'EXPORT_GLOSSARY_FAILED',
            'message': f'导出术语表失败: {str(e)}'
        }), 500


# ==================== 实时语音翻译API ====================

# 存储活跃的语音翻译任务
active_speech_tasks = {}
# 存储字幕历史记录
subtitle_history = {}


@app.route('/api/speech/start', methods=['POST'])
def start_speech_translation():
    """启动实时语音翻译"""
    data = request.json

    if not data or 'sourceLang' not in data or 'targetLang' not in data:
        return jsonify({
            'success': False,
            'error_code': 'MISSING_PARAMS',
            'message': '缺少必要参数: sourceLang, targetLang'
        }), 400

    source_lang = data['sourceLang']
    target_lang = data['targetLang']

    try:
        # 定义回调函数，收集字幕
        def subtitle_callback(result):
            task_id = result.get('task_id')
            if task_id not in subtitle_history:
                subtitle_history[task_id] = []
            subtitle_history[task_id].append(result)
            # 保持最近50条记录
            if len(subtitle_history[task_id]) > 50:
                subtitle_history[task_id] = subtitle_history[task_id][-50:]

        task_info = start_realtime_translation(
            source_lang=source_lang,
            target_lang=target_lang,
            callback=subtitle_callback
        )

        active_speech_tasks[task_info['task_id']] = {
            'source_lang': source_lang,
            'target_lang': target_lang,
            'status': 'running'
        }

        return jsonify({
            'success': True,
            'taskId': task_info['task_id'],
            'sourceLang': source_lang,
            'targetLang': target_lang,
            'simulation': task_info.get('simulation', False),
            'message': '实时语音翻译已启动'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'START_SPEECH_FAILED',
            'message': f'启动实时语音翻译失败: {str(e)}'
        }), 500


@app.route('/api/speech/stop/<task_id>', methods=['POST'])
def stop_speech_translation(task_id):
    """停止实时语音翻译"""
    try:
        if task_id in active_speech_tasks:
            stop_realtime_translation(task_id)
            active_speech_tasks[task_id]['status'] = 'stopped'
            del active_speech_tasks[task_id]

            return jsonify({
                'success': True,
                'message': '实时语音翻译已停止'
            })
        else:
            return jsonify({
                'success': False,
                'error_code': 'TASK_NOT_FOUND',
                'message': '任务不存在或已结束'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'STOP_SPEECH_FAILED',
            'message': f'停止实时语音翻译失败: {str(e)}'
        }), 500


@app.route('/api/speech/subtitles/<task_id>', methods=['GET'])
def get_subtitles(task_id):
    """获取字幕历史记录"""
    try:
        if task_id in subtitle_history:
            subtitles = subtitle_history[task_id]
            return jsonify({
                'success': True,
                'taskId': task_id,
                'subtitles': subtitles,
                'count': len(subtitles),
                'message': '获取字幕成功'
            })
        else:
            return jsonify({
                'success': True,
                'taskId': task_id,
                'subtitles': [],
                'count': 0,
                'message': '暂无字幕记录'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_code': 'GET_SUBTITLES_FAILED',
            'message': f'获取字幕失败: {str(e)}'
        }), 500


@app.route('/api/speech/status', methods=['GET'])
def get_speech_status():
    """获取语音翻译任务状态"""
    return jsonify({
        'success': True,
        'activeTasks': len(active_speech_tasks),
        'tasks': list(active_speech_tasks.keys()),
        'message': '获取状态成功'
    })


if __name__ == '__main__':
    init_ocr()
    init_speech_translator()
    app.run(debug=True, port=5000)