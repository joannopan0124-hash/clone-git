"""
翻译服务模块

支持多种翻译服务：
1. 腾讯云机器翻译API（优先） - 需配置TENCENT_SECRET_ID和TENCENT_SECRET_KEY
2. 火山引擎机器翻译API - 需配置VOLC_ACCESS_KEY和VOLC_SECRET_KEY
3. 免费在线翻译API（LibreTranslate/MyMemory）
4. 本地模拟翻译（回退）

支持术语表功能，作为翻译记忆库使用
"""

import os
import json
import re
import requests
import random
from datetime import datetime
import hashlib

# 繁简转换
try:
    from opencc import OpenCC
    _t2s_converter = OpenCC('t2s')
    def _to_simplified_chinese(text):
        """繁体转简体"""
        if not text:
            return text
        try:
            return _t2s_converter.convert(text)
        except Exception:
            return text
except ImportError:
    def _to_simplified_chinese(text):
        return text

import hmac
import urllib.parse
from glossary_service import apply_glossary_to_translation, restore_glossary_terms


# 免费在线翻译API（无需密钥）
LIBRETRANSLATE_URL = 'https://libretranslate.com/translate'
MYMEMORY_URL = 'https://api.mymemory.translated.net/get'

# 语言代码映射到 MyMemory 使用的格式
MYMEMORY_LANG_MAP = {
    'zh': 'zh-CN',
    'en': 'en',
    'ja': 'ja',
    'ko': 'ko',
    'fr': 'fr',
    'de': 'de',
    'es': 'es',
    'pt': 'pt',
    'ru': 'ru',
    'it': 'it',
}


def _call_libretranslate(text, source_lang, target_lang):
    """
    调用 LibreTranslate 免费在线翻译API
    格式: {q: text, source: 'en', target: 'zh', format: 'text'}
    
    Args:
        text: 待翻译文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
    
    Returns:
        str: 翻译结果，失败时返回 None
    """
    src = MYMEMORY_LANG_MAP.get(source_lang, source_lang)
    dst = MYMEMORY_LANG_MAP.get(target_lang, target_lang)

    data = {
        'q': text,
        'source': src,
        'target': dst,
        'format': 'text',
    }

    try:
        response = requests.post(LIBRETRANSLATE_URL, json=data, timeout=15)
        if response.status_code != 200:
            print(f'LibreTranslate 返回错误状态码: {response.status_code}')
            return None

        result = response.json()
        translated = result.get('translatedText')
        if translated:
            return translated
        return None
    except Exception as e:
        print(f'LibreTranslate 调用失败: {e}')
        return None


def _is_mostly_english(text):
    """
    检测文本是否主要为英文（用于判断翻译是否失败）
    如果文本中英文字母占比超过70%，则认为还是英文
    """
    if not text:
        return False
    # 去除空格和标点
    stripped = re.sub(r'[\s\W]', '', text)
    if not stripped:
        return False
    # 统计英文字母
    english_chars = sum(1 for c in stripped if c.isascii() and c.isalpha())
    return english_chars / len(stripped) > 0.7


def _call_mymemory(text, source_lang, target_lang):
    """
    调用 MyMemory 免费在线翻译API（备用）
    无需API密钥，每日有免费额度

    Args:
        text: 待翻译文本
        source_lang: 源语言代码
        target_lang: 目标语言代码

    Returns:
        str: 翻译结果，失败时返回 None
    """
    src = MYMEMORY_LANG_MAP.get(source_lang, source_lang)
    dst = MYMEMORY_LANG_MAP.get(target_lang, target_lang)

    params = {
        'q': text,
        'langpair': f'{src}|{dst}',
    }

    try:
        response = requests.get(MYMEMORY_URL, params=params, timeout=15)
        if response.status_code != 200:
            return None

        data = response.json()
        translated = data.get('responseData', {}).get('translatedText')
        if translated and data.get('responseStatus') == 200:
            # 繁体转简体
            translated = _to_simplified_chinese(translated)
            # 检测是否仍未翻译（返回了原文英文）
            if target_lang.startswith('zh') and _is_mostly_english(translated):
                print(f'MyMemory 返回未翻译的英文: {translated}')
                return None
            return translated
        return None
    except Exception as e:
        print(f'MyMemory 调用失败: {e}')
        return None


