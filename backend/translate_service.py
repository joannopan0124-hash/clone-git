"""
翻译服务模块

支持火山引擎机器翻译API，未配置密钥时使用模拟翻译模式
文档: https://www.volcengine.com/docs/4640/65067

支持术语表功能，作为翻译记忆库使用
"""

import os
import json
import requests
import random
from datetime import datetime
import hashlib
import hmac
import urllib.parse
from glossary_service import apply_glossary_to_translation, restore_glossary_terms


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
        self.simulation_mode = False

        if not self.access_key or not self.secret_key:
            print('警告: 未配置火山引擎API密钥，将使用模拟翻译模式')
            self.simulation_mode = True

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

    def _simulate_translate(self, text, source_lang, target_lang):
        """
        模拟翻译（用于演示）

        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            str: 模拟翻译结果
        """
        if not text or not text.strip():
            return text

        # 常见词汇翻译表
        en_to_zh = {
            'hello': '你好',
            'world': '世界',
            'welcome': '欢迎',
            'translation': '翻译',
            'system': '系统',
            'image': '图片',
            'text': '文字',
            'recognition': '识别',
            'document': '文档',
            'technology': '技术',
            'the': '',
            'is': '是',
            'are': '是',
            'a': '一个',
            'an': '一个',
            'i': '我',
            'we': '我们',
            'you': '你',
            'he': '他',
            'she': '她',
            'it': '它',
            'they': '他们',
            'in': '在',
            'on': '在',
            'at': '在',
            'and': '和',
            'with': '与',
            'of': '的',
            'for': '为了',
            'to': '到',
            'from': '从',
            'this': '这',
            'that': '那',
            'these': '这些',
            'those': '那些',
            'have': '有',
            'has': '有',
            'had': '有',
            'can': '可以',
            'will': '会',
            'would': '会',
            'should': '应该',
            'must': '必须',
            'do': '做',
            'does': '做',
            'did': '做了',
            'not': '不',
            'no': '不',
            'yes': '是',
            'good': '好',
            'bad': '坏',
            'new': '新',
            'old': '旧',
            'big': '大',
            'small': '小',
            'many': '很多',
            'much': '很多',
            'more': '更多',
            'less': '更少',
            'time': '时间',
            'day': '天',
            'year': '年',
            'people': '人',
            'man': '男人',
            'woman': '女人',
            'child': '孩子',
            'work': '工作',
            'life': '生活',
            'love': '爱',
            'book': '书',
            'word': '词',
            'name': '名字',
            'line': '行',
            'number': '数字',
            'way': '方式',
            'day': '天',
            'today': '今天',
            'tomorrow': '明天',
            'yesterday': '昨天',
            'now': '现在',
            'then': '然后',
            'here': '这里',
            'there': '那里',
            'very': '非常',
            'just': '只是',
            'also': '也',
            'too': '也',
            'so': '所以',
            'but': '但是',
            'if': '如果',
            'because': '因为',
            'when': '当',
            'where': '哪里',
            'what': '什么',
            'who': '谁',
            'how': '如何',
            'which': '哪个',
            'all': '所有',
            'some': '一些',
            'any': '任何',
            'each': '每个',
            'every': '每个',
            'other': '其他',
            'another': '另一个',
            'same': '相同',
            'different': '不同',
            'first': '第一',
            'last': '最后',
            'next': '下一个',
            'before': '之前',
            'after': '之后',
            'about': '关于',
            'into': '进入',
            'over': '超过',
            'under': '在下面',
            'out': '出去',
            'up': '向上',
            'down': '向下',
            'back': '回来',
            'come': '来',
            'go': '去',
            'make': '制作',
            'get': '得到',
            'give': '给',
            'take': '拿',
            'find': '找到',
            'know': '知道',
            'think': '想',
            'see': '看',
            'want': '想要',
            'need': '需要',
            'try': '尝试',
            'use': '使用',
            'call': '打电话',
            'ask': '问',
            'tell': '告诉',
            'say': '说',
            'speak': '说',
            'read': '读',
            'write': '写',
            'learn': '学习',
            'study': '学习',
            'teach': '教',
            'help': '帮助',
            'like': '喜欢',
            'start': '开始',
            'end': '结束',
            'stop': '停止',
            'open': '打开',
            'close': '关闭',
            'run': '跑',
            'walk': '走',
            'move': '移动',
            'change': '改变',
            'turn': '转',
            'play': '玩',
            'eat': '吃',
            'drink': '喝',
            'sleep': '睡觉',
            'live': '生活',
            'die': '死亡',
            'buy': '买',
            'sell': '卖',
            'send': '发送',
            'receive': '接收',
            'create': '创建',
            'build': '建造',
            'break': '打破',
            'keep': '保持',
            'hold': '持有',
            'let': '让',
            'begin': '开始',
            'seem': '似乎',
            'feel': '感觉',
            'leave': '离开',
            'put': '放',
            'set': '设置',
            'mean': '意思是',
            'show': '展示',
            'hear': '听到',
            'stand': '站',
            'lose': '失去',
            'pay': '支付',
            'meet': '见面',
            'include': '包括',
            'continue': '继续',
            'set': '设置',
            'learn': '学习',
            'change': '改变',
            'lead': '领导',
            'understand': '理解',
            'watch': '看',
            'follow': '跟随',
            'stop': '停止',
            'create': '创建',
            'speak': '说',
            'read': '读',
            'allow': '允许',
            'add': '加',
            'spend': '花',
            'grow': '成长',
            'open': '打开',
            'walk': '走',
            'win': '赢',
            'offer': '提供',
            'remember': '记住',
            'love': '爱',
            'consider': '考虑',
            'appear': '出现',
            'buy': '买',
            'wait': '等待',
            'serve': '服务',
            'die': '死',
            'send': '发送',
            'build': '建造',
            'stay': '停留',
            'fall': '落下',
            'cut': '切',
            'reach': '到达',
            'kill': '杀',
            'remain': '保持',
            'suggest': '建议',
            'raise': '提高',
            'pass': '通过',
            'sell': '卖',
            'require': '需要',
            'report': '报告',
            'decide': '决定',
            'pull': '拉',
            'develop': '发展',
        }

        zh_to_en = {v: k for k, v in en_to_zh.items() if v}

        # 根据语言方向选择翻译表
        if source_lang == 'en' and target_lang == 'zh':
            # 英译中
            words = text.split()
            result_parts = []
            translated_count = 0
            for word in words:
                clean_word = word.rstrip('.,!?;:()[]{}"\'')
                punctuation = word[len(clean_word):]
                lower_word = clean_word.lower()
                if lower_word in en_to_zh:
                    translated = en_to_zh[lower_word]
                    translated_count += 1
                else:
                    translated = clean_word
                result_parts.append(translated + punctuation)
            result = ''.join(result_parts)
            # 模拟模式下，总是添加标记让用户知道这是模拟翻译
            if not result.startswith('[模拟翻译]'):
                result = f'[模拟翻译] {result}'
            return result

        elif source_lang == 'zh' and target_lang == 'en':
            # 中译英 - 简单的字符级翻译
            result = text
            translated_count = 0
            # 按长度排序，长词优先匹配
            sorted_zh = sorted(zh_to_en.keys(), key=len, reverse=True)
            for zh in sorted_zh:
                if zh in result:
                    result = result.replace(zh, zh_to_en[zh] + ' ')
                    translated_count += 1
            result = result.strip()
            # 模拟模式下，总是添加标记让用户知道这是模拟翻译
            if not result.startswith('[模拟翻译]'):
                result = f'[模拟翻译] {result}'
            return result

        else:
            # 其他语言对，直接返回带标记的文本
            return f'[模拟翻译] {text}'

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
        # 模拟模式
        if self.simulation_mode:
            import time
            time.sleep(0.5)  # 模拟网络延迟
            return self._simulate_translate(text, source_lang or 'en', target_lang)

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


