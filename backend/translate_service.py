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
            
            # 3. 对剩余的单词逐词翻译
            if result == text:  # 没有短语匹配
                words = text.split()
                result_parts = []
                for word in words:
                    clean_word = word.rstrip('.,!?;:()[]{}"\'')
                    punctuation = word[len(clean_word):]
                    lower_word = clean_word.lower()
                    if lower_word in en_to_zh:
                        translated = en_to_zh[lower_word]
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