class TencentCloudTranslator:
    """腾讯云翻译客户端 - 使用官方SDK"""

    def __init__(self, secret_id=None, secret_key=None):
        """
        初始化腾讯云翻译客户端

        Args:
            secret_id: 腾讯云 SecretId
            secret_key: 腾讯云 SecretKey
        """
        self.secret_id = secret_id or os.environ.get('TENCENT_SECRET_ID', '')
        self.secret_key = secret_key or os.environ.get('TENCENT_SECRET_KEY', '')
        self.region = 'ap-guangzhou'
        self.simulation_mode = False

        if not self.secret_id or not self.secret_key:
            print('警告: 未配置腾讯云API密钥')
            self.simulation_mode = True

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
        if self.simulation_mode:
            raise Exception('腾讯云翻译未配置密钥')

        MAX_TEXT_LENGTH = 2000

        if len(text) <= MAX_TEXT_LENGTH:
            return self._translate_single(text, source_lang, target_lang)

        segments = self._split_text(text, MAX_TEXT_LENGTH)
        results = []
        for segment in segments:
            translated = self._translate_single(segment, source_lang, target_lang)
            results.append(translated)
        return ''.join(results)

    def _split_text(self, text, max_length):
        """
        按句子边界分割长文本，确保每段不超过max_length字符

        Args:
            text: 待分割文本
            max_length: 每段最大长度

        Returns:
            list: 分割后的文本片段列表
        """
        segments = []
        current_segment = ''

        sentences = re.split(r'(?<=[.!?。！？])\s*', text)

        for sentence in sentences:
            if not sentence.strip():
                continue

            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment)
                current_segment = sentence

        if current_segment:
            segments.append(current_segment)

        if not segments:
            segments = [text[:max_length]]

        return segments

    def _translate_single(self, text, source_lang=None, target_lang='zh'):
        """
        单次翻译（不超过2000字符）

        Args:
            text: 待翻译文本
            source_lang: 源语言代码
            target_lang: 目标语言代码

        Returns:
            str: 翻译后的文本

        Raises:
            Exception: 翻译失败时抛出异常
        """
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.tmt.v20180321 import tmt_client, models

        cred = credential.Credential(self.secret_id, self.secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.ap-guangzhou.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        client = tmt_client.TmtClient(cred, self.region, clientProfile)

        req = models.TextTranslateRequest()
        req.SourceText = text
        req.Target = target_lang
        req.Source = source_lang or 'auto'
        req.ProjectId = 0

        try:
            resp = client.TextTranslate(req)
            return resp.TargetText
        except TencentCloudSDKException as err:
            raise Exception(f'腾讯云翻译失败: {err.message}')


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
            print('警告: 未配置火山引擎API密钥')
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

    def _lookup_word(self, word, word_dict):
        """
        查询单词翻译，支持词形还原（复数、过去式、进行时等）
        """
        # 1. 直接查找
        if word in word_dict:
            return word_dict[word]

        # 2. 词形还原尝试
        candidates = []

        # 复数 -> 单数
        if word.endswith('ies') and len(word) > 4:
            candidates.append(word[:-3] + 'y')  # cities -> city
        if word.endswith('es') and len(word) > 3:
            candidates.append(word[:-2])  # boxes -> box
        if word.endswith('s') and len(word) > 2:
            candidates.append(word[:-1])  # students -> student

        # 过去式 -> 原形
        if word.endswith('ied') and len(word) > 4:
            candidates.append(word[:-3] + 'y')  # studied -> study
        if word.endswith('ed') and len(word) > 3:
            candidates.append(word[:-2])  # worked -> work
            candidates.append(word[:-1])  # liked -> like

        # 现在分词 -> 原形
        if word.endswith('ing') and len(word) > 4:
            candidates.append(word[:-3])  # going -> go
            candidates.append(word[:-3] + 'e')  # making -> make

        # 比较级/最高级
        if word.endswith('est') and len(word) > 4:
            candidates.append(word[:-3])  # biggest -> big
            candidates.append(word[:-2])  # largest -> large
        if word.endswith('er') and len(word) > 3:
            candidates.append(word[:-2])  # bigger -> big
            candidates.append(word[:-1])  # larger -> large

        # 尝试所有候选词形
        for candidate in candidates:
            if candidate in word_dict:
                return word_dict[candidate]

        # 3. 都找不到，返回原词
        return word

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

        # 常用短语翻译表（优先匹配）
        phrase_to_zh = {
            # 问候语
            'good morning': '早上好',
            'good afternoon': '下午好',
            'good evening': '晚上好',
            'good night': '晚安',
            'good day': '日安',
            'hello world': '你好世界',
            'how are you': '你好吗',
            'how are you doing': '你怎么样',
            'how do you do': '你好',
            'nice to meet you': '很高兴认识你',
            'nice to see you': '很高兴见到你',
            'see you later': '回头见',
            'see you soon': '很快再见',
            'see you tomorrow': '明天见',
            'take care': '保重',
            'have a good day': '祝你今天愉快',
            'have a nice day': '祝你今天愉快',
            'have a good time': '祝你玩得开心',
            'thank you very much': '非常感谢',
            'thanks a lot': '多谢',
            'many thanks': '多谢',
            'you are welcome': '不客气',
            'no problem': '没问题',
            'no worries': '不用担心',
            'dont worry': '别担心',
            'excuse me': '抱歉',
            'i am sorry': '对不起',
            'sorry about that': '抱歉',
            'please help me': '请帮我',
            'can you help me': '你能帮我吗',
            'could you help me': '你能帮我吗',
            'what is your name': '你叫什么名字',
            'my name is': '我的名字是',
            'i am from': '我来自',
            'where are you from': '你来自哪里',
            'what time is it': '现在几点了',
            'how much is this': '这个多少钱',
            'how much does it cost': '这个多少钱',
            'i love you': '我爱你',
            'i like you': '我喜欢你',
            'best wishes': '最美好的祝愿',
            'happy birthday': '生日快乐',
            'happy new year': '新年快乐',
            'merry christmas': '圣诞快乐',
            'congratulations': '恭喜',
            'well done': '做得好',
            'good job': '做得好',
            'good luck': '祝好运',
            'all the best': '一切顺利',
            # 常用句子
            'i dont know': '我不知道',
            'i know': '我知道',
            'i understand': '我理解',
            'i dont understand': '我不理解',
            'i think': '我认为',
            'i believe': '我相信',
            'i hope': '我希望',
            'i want': '我想',
            'i need': '我需要',
            'i like': '我喜欢',
            'i prefer': '我更喜欢',
            'it is': '这是',
            'this is': '这是',
            'that is': '那是',
            'there is': '有',
            'here is': '这里有',
            'let me': '让我',
            'let us': '让我们',
            'let us go': '让我们去',
            'let us start': '让我们开始',
            'please wait': '请等待',
            'please wait a moment': '请稍等',
            'just a moment': '稍等一下',
            'one moment please': '请稍等',
            'hold on': '等一下',
            'wait a minute': '等一下',
            'wait a moment': '等一下',
            'come here': '来这里',
            'go there': '去那里',
            'go home': '回家',
            'go to work': '去上班',
            'go to school': '去上学',
            'have breakfast': '吃早餐',
            'have lunch': '吃午餐',
            'have dinner': '吃晚餐',
            'have fun': '玩得开心',
            'take a look': '看一看',
            'take a rest': '休息一下',
            'have a seat': '请坐',
            'sit down': '坐下',
            'stand up': '站起来',
            'wake up': '醒来',
            'get up': '起床',
            'go to bed': '去睡觉',
            'go to sleep': '去睡觉',
            'turn on': '打开',
            'turn off': '关闭',
            'open the door': '开门',
            'close the door': '关门',
            'turn left': '左转',
            'turn right': '右转',
            'go straight': '直走',
            'go ahead': '继续前进',
            'come in': '进来',
            'come out': '出来',
            'get in': '进去',
            'get out': '出来',
            'pick up': '捡起',
            'put down': '放下',
            'look at': '看',
            'listen to': '听',
            'think about': '考虑',
            'talk about': '谈论',
            'speak about': '谈论',
            'write down': '写下',
            'read aloud': '朗读',
            'work hard': '努力工作',
            'study hard': '努力学习',
            'try again': '再试一次',
            'start again': '重新开始',
            'do it again': '再做一次',
            'come back': '回来',
            'go back': '回去',
            'get back': '回来',
            'move on': '继续前进',
            'carry on': '继续',
            'keep going': '继续前进',
            'never give up': '永不放弃',
            'dont give up': '不要放弃',
            'hold on tight': '紧紧抓住',
            'stay safe': '保持安全',
            'be careful': '小心',
            'watch out': '注意',
            'look out': '小心',
            'pay attention': '注意',
            'make sure': '确保',
            'make it': '做到',
            'do your best': '尽力而为',
            'give it a try': '试一试',
            'give me': '给我',
            'show me': '给我看',
            'tell me': '告诉我',
            'let me know': '让我知道',
            'keep in touch': '保持联系',
            'stay in touch': '保持联系',
            'get in touch': '联系',
            'call me': '打电话给我',
            'email me': '给我发邮件',
            'send me': '发送给我',
            'text me': '给我发短信',
            # 简单常用表达
            'yes of course': '当然',
            'of course': '当然',
            'sure thing': '当然',
            'absolutely': '绝对',
            'definitely': '肯定',
            'exactly': '确切',
            'thats right': '正确',
            'thats correct': '正确',
            'not bad': '不错',
            'very good': '很好',
            'very nice': '很好',
            'so good': '很好',
            'too bad': '太糟糕',
            'too late': '太晚了',
            'too early': '太早了',
            'too much': '太多',
            'too many': '太多',
            'not enough': '不够',
            'just right': '刚好',
            'more or less': '或多或少',
            'at least': '至少',
            'at most': '最多',
            'as soon as possible': '尽快',
            'right now': '现在',
            'just now': '刚才',
            'right here': '就在这里',
            'right there': '就在那里',
            'over there': '那边',
            'over here': '这边',
            'in here': '在这里',
            'out there': '在外面',
            'up there': '上面',
            'down there': '下面',
            # 技术相关短语
            'machine learning': '机器学习',
            'artificial intelligence': '人工智能',
            'deep learning': '深度学习',
            'natural language processing': '自然语言处理',
            'computer vision': '计算机视觉',
            'data science': '数据科学',
            'big data': '大数据',
            'cloud computing': '云计算',
            'internet of things': '物联网',
            'virtual reality': '虚拟现实',
            'augmented reality': '增强现实',
            'block chain': '区块链',
            'open source': '开源',
            'source code': '源代码',
            'user interface': '用户界面',
            'user experience': '用户体验',
            'web development': '网页开发',
            'mobile app': '移动应用',
            'software development': '软件开发',
            'product management': '产品管理',
            'project management': '项目管理',
            'version control': '版本控制',
            'continuous integration': '持续集成',
            'continuous delivery': '持续交付',
            'test automation': '自动化测试',
            'unit testing': '单元测试',
            'integration testing': '集成测试',
            'performance testing': '性能测试',
            'security testing': '安全测试',
            'code review': '代码审查',
            'technical support': '技术支持',
            'customer service': '客户服务',
            'quality assurance': '质量保证',
            'bug fix': '修复错误',
            'feature request': '功能请求',
            'product launch': '产品发布',
            'market research': '市场研究',
            'business model': '商业模式',
            'business plan': '商业计划',
            'financial report': '财务报告',
            'annual report': '年度报告',
            'quarterly report': '季度报告',
            'progress report': '进度报告',
            'status update': '状态更新',
            'meeting minutes': '会议记录',
            'action item': '行动项目',
            'next steps': '下一步',
            'follow up': '跟进',
            'deadline': '截止日期',
            'time line': '时间线',
            'road map': '路线图',
            'milestone': '里程碑',
            'key point': '关键点',
            'main goal': '主要目标',
            'top priority': '最高优先级',
            'high priority': '高优先级',
            'low priority': '低优先级',
        }

        # 常见词汇翻译表
        en_to_zh = {
            # 基础词汇
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
            'china': '中国',
            'english': '英语',
            'chinese': '中文',
            'japanese': '日语',
            'language': '语言',
            'computer': '电脑',
            'phone': '电话',
            'mobile': '手机',
            'internet': '互联网',
            'website': '网站',
            'app': '应用',
            'software': '软件',
            'hardware': '硬件',
            'code': '代码',
            'program': '程序',
            'data': '数据',
            'file': '文件',
            'video': '视频',
            'audio': '音频',
            'music': '音乐',
            'movie': '电影',
            'game': '游戏',
            'sport': '运动',
            'food': '食物',
            'water': '水',
            'tea': '茶',
            'coffee': '咖啡',
            'fruit': '水果',
            'vegetable': '蔬菜',
            'meat': '肉',
            'rice': '米饭',
            'bread': '面包',
            'money': '钱',
            'price': '价格',
            'shop': '商店',
            'store': '商店',
            'market': '市场',
            'company': '公司',
            'business': '商业',
            'job': '工作',
            'office': '办公室',
            'school': '学校',
            'student': '学生',
            'teacher': '老师',
            'class': '班级',
            'lesson': '课程',
            'exam': '考试',
            'test': '测试',
            'question': '问题',
            'answer': '答案',
            'problem': '问题',
            'solution': '解决方案',
            'idea': '想法',
            'plan': '计划',
            'goal': '目标',
            'dream': '梦想',
            'hope': '希望',
            'success': '成功',
            'failure': '失败',
            'error': '错误',
            'message': '消息',
            'email': '邮件',
            'letter': '信',
            'paper': '纸',
            'pen': '笔',
            'desk': '桌子',
            'chair': '椅子',
            'room': '房间',
            'house': '房子',
            'home': '家',
            'family': '家庭',
            'friend': '朋友',
            'neighbor': '邻居',
            'city': '城市',
            'country': '国家',
            'place': '地方',
            'road': '道路',
            'street': '街道',
            'car': '汽车',
            'bus': '公交车',
            'train': '火车',
            'plane': '飞机',
            'airport': '机场',
            'station': '车站',
            'hotel': '酒店',
            'restaurant': '餐厅',
            'hospital': '医院',
            'bank': '银行',
            'park': '公园',
            'garden': '花园',
            'tree': '树',
            'flower': '花',
            'animal': '动物',
            'dog': '狗',
            'cat': '猫',
            'bird': '鸟',
            'fish': '鱼',
            'sun': '太阳',
            'moon': '月亮',
            'star': '星星',
            'sky': '天空',
            'cloud': '云',
            'rain': '雨',
            'snow': '雪',
            'wind': '风',
            'weather': '天气',
            'spring': '春天',
            'summer': '夏天',
            'autumn': '秋天',
            'winter': '冬天',
            'morning': '早上',
            'afternoon': '下午',
            'evening': '晚上',
            'night': '夜晚',
            'today': '今天',
            'tomorrow': '明天',
            'yesterday': '昨天',
            'week': '周',
            'month': '月',
            'year': '年',
            'time': '时间',
            'hour': '小时',
            'minute': '分钟',
            'second': '秒',
            'date': '日期',
            'birthday': '生日',
            'holiday': '假期',
            'festival': '节日',
            'party': '派对',
            'meeting': '会议',
            'event': '事件',
            'news': '新闻',
            'story': '故事',
            'book': '书',
            'page': '页',
            'chapter': '章节',
            'content': '内容',
            'title': '标题',
            'name': '名字',
            'age': '年龄',
            'number': '数字',
            'color': '颜色',
            'size': '大小',
            'shape': '形状',
            'style': '风格',
            'type': '类型',
            'kind': '种类',
            'part': '部分',
            'side': '侧面',
            'center': '中心',
            'top': '顶部',
            'bottom': '底部',
            'left': '左边',
            'right': '右边',
            'front': '前面',
            'back': '后面',
            'inside': '里面',
            'outside': '外面',
            'north': '北',
            'south': '南',
            'east': '东',
            'west': '西',
            # 常用动词
            'go': '去',
            'come': '来',
            'walk': '走',
            'run': '跑',
            'sit': '坐',
            'stand': '站',
            'sleep': '睡觉',
            'wake': '醒来',
            'eat': '吃',
            'drink': '喝',
            'cook': '做饭',
            'buy': '买',
            'sell': '卖',
            'give': '给',
            'take': '拿',
            'bring': '带来',
            'send': '发送',
            'receive': '接收',
            'find': '找到',
            'lose': '丢失',
            'keep': '保持',
            'make': '制作',
            'build': '建造',
            'create': '创建',
            'change': '改变',
            'move': '移动',
            'stop': '停止',
            'start': '开始',
            'finish': '完成',
            'end': '结束',
            'continue': '继续',
            'wait': '等待',
            'help': '帮助',
            'try': '尝试',
            'use': '使用',
            'learn': '学习',
            'teach': '教',
            'study': '学习',
            'read': '读',
            'write': '写',
            'listen': '听',
            'hear': '听到',
            'speak': '说',
            'say': '说',
            'tell': '告诉',
            'ask': '问',
            'answer': '回答',
            'call': '打电话',
            'visit': '访问',
            'meet': '见面',
            'join': '加入',
            'leave': '离开',
            'return': '返回',
            'arrive': '到达',
            'travel': '旅行',
            'drive': '驾驶',
            'fly': '飞',
            'swim': '游泳',
            'play': '玩',
            'watch': '看',
            'look': '看',
            'see': '看到',
            'show': '展示',
            'draw': '画',
            'paint': '绘画',
            'sing': '唱歌',
            'dance': '跳舞',
            'work': '工作',
            'rest': '休息',
            'think': '思考',
            'know': '知道',
            'understand': '理解',
            'remember': '记住',
            'forget': '忘记',
            'believe': '相信',
            'feel': '感觉',
            'love': '爱',
            'like': '喜欢',
            'hate': '讨厌',
            'want': '想要',
            'need': '需要',
            'wish': '希望',
            'hope': '希望',
            'expect': '期待',
            'agree': '同意',
            'disagree': '不同意',
            'accept': '接受',
            'refuse': '拒绝',
            'allow': '允许',
            'decide': '决定',
            'choose': '选择',
            'prefer': '更喜欢',
            'enjoy': '享受',
            'share': '分享',
            'save': '保存',
            'spend': '花费',
            'pay': '支付',
            'cost': '花费',
            'earn': '赚取',
            'win': '赢',
            'lose': '输',
            'fail': '失败',
            'succeed': '成功',
            'improve': '改进',
            'develop': '发展',
            'grow': '成长',
            'increase': '增加',
            'decrease': '减少',
            'add': '添加',
            'remove': '移除',
            'delete': '删除',
            'update': '更新',
            'check': '检查',
            'fix': '修复',
            'solve': '解决',
            'explain': '解释',
            'describe': '描述',
            'discuss': '讨论',
            'compare': '比较',
            'recommend': '推荐',
            'suggest': '建议',
            'report': '报告',
            'announce': '宣布',
            'introduce': '介绍',
            'present': '呈现',
            'review': '审查',
            'analyze': '分析',
            'design': '设计',
            'plan': '计划',
            'organize': '组织',
            'manage': '管理',
            'lead': '领导',
            'follow': '跟随',
            'support': '支持',
            'serve': '服务',
            'produce': '生产',
            'provide': '提供',
            'offer': '提供',
            'supply': '供应',
            'deliver': '交付',
            'export': '导出',
            'import': '导入',
            # 代词和冠词
            'the': '',
            'a': '',
            'an': '',
            'i': '我',
            'me': '我',
            'my': '我的',
            'we': '我们',
            'us': '我们',
            'our': '我们的',
            'you': '你',
            'your': '你的',
            'he': '他',
            'him': '他',
            'his': '他的',
            'she': '她',
            'her': '她的',
            'it': '它',
            'its': '它的',
            'they': '他们',
            'them': '他们',
            'their': '他们的',
            'this': '这',
            'that': '那',
            'these': '这些',
            'those': '那些',
            'what': '什么',
            'who': '谁',
            'which': '哪个',
            'where': '哪里',
            'when': '何时',
            'why': '为什么',
            'how': '如何',
            # 介词和连词
            'in': '在',
            'on': '在',
            'at': '在',
            'to': '到',
            'from': '从',
            'of': '的',
            'for': '为',
            'with': '与',
            'by': '由',
            'about': '关于',
            'between': '之间',
            'among': '之中',
            'through': '通过',
            'over': '在上方',
            'under': '在下方',
            'above': '上方',
            'below': '下方',
            'up': '向上',
            'down': '向下',
            'into': '进入',
            'out': '出去',
            'off': '离开',
            'around': '周围',
            'before': '之前',
            'after': '之后',
            'since': '自从',
            'until': '直到',
            'while': '当',
            'during': '期间',
            'and': '和',
            'or': '或',
            'but': '但是',
            'so': '所以',
            'because': '因为',
            'if': '如果',
            'then': '然后',
            'else': '否则',
            'also': '也',
            'too': '也',
            'as': '作为',
            'like': '像',
            'than': '比',
            # 助动词和情态动词
            'is': '是',
            'are': '是',
            'am': '是',
            'was': '是',
            'were': '是',
            'be': '是',
            'been': '是',
            'being': '是',
            'have': '有',
            'has': '有',
            'had': '有',
            'having': '有',
            'do': '做',
            'does': '做',
            'did': '做',
            'doing': '做',
            'can': '能',
            'could': '能',
            'will': '将',
            'would': '将',
            'shall': '将',
            'should': '应该',
            'may': '可能',
            'might': '可能',
            'must': '必须',
            # 常用形容词
            'good': '好',
            'bad': '坏',
            'great': '伟大',
            'nice': '好',
            'fine': '好',
            'beautiful': '美丽',
            'ugly': '丑陋',
            'pretty': '漂亮',
            'cute': '可爱',
            'cool': '酷',
            'hot': '热',
            'cold': '冷',
            'warm': '温暖',
            'cool': '凉爽',
            'dry': '干燥',
            'wet': '湿润',
            'clean': '干净',
            'dirty': '脏',
            'fast': '快',
            'slow': '慢',
            'quick': '快速',
            'easy': '简单',
            'difficult': '困难',
            'hard': '困难',
            'simple': '简单',
            'complex': '复杂',
            'clear': '清楚',
            'confusing': '困惑',
            'true': '真实',
            'false': '错误',
            'real': '真实',
            'fake': '虚假',
            'right': '正确',
            'wrong': '错误',
            'correct': '正确',
            'incorrect': '不正确',
            'important': '重要',
            'necessary': '必要',
            'possible': '可能',
            'impossible': '不可能',
            'available': '可用',
            'free': '免费',
            'cheap': '便宜',
            'expensive': '昂贵',
            'rich': '富有',
            'poor': '贫穷',
            'happy': '快乐',
            'sad': '悲伤',
            'angry': '愤怒',
            'excited': '兴奋',
            'tired': '疲惫',
            'busy': '忙碌',
            'lazy': '懒惰',
            'smart': '聪明',
            'stupid': '愚蠢',
            'clever': '聪明',
            'foolish': '愚蠢',
            'strong': '强壮',
            'weak': '虚弱',
            'healthy': '健康',
            'sick': '生病',
            'young': '年轻',
            'old': '老',
            'new': '新',
            'modern': '现代',
            'traditional': '传统',
            'popular': '流行',
            'famous': '著名',
            'special': '特殊',
            'common': '常见',
            'rare': '罕见',
            'unique': '独特',
            'different': '不同',
            'same': '相同',
            'similar': '相似',
            'big': '大',
            'small': '小',
            'large': '大',
            'little': '小',
            'huge': '巨大',
            'tiny': '微小',
            'long': '长',
            'short': '短',
            'high': '高',
            'low': '低',
            'tall': '高',
            'wide': '宽',
            'narrow': '窄',
            'thick': '厚',
            'thin': '薄',
            'heavy': '重',
            'light': '轻',
            'deep': '深',
            'shallow': '浅',
            'bright': '明亮',
            'dark': '黑暗',
            'white': '白',
            'black': '黑',
            'red': '红',
            'blue': '蓝',
            'green': '绿',
            'yellow': '黄',
            'orange': '橙',
            'purple': '紫',
            'pink': '粉',
            'brown': '棕',
            'gray': '灰',
            'golden': '金色',
            'silver': '银色',
            # 常用副词
            'very': '非常',
            'really': '真的',
            'quite': '相当',
            'just': '只是',
            'only': '仅仅',
            'always': '总是',
            'usually': '通常',
            'often': '经常',
            'sometimes': '有时',
            'never': '从不',
            'ever': '曾经',
            'once': '一次',
            'twice': '两次',
            'again': '再次',
            'still': '仍然',
            'already': '已经',
            'yet': '还',
            'soon': '很快',
            'early': '早',
            'late': '晚',
            'quickly': '快速',
            'slowly': '缓慢',
            'carefully': '仔细',
            'easily': '容易',
            'hardly': '几乎不',
            'probably': '可能',
            'certainly': '肯定',
            'definitely': '绝对',
            'maybe': '也许',
            'perhaps': '或许',
            'luckily': '幸运',
            'unfortunately': '不幸',
            'actually': '实际上',
            'basically': '基本',
            'especially': '特别',
            'exactly': '确切',
            'finally': '最终',
            'firstly': '首先',
            'lastly': '最后',
            'mainly': '主要',
            'mostly': '主要',
            'nearly': '几乎',
            'particularly': '特别',
            'personally': '个人',
            'simply': '简单',
            'suddenly': '突然',
            'totally': '完全',
            'truly': '真正',
            'usually': '通常',
            # 数词
            'one': '一',
            'two': '二',
            'three': '三',
            'four': '四',
            'five': '五',
            'six': '六',
            'seven': '七',
            'eight': '八',
            'nine': '九',
            'ten': '十',
            'eleven': '十一',
            'twelve': '十二',
            'twenty': '二十',
            'thirty': '三十',
            'forty': '四十',
            'fifty': '五十',
            'hundred': '百',
            'thousand': '千',
            'million': '百万',
            'first': '第一',
            'second': '第二',
            'third': '第三',
            'last': '最后',
            'next': '下一个',
            'other': '其他',
            'another': '另一个',
            'all': '所有',
            'some': '一些',
            'any': '任何',
            'many': '许多',
            'much': '很多',
            'more': '更多',
            'most': '最多',
            'less': '更少',
            'least': '最少',
            'few': '很少',
            'several': '几个',
            'every': '每个',
            'each': '每个',
            'both': '两个',
            'either': '任一',
            'neither': '都不',
            'none': '没有',
            # 其他常用词
            'yes': '是',
            'no': '不',
            'not': '不',
            'please': '请',
            'thank': '谢谢',
            'thanks': '谢谢',
            'sorry': '抱歉',
            'excuse': '借口',
            'ok': '好的',
            'okay': '好的',
            'well': '好',
            'maybe': '也许',
            'perhaps': '可能',
            'anything': '任何事',
            'something': '某事',
            'nothing': '没有',
            'everything': '一切',
            'anyone': '任何人',
            'someone': '某人',
            'nobody': '没有人',
            'everybody': '每个人',
            'everyone': '每个人',
            'anywhere': '任何地方',
            'somewhere': '某处',
            'nowhere': '没有地方',
            'everywhere': '到处',
            'anytime': '任何时候',
            'sometimes': '有时',
            'always': '总是',
            'never': '从不',
            'really': '真的',
            'sure': '确定',
            'certain': '确定',
            'absolutely': '绝对',
            'exactly': '确切',
            'actually': '实际上',
            'basically': '基本上',
            'probably': '可能',
            'likely': '可能',
            'possibly': '可能',
            'definitely': '肯定',
            'certainly': '肯定',
            'indeed': '确实',
            'fact': '事实',
            'point': '点',
            'example': '例子',
            'reason': '原因',
            'result': '结果',
            'effect': '效果',
            'cause': '原因',
            'case': '情况',
            'situation': '情况',
            'condition': '条件',
            'environment': '环境',
            'nature': '自然',
            'culture': '文化',
            'history': '历史',
            'science': '科学',
            'art': '艺术',
            'math': '数学',
            'physics': '物理',
            'chemistry': '化学',
            'biology': '生物',
            'geography': '地理',
            'politics': '政治',
            'economy': '经济',
            'society': '社会',
            'law': '法律',
            'rule': '规则',
            'policy': '政策',
            'method': '方法',
            'way': '方式',
            'process': '过程',
            'step': '步骤',
            'action': '行动',
            'activity': '活动',
            'task': '任务',
            'project': '项目',
            'mission': '使命',
            'purpose': '目的',
            'meaning': '意义',
            'value': '价值',
            'quality': '质量',
            'quantity': '数量',
            'amount': '数量',
            'level': '水平',
            'degree': '程度',
            'range': '范围',
            'limit': '限制',
            'maximum': '最大',
            'minimum': '最小',
            'average': '平均',
            'total': '总计',
            'sum': '总和',
            'difference': '差异',
            'similarity': '相似',
            'connection': '连接',
            'relation': '关系',
            'relationship': '关系',
            'association': '关联',
            'organization': '组织',
            'institution': '机构',
            'department': '部门',
            'division': '部门',
            'section': '部分',
            'unit': '单位',
            'element': '元素',
            'component': '组件',
            'feature': '特征',
            'characteristic': '特点',
            'property': '属性',
            'attribute': '属性',
            'advantage': '优势',
            'disadvantage': '劣势',
            'benefit': '利益',
            'profit': '利润',
            'loss': '损失',
            'risk': '风险',
            'danger': '危险',
            'safety': '安全',
            'security': '安全',
            'protection': '保护',
            'defense': '防御',
            'attack': '攻击',
            'fight': '战斗',
            'battle': '战斗',
            'war': '战争',
            'peace': '和平',
            'victory': '胜利',
            'defeat': '失败',
            'hero': '英雄',
            'leader': '领导',
            'follower': '追随者',
            'member': '成员',
            'partner': '伙伴',
            'colleague': '同事',
            'assistant': '助手',
            'expert': '专家',
            'professional': '专业',
            'amateur': '业余',
            'beginner': '初学者',
            'master': '大师',
            'student': '学生',
            'learner': '学习者',
            'user': '用户',
            'customer': '客户',
            'client': '客户',
            'buyer': '买家',
            'seller': '卖家',
            'producer': '生产者',
            'consumer': '消费者',
            'manufacturer': '制造商',
            'supplier': '供应商',
            'distributor': '分销商',
            'retailer': '零售商',
            'wholesaler': '批发商',
            'trader': '贸易商',
            'investor': '投资者',
            'shareholder': '股东',
            'owner': '所有者',
            'manager': '经理',
            'director': '董事',
            'president': '总统',
            'chairman': '主席',
            'ceo': '首席执行官',
            'employee': '员工',
            'worker': '工人',
            'staff': '员工',
            'team': '团队',
            'group': '小组',
            'community': '社区',
            'public': '公共',
            'private': '私人',
            'personal': '个人',
            'official': '官方',
            'formal': '正式',
            'informal': '非正式',
            'local': '本地',
            'global': '全球',
            'international': '国际',
            'national': '国家',
            'regional': '区域',
            'central': '中央',
            'main': '主要',
            'primary': '主要',
            'secondary': '次要',
            'major': '主要',
            'minor': '次要',
            'key': '关键',
            'core': '核心',
            'basic': '基本',
            'advanced': '高级',
            'intermediate': '中级',
            'elementary': '初级',
            'general': '一般',
            'specific': '具体',
            'detailed': '详细',
            'brief': '简短',
            'short': '短',
            'long': '长',
            'full': '完整',
            'empty': '空',
            'complete': '完整',
            'incomplete': '不完整',
            'perfect': '完美',
            'imperfect': '不完美',
            'excellent': '优秀',
            'good': '好',
            'poor': '差',
            'average': '平均',
            'standard': '标准',
            'normal': '正常',
            'abnormal': '异常',
            'typical': '典型',
            'unusual': '不寻常',
            'ordinary': '普通',
            'extraordinary': '非凡',
            'amazing': '惊人',
            'wonderful': '精彩',
            'awesome': '极好',
            'fantastic': '极好',
            'terrible': '可怕',
            'horrible': '可怕',
            'awful': '糟糕',
            'disaster': '灾难',
            'crisis': '危机',
            'emergency': '紧急',
            'urgent': '紧急',
            'immediate': '立即',
            'instant': '瞬间',
            'sudden': '突然',
            'gradual': '逐渐',
            'steady': '稳定',
            'stable': '稳定',
            'unstable': '不稳定',
            'balanced': '平衡',
            'unbalanced': '不平衡',
            'fair': '公平',
            'unfair': '不公平',
            'equal': '相等',
            'unequal': '不等',
            'compatible': '兼容',
            'incompatible': '不兼容',
            'related': '相关',
            'unrelated': '无关',
            'connected': '连接',
            'disconnected': '断开',
            'linked': '链接',
            'separated': '分离',
            'combined': '结合',
            'mixed': '混合',
            'pure': '纯',
            'fresh': '新鲜',
            'stale': '陈旧',
            'original': '原始',
            'copy': '副本',
            'version': '版本',
            'edition': '版本',
            'release': '发布',
            'update': '更新',
            'upgrade': '升级',
            'downgrade': '降级',
            'install': '安装',
            'uninstall': '卸载',
            'download': '下载',
            'upload': '上传',
            'transfer': '传输',
            'convert': '转换',
            'transform': '变换',
            'translate': '翻译',
            'interpret': '解释',
            'understand': '理解',
            ' misunderstand': '误解',
            # ===== 扩展词汇库（科技/计算机） =====
            'computer': '计算机', 'laptop': '笔记本电脑', 'desktop': '台式机',
            'server': '服务器', 'client': '客户端', 'browser': '浏览器',
            'database': '数据库', 'table': '表格', 'record': '记录',
            'field': '字段', 'query': '查询', 'index': '索引',
            'algorithm': '算法', 'function': '函数', 'variable': '变量',
            'parameter': '参数', 'argument': '参数', 'return': '返回',
            'array': '数组', 'list': '列表', 'dictionary': '字典',
            'string': '字符串', 'number': '数字', 'boolean': '布尔值',
            'integer': '整数', 'float': '浮点数', 'character': '字符',
            'loop': '循环', 'condition': '条件', 'statement': '语句',
            'class': '类', 'object': '对象', 'method': '方法',
            'property': '属性', 'event': '事件', 'handler': '处理程序',
            'module': '模块', 'package': '包', 'library': '库',
            'framework': '框架', 'platform': '平台', 'environment': '环境',
            'config': '配置', 'configuration': '配置', 'setting': '设置',
            'option': '选项', 'preference': '偏好', 'default': '默认',
            'version': '版本', 'release': '发布', 'update': '更新',
            'upgrade': '升级', 'patch': '补丁', 'bug': '缺陷',
            'error': '错误', 'warning': '警告', 'exception': '异常',
            'debug': '调试', 'log': '日志', 'trace': '追踪',
            'compile': '编译', 'run': '运行', 'execute': '执行',
            'build': '构建', 'deploy': '部署', 'install': '安装',
            'uninstall': '卸载', 'setup': '设置', 'wizard': '向导',
            'interface': '界面', 'window': '窗口', 'dialog': '对话框',
            'menu': '菜单', 'toolbar': '工具栏', 'sidebar': '侧边栏',
            'button': '按钮', 'checkbox': '复选框', 'radio': '单选',
            'input': '输入', 'output': '输出', 'label': '标签',
            'icon': '图标', 'cursor': '光标', 'pointer': '指针',
            'screen': '屏幕', 'display': '显示', 'resolution': '分辨率',
            'pixel': '像素', 'color': '颜色', 'font': '字体',
            'size': '大小', 'width': '宽度', 'height': '高度',
            'length': '长度', 'depth': '深度', 'margin': '边距',
            'padding': '内边距', 'border': '边框', 'radius': '半径',
            'network': '网络', 'connection': '连接', 'disconnect': '断开',
            'online': '在线', 'offline': '离线', 'signal': '信号',
            'bandwidth': '带宽', 'latency': '延迟', 'timeout': '超时',
            'protocol': '协议', 'http': 'HTTP', 'https': 'HTTPS',
            'request': '请求', 'response': '响应', 'header': '头部',
            'body': '主体', 'status': '状态', 'code': '代码',
            'url': '网址', 'link': '链接', 'hyperlink': '超链接',
            'website': '网站', 'webpage': '网页', 'homepage': '主页',
            'domain': '域名', 'host': '主机', 'port': '端口',
            'ip': 'IP', 'address': '地址', 'route': '路由',
            'packet': '数据包', 'firewall': '防火墙', 'proxy': '代理',
            'cache': '缓存', 'cookie': 'Cookie', 'session': '会话',
            'token': '令牌', 'key': '密钥', 'encrypt': '加密',
            'decrypt': '解密', 'password': '密码', 'login': '登录',
            'logout': '登出', 'register': '注册', 'account': '账户',
            'user': '用户', 'admin': '管理员', 'permission': '权限',
            'role': '角色', 'group': '组', 'member': '成员',
            'profile': '档案', 'avatar': '头像', 'nickname': '昵称',
            # ===== 自然科学 =====
            'physics': '物理', 'chemistry': '化学', 'biology': '生物',
            'mathematics': '数学', 'geometry': '几何', 'algebra': '代数',
            'calculus': '微积分', 'statistics': '统计学', 'probability': '概率',
            'theory': '理论', 'hypothesis': '假设', 'experiment': '实验',
            'observation': '观察', 'analysis': '分析', 'conclusion': '结论',
            'evidence': '证据', 'data': '数据', 'fact': '事实',
            'element': '元素', 'molecule': '分子', 'atom': '原子',
            'electron': '电子', 'proton': '质子', 'neutron': '中子',
            'energy': '能量', 'force': '力', 'power': '力量',
            'velocity': '速度', 'acceleration': '加速度', 'mass': '质量',
            'weight': '重量', 'volume': '体积', 'density': '密度',
            'temperature': '温度', 'pressure': '压力', 'heat': '热',
            'light': '光', 'sound': '声音', 'wave': '波',
            'frequency': '频率', 'wavelength': '波长', 'spectrum': '光谱',
            'cell': '细胞', 'tissue': '组织', 'organ': '器官',
            'gene': '基因', 'dna': 'DNA', 'protein': '蛋白质',
            'enzyme': '酶', 'hormone': '激素', 'metabolism': '新陈代谢',
            'evolution': '进化', 'species': '物种', 'habitat': '栖息地',
            'ecosystem': '生态系统', 'environment': '环境', 'climate': '气候',
            # ===== 医学/健康 =====
            'medicine': '医学', 'medical': '医疗的', 'doctor': '医生',
            'nurse': '护士', 'patient': '病人', 'hospital': '医院',
            'clinic': '诊所', 'pharmacy': '药房', 'drug': '药物',
            'pill': '药丸', 'tablet': '药片', 'capsule': '胶囊',
            'injection': '注射', 'vaccine': '疫苗', 'virus': '病毒',
            'bacteria': '细菌', 'infection': '感染', 'disease': '疾病',
            'symptom': '症状', 'fever': '发烧', 'cough': '咳嗽',
            'headache': '头痛', 'stomach': '胃', 'heart': '心脏',
            'lung': '肺', 'liver': '肝脏', 'kidney': '肾脏',
            'blood': '血液', 'brain': '大脑', 'nerve': '神经',
            'muscle': '肌肉', 'bone': '骨头', 'skin': '皮肤',
            'eye': '眼睛', 'ear': '耳朵', 'nose': '鼻子',
            'mouth': '嘴巴', 'tooth': '牙齿', 'tongue': '舌头',
            'hand': '手', 'foot': '脚', 'arm': '手臂',
            'leg': '腿', 'head': '头', 'neck': '脖子',
            'shoulder': '肩膀', 'chest': '胸部', 'back': '背部',
            'health': '健康', 'healthy': '健康的', 'sick': '生病的',
            'illness': '疾病', 'treatment': '治疗', 'cure': '治愈',
            'recovery': '康复', 'surgery': '手术', 'operation': '手术',
            'examination': '检查', 'diagnosis': '诊断', 'prescription': '处方',
            # ===== 商业/经济 =====
            'business': '商业', 'company': '公司', 'corporation': '公司',
            'enterprise': '企业', 'industry': '行业', 'factory': '工厂',
            'product': '产品', 'service': '服务', 'customer': '客户',
            'client': '客户', 'market': '市场', 'marketing': '营销',
            'sale': '销售', 'sell': '卖', 'buy': '买',
            'purchase': '购买', 'price': '价格', 'cost': '成本',
            'profit': '利润', 'loss': '亏损', 'revenue': '收入',
            'income': '收入', 'expense': '支出', 'budget': '预算',
            'finance': '财务', 'financial': '财务的', 'bank': '银行',
            'money': '钱', 'cash': '现金', 'credit': '信用',
            'card': '卡片', 'check': '支票', 'invoice': '发票',
            'receipt': '收据', 'bill': '账单', 'fee': '费用',
            'tax': '税', 'interest': '利息', 'loan': '贷款',
            'investment': '投资', 'investor': '投资者', 'stock': '股票',
            'share': '股份', 'market': '市场', 'trade': '贸易',
            'import': '进口', 'export': '出口', 'deal': '交易',
            'contract': '合同', 'agreement': '协议', 'negotiate': '谈判',
            'manager': '经理', 'director': '董事', 'officer': '官员',
            'employee': '员工', 'staff': '职员', 'worker': '工人',
            'job': '工作', 'career': '职业', 'profession': '专业',
            'interview': '面试', 'salary': '薪水', 'wage': '工资',
            'meeting': '会议', 'conference': '会议', 'presentation': '演示',
            'report': '报告', 'document': '文档', 'file': '文件',
            'folder': '文件夹', 'directory': '目录', 'path': '路径',
            # ===== 教育 =====
            'education': '教育', 'school': '学校', 'college': '学院',
            'university': '大学', 'institute': '研究所', 'academy': '学院',
            'teacher': '老师', 'professor': '教授', 'student': '学生',
            'pupil': '小学生', 'classmate': '同学', 'lesson': '课程',
            'course': '课程', 'subject': '科目', 'major': '专业',
            'degree': '学位', 'diploma': '文凭', 'certificate': '证书',
            'grade': '成绩', 'score': '分数', 'mark': '分数',
            'exam': '考试', 'test': '测试', 'quiz': '小测验',
            'homework': '作业', 'assignment': '作业', 'project': '项目',
            'research': '研究', 'thesis': '论文', 'paper': '论文',
            'article': '文章', 'chapter': '章节', 'page': '页',
            'book': '书', 'textbook': '教科书', 'notebook': '笔记本',
            'library': '图书馆', 'laboratory': '实验室', 'classroom': '教室',
            'blackboard': '黑板', 'desk': '课桌', 'chair': '椅子',
            'knowledge': '知识', 'wisdom': '智慧', 'intelligence': '智力',
            'memory': '记忆', 'thinking': '思考', 'learning': '学习',
            'study': '学习', 'practice': '练习', 'training': '训练',
            'skill': '技能', 'ability': '能力', 'talent': '天赋',
            'experience': '经验', 'knowledge': '知识', 'understanding': '理解',
            # ===== 日常生活 =====
            'home': '家', 'house': '房子', 'apartment': '公寓',
            'room': '房间', 'kitchen': '厨房', 'bedroom': '卧室',
            'bathroom': '浴室', 'living': '客厅', 'dining': '餐厅',
            'garden': '花园', 'garage': '车库', 'balcony': '阳台',
            'door': '门', 'window': '窗户', 'wall': '墙',
            'floor': '地板', 'ceiling': '天花板', 'roof': '屋顶',
            'stairs': '楼梯', 'elevator': '电梯', 'escalator': '自动扶梯',
            'furniture': '家具', 'sofa': '沙发', 'bed': '床',
            'table': '桌子', 'shelf': '架子', 'cabinet': '柜子',
            'lamp': '灯', 'light': '灯', 'clock': '时钟',
            'mirror': '镜子', 'picture': '图片', 'painting': '画作',
            'curtain': '窗帘', 'carpet': '地毯', 'rug': '小地毯',
            'food': '食物', 'meal': '一餐', 'breakfast': '早餐',
            'lunch': '午餐', 'dinner': '晚餐', 'supper': '晚餐',
            'snack': '零食', 'dessert': '甜点', 'drink': '饮料',
            'water': '水', 'juice': '果汁', 'coffee': '咖啡',
            'tea': '茶', 'milk': '牛奶', 'wine': '葡萄酒',
            'beer': '啤酒', 'alcohol': '酒精', 'ice': '冰',
            'rice': '米饭', 'noodle': '面条', 'bread': '面包',
            'meat': '肉', 'beef': '牛肉', 'pork': '猪肉',
            'chicken': '鸡肉', 'fish': '鱼', 'seafood': '海鲜',
            'egg': '鸡蛋', 'vegetable': '蔬菜', 'fruit': '水果',
            'apple': '苹果', 'banana': '香蕉', 'orange': '橙子',
            'grape': '葡萄', 'lemon': '柠檬', 'peach': '桃子',
            'pear': '梨', 'strawberry': '草莓', 'watermelon': '西瓜',
            'tomato': '番茄', 'potato': '土豆', 'onion': '洋葱',
            'garlic': '大蒜', 'ginger': '姜', 'pepper': '胡椒',
            'salt': '盐', 'sugar': '糖', 'oil': '油',
            'sauce': '酱汁', 'vinegar': '醋', 'flour': '面粉',
            'cake': '蛋糕', 'cookie': '饼干', 'pie': '馅饼',
            'pizza': '披萨', 'hamburger': '汉堡', 'sandwich': '三明治',
            'chocolate': '巧克力', 'candy': '糖果', 'cheese': '奶酪',
            'butter': '黄油', 'yogurt': '酸奶', 'cream': '奶油',
            # ===== 交通/旅行 =====
            'travel': '旅行', 'trip': '旅行', 'journey': '旅程',
            'tour': '旅游', 'tourist': '游客', 'visitor': '访客',
            'ticket': '票', 'passport': '护照', 'visa': '签证',
            'luggage': '行李', 'bag': '包', 'suitcase': '手提箱',
            'map': '地图', 'guide': '指南', 'direction': '方向',
            'hotel': '酒店', 'motel': '汽车旅馆', 'hostel': '旅舍',
            'restaurant': '餐厅', 'cafe': '咖啡馆', 'bar': '酒吧',
            'airport': '机场', 'station': '车站', 'port': '港口',
            'harbor': '港口', 'terminal': '航站楼', 'platform': '站台',
            'car': '汽车', 'vehicle': '车辆', 'automobile': '汽车',
            'bus': '公交车', 'truck': '卡车', 'taxi': '出租车',
            'train': '火车', 'subway': '地铁', 'metro': '地铁',
            'airplane': '飞机', 'plane': '飞机', 'flight': '航班',
            'ship': '船', 'boat': '小船', 'vessel': '船',
            'bicycle': '自行车', 'bike': '自行车', 'motorcycle': '摩托车',
            'engine': '发动机', 'wheel': '轮子', 'tire': '轮胎',
            'brake': '刹车', 'gear': '齿轮', 'fuel': '燃料',
            'gasoline': '汽油', 'petrol': '汽油', 'diesel': '柴油',
            'road': '路', 'street': '街道', 'avenue': '大道',
            'highway': '高速公路', 'bridge': '桥', 'tunnel': '隧道',
            'crossroad': '十字路口', 'intersection': '交叉路口', 'traffic': '交通',
            'signal': '信号', 'sign': '标志', 'parking': '停车',
            # ===== 自然/天气 =====
            'nature': '自然', 'forest': '森林', 'mountain': '山',
            'hill': '小山', 'valley': '山谷', 'river': '河流',
            'lake': '湖', 'sea': '海', 'ocean': '海洋',
            'beach': '海滩', 'island': '岛屿', 'desert': '沙漠',
            'field': '田野', 'meadow': '草地', 'prairie': '草原',
            'cave': '洞穴', 'cliff': '悬崖', 'waterfall': '瀑布',
            'spring': '春天', 'summer': '夏天', 'autumn': '秋天',
            'fall': '秋天', 'winter': '冬天', 'season': '季节',
            'weather': '天气', 'sunny': '晴朗的', 'cloudy': '多云的',
            'rainy': '下雨的', 'windy': '有风的', 'snowy': '下雪的',
            'foggy': '有雾的', 'storm': '风暴', 'thunder': '雷',
            'lightning': '闪电', 'rain': '雨', 'snow': '雪',
            'wind': '风', 'cloud': '云', 'fog': '雾',
            'ice': '冰', 'frost': '霜', 'dew': '露水',
            'sun': '太阳', 'moon': '月亮', 'star': '星星',
            'planet': '行星', 'earth': '地球', 'mars': '火星',
            'sky': '天空', 'land': '陆地', 'water': '水',
            'fire': '火', 'air': '空气', 'dust': '灰尘',
            'stone': '石头', 'rock': '岩石', 'sand': '沙子',
            'mud': '泥', 'clay': '黏土', 'metal': '金属',
            'gold': '金', 'silver': '银', 'iron': '铁',
            'copper': '铜', 'steel': '钢', 'wood': '木材',
            'tree': '树', 'branch': '树枝', 'leaf': '叶子',
            'root': '根', 'trunk': '树干', 'seed': '种子',
            'flower': '花', 'grass': '草', 'bush': '灌木',
            'rose': '玫瑰', 'lily': '百合', 'tulip': '郁金香',
            'animal': '动物', 'bird': '鸟', 'fish': '鱼',
            'horse': '马', 'cow': '牛', 'pig': '猪',
            'sheep': '羊', 'goat': '山羊', 'dog': '狗',
            'cat': '猫', 'rabbit': '兔子', 'mouse': '老鼠',
            'rat': '老鼠', 'elephant': '大象', 'lion': '狮子',
            'tiger': '老虎', 'bear': '熊', 'monkey': '猴子',
            'snake': '蛇', 'frog': '青蛙', 'duck': '鸭子',
            'chicken': '鸡', 'goose': '鹅', 'fox': '狐狸',
            'wolf': '狼', 'deer': '鹿', 'camel': '骆驼',
            # ===== 时间/日期 =====
            'time': '时间', 'hour': '小时', 'minute': '分钟',
            'second': '秒', 'moment': '时刻', 'while': '一会儿',
            'day': '天', 'week': '周', 'month': '月',
            'year': '年', 'decade': '十年', 'century': '世纪',
            'today': '今天', 'tomorrow': '明天', 'yesterday': '昨天',
            'now': '现在', 'then': '那时', 'later': '稍后',
            'soon': '很快', 'recently': '最近', 'lately': '近来',
            'morning': '早上', 'afternoon': '下午', 'evening': '晚上',
            'night': '夜晚', 'midnight': '午夜', 'noon': '中午',
            'monday': '星期一', 'tuesday': '星期二', 'wednesday': '星期三',
            'thursday': '星期四', 'friday': '星期五', 'saturday': '星期六',
            'sunday': '星期日', 'january': '一月', 'february': '二月',
            'march': '三月', 'april': '四月', 'may': '五月',
            'june': '六月', 'july': '七月', 'august': '八月',
            'september': '九月', 'october': '十月', 'november': '十一月',
            'december': '十二月',
            # ===== 情感/状态 =====
            'happy': '快乐的', 'sad': '悲伤的', 'angry': '生气的',
            'excited': '兴奋的', 'surprised': '惊讶的', 'scared': '害怕的',
            'afraid': '害怕的', 'worried': '担心的', 'nervous': '紧张的',
            'calm': '平静的', 'relaxed': '放松的', 'tired': '疲倦的',
            'sleepy': '困倦的', 'hungry': '饥饿的', 'thirsty': '口渴的',
            'sick': '生病的', 'healthy': '健康的', 'strong': '强壮的',
            'weak': '虚弱的', 'young': '年轻的', 'old': '老的',
            'new': '新的', 'fresh': '新鲜的', 'ancient': '古老的',
            'modern': '现代的', 'traditional': '传统的', 'classic': '经典的',
            'popular': '流行的', 'famous': '著名的', 'important': '重要的',
            'necessary': '必要的', 'possible': '可能的', 'impossible': '不可能的',
            'certain': '确定的', 'sure': '确定的', 'doubt': '怀疑',
            'hope': '希望', 'wish': '愿望', 'dream': '梦想',
            'love': '爱', 'hate': '恨', 'like': '喜欢',
            'dislike': '不喜欢', 'prefer': '更喜欢', 'enjoy': '享受',
            'feel': '感觉', 'sense': '感觉', 'emotion': '情感',
            'feeling': '感觉', 'mood': '心情', 'attitude': '态度',
            # ===== 运动/活动 =====
            'sport': '运动', 'exercise': '锻炼', 'game': '游戏',
            'play': '玩', 'run': '跑', 'walk': '走',
            'jump': '跳', 'swim': '游泳', 'climb': '攀爬',
            'dance': '跳舞', 'sing': '唱歌', 'music': '音乐',
            'song': '歌曲', 'movie': '电影', 'film': '电影',
            'show': '节目', 'program': '节目', 'channel': '频道',
            'news': '新闻', 'information': '信息', 'message': '消息',
            'letter': '信', 'email': '电子邮件', 'phone': '电话',
            'call': '打电话', 'talk': '谈话', 'speak': '说',
            'say': '说', 'tell': '告诉', 'ask': '问',
            'answer': '回答', 'reply': '回复', 'respond': '回应',
            'discuss': '讨论', 'explain': '解释', 'describe': '描述',
            'read': '读', 'write': '写', 'listen': '听',
            'hear': '听到', 'watch': '观看', 'see': '看见',
            'look': '看', 'find': '找到', 'search': '搜索',
            'discover': '发现', 'invent': '发明', 'create': '创造',
            'make': '制作', 'build': '建造', 'construct': '建设',
            'destroy': '破坏', 'break': '打破', 'fix': '修理',
            'repair': '修理', 'clean': '清洁', 'wash': '洗',
            'cook': '烹饪', 'bake': '烘烤', 'fry': '油炸',
            'boil': '煮沸', 'cut': '切', 'slice': '切片',
            'mix': '混合', 'stir': '搅拌', 'pour': '倒',
            # ===== 形容词 =====
            'big': '大的', 'small': '小的', 'large': '大的',
            'tiny': '微小的', 'huge': '巨大的', 'enormous': '庞大的',
            'tall': '高的', 'short': '短的', 'long': '长的',
            'wide': '宽的', 'narrow': '窄的', 'thick': '厚的',
            'thin': '薄的', 'deep': '深的', 'shallow': '浅的',
            'heavy': '重的', 'light': '轻的', 'hard': '硬的',
            'soft': '软的', 'smooth': '光滑的', 'rough': '粗糙的',
            'sharp': '锋利的', 'dull': '钝的', 'round': '圆的',
            'square': '方的', 'flat': '平的', 'curved': '弯曲的',
            'straight': '直的', 'clean': '干净的', 'dirty': '脏的',
            'dry': '干的', 'wet': '湿的', 'hot': '热的',
            'cold': '冷的', 'warm': '温暖的', 'cool': '凉爽的',
            'bright': '明亮的', 'dark': '黑暗的', 'clear': '清晰的',
            'cloudy': '模糊的', 'beautiful': '美丽的', 'ugly': '丑陋的',
            'pretty': '漂亮的', 'handsome': '英俊的', 'cute': '可爱的',
            'good': '好的', 'bad': '坏的', 'better': '更好的',
            'best': '最好的', 'worse': '更坏的', 'worst': '最坏的',
            'great': '伟大的', 'excellent': '优秀的', 'perfect': '完美的',
            'terrible': '糟糕的', 'awful': '可怕的', 'wonderful': '精彩的',
            'fantastic': '极好的', 'amazing': '令人惊叹的', 'incredible': '难以置信的',
            'simple': '简单的', 'complex': '复杂的', 'easy': '容易的',
            'difficult': '困难的', 'hard': '难的', 'safe': '安全的',
            'dangerous': '危险的', 'free': '自由的', 'busy': '忙碌的',
            'empty': '空的', 'full': '满的', 'open': '打开的',
            'close': '关闭的', 'closed': '关闭的', 'public': '公共的',
            'private': '私人的', 'secret': '秘密的', 'open': '公开的',
            # ===== 代词/连词/介词 =====
            'i': '我', 'me': '我', 'my': '我的',
            'mine': '我的', 'myself': '我自己', 'we': '我们',
            'us': '我们', 'our': '我们的', 'ours': '我们的',
            'ourselves': '我们自己', 'you': '你', 'your': '你的',
            'yours': '你的', 'yourself': '你自己', 'yourselves': '你们自己',
            'he': '他', 'him': '他', 'his': '他的',
            'himself': '他自己', 'she': '她', 'her': '她',
            'hers': '她的', 'herself': '她自己', 'it': '它',
            'its': '它的', 'itself': '它自己', 'they': '他们',
            'them': '他们', 'their': '他们的', 'theirs': '他们的',
            'themselves': '他们自己', 'this': '这个', 'that': '那个',
            'these': '这些', 'those': '那些', 'who': '谁',
            'whom': '谁', 'whose': '谁的', 'which': '哪个',
            'what': '什么', 'where': '哪里', 'when': '什么时候',
            'why': '为什么', 'how': '怎样', 'whether': '是否',
            'if': '如果', 'although': '虽然', 'though': '虽然',
            'because': '因为', 'since': '既然', 'unless': '除非',
            'until': '直到', 'while': '当', 'whereas': '然而',
            'and': '和', 'or': '或', 'but': '但是',
            'so': '所以', 'yet': '然而', 'for': '因为',
            'nor': '也不', 'about': '关于', 'above': '在上方',
            'across': '穿过', 'after': '之后', 'against': '反对',
            'along': '沿着', 'among': '在之中', 'around': '周围',
            'at': '在', 'before': '之前', 'behind': '在后面',
            'below': '在下方', 'beneath': '在下方', 'beside': '在旁边',
            'between': '之间', 'beyond': '超越', 'by': '通过',
            'down': '向下', 'during': '期间', 'except': '除了',
            'from': '从', 'in': '里', 'inside': '里面',
            'into': '进入', 'near': '附近', 'of': '的',
            'off': '离开', 'on': '上', 'onto': '到上',
            'out': '外', 'outside': '外面', 'over': '上方',
            'past': '经过', 'through': '通过', 'throughout': '贯穿',
            'to': '到', 'toward': '朝向', 'under': '下方',
            'underneath': '下面', 'up': '向上', 'upon': '在上面',
            'with': '和', 'within': '在内', 'without': '没有',
            # ===== 常用动词 =====
            'be': '是', 'am': '是', 'is': '是',
            'are': '是', 'was': '是', 'were': '是',
            'been': '是', 'being': '是', 'have': '有',
            'has': '有', 'had': '有', 'having': '有',
            'do': '做', 'does': '做', 'did': '做',
            'done': '做', 'doing': '做', 'will': '将',
            'would': '将', 'shall': '将', 'should': '应该',
            'can': '能', 'could': '能', 'may': '可以',
            'might': '可能', 'must': '必须', 'ought': '应该',
            'need': '需要', 'dare': '敢', 'used': '过去',
            'get': '得到', 'got': '得到', 'gotten': '得到',
            'give': '给', 'gave': '给', 'given': '给',
            'take': '拿', 'took': '拿', 'taken': '拿',
            'come': '来', 'came': '来', 'coming': '来',
            'go': '去', 'went': '去', 'gone': '去',
            'see': '看见', 'saw': '看见', 'seen': '看见',
            'know': '知道', 'knew': '知道', 'known': '知道',
            'think': '认为', 'thought': '认为', 'thinking': '认为',
            'look': '看', 'looked': '看', 'looking': '看',
            'want': '想要', 'wanted': '想要', 'wanting': '想要',
            'use': '使用', 'used': '使用', 'using': '使用',
            'find': '找到', 'found': '找到', 'finding': '找到',
            'tell': '告诉', 'told': '告诉', 'telling': '告诉',
            'ask': '问', 'asked': '问', 'asking': '问',
            'work': '工作', 'worked': '工作', 'working': '工作',
            'seem': '似乎', 'seemed': '似乎', 'seeming': '似乎',
            'feel': '感觉', 'felt': '感觉', 'feeling': '感觉',
            'try': '尝试', 'tried': '尝试', 'trying': '尝试',
            'leave': '离开', 'left': '离开', 'leaving': '离开',
            'call': '叫', 'called': '叫', 'calling': '叫',
            'move': '移动', 'moved': '移动', 'moving': '移动',
            'live': '生活', 'lived': '生活', 'living': '生活',
            'believe': '相信', 'believed': '相信', 'believing': '相信',
            'bring': '带来', 'brought': '带来', 'bringing': '带来',
            'happen': '发生', 'happened': '发生', 'happening': '发生',
            'write': '写', 'wrote': '写', 'written': '写',
            'provide': '提供', 'provided': '提供', 'providing': '提供',
            'sit': '坐', 'sat': '坐', 'sitting': '坐',
            'stand': '站', 'stood': '站', 'standing': '站',
            'lose': '失去', 'lost': '失去', 'losing': '失去',
            'pay': '支付', 'paid': '支付', 'paying': '支付',
            'meet': '遇见', 'met': '遇见', 'meeting': '遇见',
            'include': '包括', 'included': '包括', 'including': '包括',
            'continue': '继续', 'continued': '继续', 'continuing': '继续',
            'set': '设置', 'setting': '设置',
            'learn': '学习', 'learned': '学习', 'learning': '学习',
            'change': '改变', 'changed': '改变', 'changing': '改变',
            'lead': '领导', 'led': '领导', 'leading': '领导',
            'understand': '理解', 'understood': '理解', 'understanding': '理解',
            'watch': '观看', 'watched': '观看', 'watching': '观看',
            'follow': '跟随', 'followed': '跟随', 'following': '跟随',
            'stop': '停止', 'stopped': '停止', 'stopping': '停止',
            'create': '创造', 'created': '创造', 'creating': '创造',
            'speak': '说话', 'spoke': '说话', 'spoken': '说话',
            'read': '阅读', 'reading': '阅读',
            'allow': '允许', 'allowed': '允许', 'allowing': '允许',
            'add': '添加', 'added': '添加', 'adding': '添加',
            'spend': '花费', 'spent': '花费', 'spending': '花费',
            'grow': '成长', 'grew': '成长', 'grown': '成长',
            'open': '打开', 'opened': '打开', 'opening': '打开',
            'walk': '走', 'walked': '走', 'walking': '走',
            'win': '赢', 'won': '赢', 'winning': '赢',
            'offer': '提供', 'offered': '提供', 'offering': '提供',
            'remember': '记得', 'remembered': '记得', 'remembering': '记得',
            'love': '爱', 'loved': '爱', 'loving': '爱',
            'consider': '考虑', 'considered': '考虑', 'considering': '考虑',
            'appear': '出现', 'appeared': '出现', 'appearing': '出现',
            'buy': '买', 'bought': '买', 'buying': '买',
            'wait': '等待', 'waited': '等待', 'waiting': '等待',
            'serve': '服务', 'served': '服务', 'serving': '服务',
            'die': '死', 'died': '死', 'dying': '死',
            'send': '发送', 'sent': '发送', 'sending': '发送',
            'expect': '期望', 'expected': '期望', 'expecting': '期望',
            'build': '建造', 'built': '建造', 'building': '建造',
            'stay': '停留', 'stayed': '停留', 'staying': '停留',
            'fall': '落下', 'fell': '落下', 'fallen': '落下',
            'cut': '切', 'cutting': '切',
            'reach': '到达', 'reached': '到达', 'reaching': '到达',
            'kill': '杀死', 'killed': '杀死', 'killing': '杀死',
            'remain': '保持', 'remained': '保持', 'remaining': '保持',
            'suggest': '建议', 'suggested': '建议', 'suggesting': '建议',
            'raise': '提高', 'raised': '提高', 'raising': '提高',
            'pass': '通过', 'passed': '通过', 'passing': '通过',
            'sell': '卖', 'sold': '卖', 'selling': '卖',
            'require': '需要', 'required': '需要', 'requiring': '需要',
            'report': '报告', 'reported': '报告', 'reporting': '报告',
            'decide': '决定', 'decided': '决定', 'deciding': '决定',
            'pull': '拉', 'pulled': '拉', 'pulling': '拉',
            'return': '返回', 'returned': '返回', 'returning': '返回',
            'explain': '解释', 'explained': '解释', 'explaining': '解释',
            'hope': '希望', 'hoped': '希望', 'hoping': '希望',
            'develop': '发展', 'developed': '发展', 'developing': '发展',
            'carry': '携带', 'carried': '携带', 'carrying': '携带',
            'break': '打破', 'broke': '打破', 'broken': '打破',
            'receive': '收到', 'received': '收到', 'receiving': '收到',
            'agree': '同意', 'agreed': '同意', 'agreeing': '同意',
            'support': '支持', 'supported': '支持', 'supporting': '支持',
            'hit': '打', 'hitting': '打',
            'produce': '生产', 'produced': '生产', 'producing': '生产',
            'eat': '吃', 'ate': '吃', 'eaten': '吃',
            'cover': '覆盖', 'covered': '覆盖', 'covering': '覆盖',
            'catch': '抓住', 'caught': '抓住', 'catching': '抓住',
            'draw': '画', 'drew': '画', 'drawn': '画',
            'choose': '选择', 'chose': '选择', 'chosen': '选择',
        }

        zh_to_en = {v: k for k, v in en_to_zh.items() if v}

        # 根据语言方向选择翻译表
        if source_lang == 'en' and target_lang == 'zh':
            # 英译中 - 先尝试短语匹配
            lower_text = text.lower().strip()
            
            # 1. 检查是否有完整短语匹配
            if lower_text in phrase_to_zh:
                return f'[模拟翻译] {phrase_to_zh[lower_text]}'
            
            # 2. 检查是否有部分短语需要替换
            result = text
            for phrase, zh_translation in sorted(phrase_to_zh.items(), key=lambda x: -len(x[0])):
                # 使用正则表达式进行大小写不敏感的替换
                import re
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                if pattern.search(result):
                    result = pattern.sub(zh_translation, result)
            
            # 3. 对剩余的单词逐词翻译（支持词形还原）
            if result == text:  # 没有短语匹配
                words = text.split()
                result_parts = []
                for word in words:
                    clean_word = word.rstrip('.,!?;:()[]{}"\'')
                    punctuation = word[len(clean_word):]
                    lower_word = clean_word.lower()
                    translated = self._lookup_word(lower_word, en_to_zh)
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
        # 模拟模式：优先尝试腾讯云翻译，然后是免费在线翻译API，最后回退到本地模拟翻译
        if self.simulation_mode:
            # 对长文本按句子分割逐句翻译，确保每句都被正确处理
            if len(text) > 200:
                sentences = re.split(r'(?<=[.!?\n])\s+', text)
                translated_sentences = []
                tencent_translator = TencentCloudTranslator()
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    # 1. 优先尝试腾讯云翻译
                    if not tencent_translator.simulation_mode:
                        try:
                            tencent_result = tencent_translator.translate(sentence, source_lang or 'auto', target_lang)
                            if tencent_result:
                                translated_sentences.append(tencent_result)
                                continue
                        except Exception as e:
                            print(f'腾讯云翻译失败: {e}')

                    # 2. 腾讯云失败，尝试 LibreTranslate
                    libre_result = _call_libretranslate(sentence, source_lang or 'en', target_lang)
                    if libre_result and not _is_mostly_english(libre_result):
                        translated_sentences.append(libre_result)
                        continue

                    # 3. LibreTranslate失败，尝试 MyMemory 备用API
                    mymemory_result = _call_mymemory(sentence, source_lang or 'en', target_lang)
                    if mymemory_result and not _is_mostly_english(mymemory_result):
                        translated_sentences.append(mymemory_result)
                        continue

                    # 4. 在线API都失败，回退到本地模拟翻译
                    local_result = self._simulate_translate(sentence, source_lang or 'en', target_lang)
                    translated_sentences.append(local_result)
                
                return ' '.join(translated_sentences)
            
            # 短文本直接翻译
            tencent_translator = TencentCloudTranslator()
            
            # 1. 优先尝试腾讯云翻译
            if not tencent_translator.simulation_mode:
                try:
                    tencent_result = tencent_translator.translate(text, source_lang or 'auto', target_lang)
                    if tencent_result:
                        print(f'使用腾讯云翻译成功')
                        return tencent_result
                except Exception as e:
                    print(f'腾讯云翻译失败: {e}')

            # 2. 腾讯云失败，尝试 LibreTranslate
            libre_result = _call_libretranslate(text, source_lang or 'en', target_lang)
            if libre_result:
                print(f'使用 LibreTranslate 翻译成功')
                return libre_result

            # 3. LibreTranslate失败，尝试 MyMemory 备用API
            mymemory_result = _call_mymemory(text, source_lang or 'en', target_lang)
            if mymemory_result:
                print(f'使用 MyMemory 翻译成功')
                return mymemory_result

            # 4. 在线API都失败，回退到本地模拟翻译
            import time
            time.sleep(0.3)
            print(f'使用本地模拟翻译')
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
    """初始化翻译客户端 - 优先使用腾讯云翻译"""
    global translator
    if translator is None:
        tencent_translator = TencentCloudTranslator()
        if not tencent_translator.simulation_mode:
            print('使用腾讯云翻译服务')
            translator = tencent_translator
        else:
            volc_translator = VolcEngineTranslator()
            if not volc_translator.simulation_mode:
                print('使用火山引擎翻译服务')
            else:
                print('使用免费在线翻译服务')
            translator = volc_translator
    return translator


def is_simulation_mode():
    """是否为模拟模式"""
    t = init_translator()
    return t.simulation_mode


def translate_text(text, source_lang, target_lang, use_glossary=True, use_memory=True):
    """
    翻译文本（支持术语表和记忆库）

    Args:
        text: 待翻译文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
        use_glossary: 是否使用术语表（默认True）
        use_memory: 是否使用记忆库（默认True）

    Returns:
        dict: 包含翻译结果和术语匹配信息
            - translation: 翻译后的文本
            - glossary_matches: 匹配的术语列表
            - simulation: 是否为模拟模式
            - from_memory: 是否来自记忆库
            - memory_id: 记忆库条目ID（如果来自记忆库）
    """
    t = init_translator()

    lang_map = {
        'zh': 'zh',
        'en': 'en',
        'ja': 'ja',
        'ko': 'ko',
        'de': 'de',
        'fr': 'fr',
        'es': 'es',
        'pt': 'pt',
        'ru': 'ru',
        'it': 'it',
        'vi': 'vi',
        'th': 'th',
        'ar': 'ar',
        'auto': None,
    }

    source_lang_code = lang_map.get(source_lang, source_lang)
    target_lang_code = lang_map.get(target_lang, target_lang)

    if source_lang_code and source_lang_code == target_lang_code:
        return {
            'translation': text,
            'glossary_matches': [],
            'simulation': t.simulation_mode,
            'from_memory': False,
            'memory_id': None
        }

    if use_memory:
        try:
            from translation_memory_service import get_similar_translation, increment_usage
            if source_lang_code:
                similar_entry = get_similar_translation(
                    text, source_lang_code, target_lang_code, min_confidence=0.85
                )
                if similar_entry:
                    increment_usage(similar_entry['id'])
                    return {
                        'translation': similar_entry['target_text'],
                        'glossary_matches': similar_entry.get('glossary_matches', []),
                        'simulation': t.simulation_mode,
                        'from_memory': True,
                        'memory_id': similar_entry['id']
                    }
        except Exception as e:
            print(f'记忆库查询失败: {e}')

    term_mapping = {}
    processed_text = text
    glossary_matches = []

    if use_glossary:
        processed_text, term_mapping = apply_glossary_to_translation(text, source_lang, target_lang)

    translated_text = t.translate(processed_text, source_lang_code, target_lang_code)

    if term_mapping:
        translated_text = restore_glossary_terms(translated_text, term_mapping)

    if term_mapping:
        from glossary_service import get_glossary_list
        all_terms = get_glossary_list(source_lang, target_lang)
        import re
        for term in all_terms:
            flags = 0 if term.get('case_sensitive', False) else re.IGNORECASE
            if re.search(r'\b' + re.escape(term['source_term']) + r'\b', text, flags):
                glossary_matches.append({
                    'source_term': term['source_term'],
                    'target_term': term['target_term'],
                    'id': term['id']
                })

    if use_memory:
        try:
            from translation_memory_service import add_memory_entry
            actual_source_lang = source_lang_code if source_lang_code else 'auto'
            add_memory_entry(
                text, translated_text,
                actual_source_lang, target_lang_code,
                confidence=1.0,
                glossary_matches=glossary_matches
            )
        except Exception as e:
            print(f'记忆库保存失败: {e}')

    return {
        'translation': translated_text,
        'glossary_matches': glossary_matches,
        'simulation': t.simulation_mode,
        'from_memory': False,
        'memory_id': None
    }