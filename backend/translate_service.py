"""
火山引擎翻译服务模块

使用火山引擎机器翻译API进行文本翻译
文档: https://www.volcengine.com/docs/4640/65067
"""

import os
import json
import requests
from datetime import datetime
import hashlib
import hmac
import urllib.parse


class VolcEngineTranslator:
    """火山引擎翻译客户端"""

    def __init__(self, access_key=None, secret_key=None):
        """
        初始化翻译客户端

        Args:
            access_key: 火山引擎 AccessKey ID
            secret_key: 火山引擎 Secret Access Key
        """
        self.access_key = access_key or os.environ.get('VOLC_ACCESS_KEY', '')
        self.secret_key = secret_key or os.environ.get('VOLC_SECRET_KEY', '')
        self.host = 'translate.volcengineapi.com'
        self.region = 'cn-north-1'
        self.service = 'translate'
        self.version = '2020-06-01'
        self.action = 'TranslateText'

        if not self.access_key or not self.secret_key:
            raise ValueError('请配置火山引擎API密钥，设置环境变量 VOLC_ACCESS_KEY 和 VOLC_SECRET_KEY')

    def _sign_request(self, method, path, query, body):
        """
        生成签名

        Args:
            method: HTTP方法
            path: URI路径
            query: 查询参数
            body: 请求体

        Returns:
            dict: 包含签名的请求头
        """
        now = datetime.utcnow()
        date_str = now.strftime('%Y%m%dT%H%M%SZ')
        date_short = now.strftime('%Y%m%d')

        # 步骤1: 创建规范请求
        canonical_query = urllib.parse.urlencode(sorted(query.items()))
        canonical_headers = f'content-type:application/json\nhost:{self.host}\nx-content-sha256:{hashlib.sha256(body.encode()).hexdigest()}\nx-date:{date_str}\n'
        signed_headers = 'content-type;host;x-content-sha256;x-date'
        body_hash = hashlib.sha256(body.encode()).hexdigest()

        canonical_request = f'{method}\n{path}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{body_hash}'

        # 步骤2: 创建待签名字符串
        credential_scope = f'{date_short}/{self.region}/{self.service}/request'
        string_to_sign = f'HMAC-SHA256\n{date_str}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}'

        # 步骤3: 计算签名
        k_date = hmac.new(self.secret_key.encode(), date_short.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, 'request'.encode(), hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

        # 步骤4: 创建Authorization头
        authorization = f'HMAC-SHA256 Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'

        headers = {
            'Content-Type': 'application/json',
            'Host': self.host,
            'X-Date': date_str,
            'X-Content-Sha256': body_hash,
            'Authorization': authorization
        }

        return headers

    def translate(self, text, source_lang=None, target_lang='zh'):
        """
        翻译文本

        Args:
            text: 待翻译文本
            source_lang: 源语言代码（可选，不指定则自动检测）
            target_lang: 目标语言代码

        Returns:
            str: 翻译后的文本

        Raises:
            Exception: 翻译失败时抛出异常
        """
        method = 'POST'
        path = '/'
        query = {
            'Action': self.action,
            'Version': self.version
        }

        # 构建请求体
        req_body = {
            'TargetLanguage': target_lang,
            'TextList': [text]
        }
        if source_lang:
            req_body['SourceLanguage'] = source_lang

        body = json.dumps(req_body)

        # 生成签名头
        headers = self._sign_request(method, path, query, body)

        # 发送请求
        url = f'https://{self.host}{path}?{urllib.parse.urlencode(sorted(query.items()))}'
        response = requests.post(url, headers=headers, data=body, timeout=10)

        if response.status_code != 200:
            raise Exception(f'翻译请求失败，状态码: {response.status_code}, 响应: {response.text}')

        result = response.json()

        # 检查错误
        error = result.get('ResponseMetadata', {}).get('Error')
        if error:
            raise Exception(f'翻译失败: {error.get("Message", str(error))}')

        # 获取翻译结果
        translation_list = result.get('TranslationList', [])
        if not translation_list:
            raise Exception('翻译结果为空')

        return translation_list[0].get('Translation', '')


# 全局翻译客户端实例
translator = None


def init_translator():
    """初始化翻译客户端"""
    global translator
    if translator is None:
        translator = VolcEngineTranslator()
    return translator


def translate_text(text, source_lang, target_lang):
    """
    翻译文本

    Args:
        text: 待翻译文本
        source_lang: 源语言代码
        target_lang: 目标语言代码

    Returns:
        str: 翻译后的文本
    """
    t = init_translator()

    # 语言代码映射（火山引擎使用的语言代码）
    lang_map = {
        'zh': 'zh',      # 中文
        'en': 'en',      # 英语
        'ja': 'ja',      # 日语
        'ko': 'ko',      # 韩语
        'de': 'de',      # 德语
        'fr': 'fr',      # 法语
        'es': 'es',      # 西班牙语
        'pt': 'pt',      # 葡萄牙语
        'ru': 'ru',      # 俄语
        'it': 'it',      # 意大利语
        'vi': 'vi',      # 越南语
        'th': 'th',      # 泰语
        'ar': 'ar',      # 阿拉伯语
        'auto': None,    # 自动检测（不指定源语言）
    }

    # 获取火山引擎语言代码
    volc_source = lang_map.get(source_lang, source_lang)
    volc_target = lang_map.get(target_lang, target_lang)

    # 如果源语言和目标语言相同，直接返回原文
    if volc_source and volc_source == volc_target:
        return text

    return t.translate(text, volc_source, volc_target)