# Flask应用配置文件

# 文件上传配置
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# OCR配置
TESSERACT_LANG = 'eng+chi_sim'  # 支持英文和简体中文

# 翻译API配置 (使用真实API时需要填写)
TRANSLATION_API_KEY = ''
TRANSLATION_API_URL = ''

# Flask配置
DEBUG = True
HOST = 'localhost'
PORT = 5000