def is_simulation_mode():
    """是否为模拟模式"""
    t = init_translator()
    return t.simulation_mode


def translate_text(text, source_lang, target_lang, use_glossary=True):
    """
    翻译文本（支持术语表）

    Args:
        text: 待翻译文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
        use_glossary: 是否使用术语表（默认True）

    Returns:
        dict: 包含翻译结果和术语匹配信息
            - translation: 翻译后的文本
            - glossary_matches: 匹配的术语列表
            - simulation: 是否为模拟模式
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
        return {
            'translation': text,
            'glossary_matches': [],
            'simulation': t.simulation_mode
        }

    # 应用术语表预处理
    term_mapping = {}
    processed_text = text
    glossary_matches = []

    if use_glossary:
        processed_text, term_mapping = apply_glossary_to_translation(text, source_lang, target_lang)

    # 调用翻译API
    translated_text = t.translate(processed_text, volc_source, volc_target)

    # 还原术语
    if term_mapping:
        translated_text = restore_glossary_terms(translated_text, term_mapping)

    # 收集匹配的术语信息
    if term_mapping:
        from glossary_service import get_glossary_list
        all_terms = get_glossary_list(source_lang, target_lang)
        # 通过原文检查匹配
        import re
        for term in all_terms:
            flags = 0 if term.get('case_sensitive', False) else re.IGNORECASE
            if re.search(r'\b' + re.escape(term['source_term']) + r'\b', text, flags):
                glossary_matches.append({
                    'source_term': term['source_term'],
                    'target_term': term['target_term'],
                    'id': term['id']
                })

    return {
        'translation': translated_text,
        'glossary_matches': glossary_matches,
        'simulation': t.simulation_mode
    }