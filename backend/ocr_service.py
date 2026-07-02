import cv2
import numpy as np
import re
from paddleocr import PaddleOCR


ocr = None


def init_ocr():
    """初始化PaddleOCR"""
    global ocr
    if ocr is None:
        ocr = PaddleOCR(
            lang='ch',
            use_textline_orientation=True
        )
    return ocr


def _extract_lines_with_coords(result):
    """
    从OCR结果中提取每行的文本和坐标信息
    
    Args:
        result: PaddleOCR返回的结果
        
    Returns:
        list: 每行的信息，格式为 {'text': str, 'y': float, 'height': float, 'x': float, 'score': float}
    """
    if not result or not result[0]:
        return []

    lines = []
    for item in result[0]:
        if len(item) >= 2:
            bbox = item[0]
            text_score = item[1]
            if isinstance(text_score, tuple) and len(text_score) >= 2:
                text = text_score[0]
                score = text_score[1]
                if text and text.strip():
                    # bbox格式: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    y_coords = [point[1] for point in bbox]
                    x_coords = [point[0] for point in bbox]
                    y = sum(y_coords) / len(y_coords)
                    height = max(y_coords) - min(y_coords)
                    x = sum(x_coords) / len(x_coords)
                    lines.append({
                        'text': text.strip(),
                        'y': y,
                        'height': height,
                        'x': x,
                        'score': score
                    })
    return lines


def _merge_lines(lines):
    """
    智能合并行：按Y坐标排序，相邻行合并，跨段保留换行
    
    Args:
        lines: 每行的信息列表
        
    Returns:
        tuple: (合并后的段落列表, 平均行高)
    """
    if not lines:
        return [], 0.0

    # 按Y坐标排序
    lines_sorted = sorted(lines, key=lambda l: (l['y'], l['x']))

    # 计算平均行高
    avg_height = sum(line['height'] for line in lines_sorted) / len(lines_sorted)

    # 将行分组到视觉行
    visual_lines = []
    current_line = []
    for i, line in enumerate(lines_sorted):
        if i == 0:
            current_line.append(line)
            continue

        prev_line = lines_sorted[i - 1]
        y_diff = abs(line['y'] - prev_line['y'])

        if y_diff < avg_height * 0.8:
            current_line.append(line)
        else:
            visual_lines.append(current_line)
            current_line = [line]

    if current_line:
        visual_lines.append(current_line)

    # 将视觉行转换为文本
    line_texts = []
    for vline in visual_lines:
        vline_sorted = sorted(vline, key=lambda l: l['x'])
        texts = [p['text'] for p in vline_sorted]
        line_texts.append(' '.join(texts))

    # 按段落分组（段落间距 > 行高 × 1.5）
    paragraphs = []
    current_paragraph = [line_texts[0]]
    
    for i in range(1, len(line_texts)):
        prev_line_info = visual_lines[i - 1][0]
        curr_line_info = visual_lines[i][0]
        y_diff = abs(curr_line_info['y'] - prev_line_info['y'])
        
        if y_diff > avg_height * 1.5:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = [line_texts[i]]
        else:
            current_paragraph.append(line_texts[i])
    
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))

    return paragraphs, avg_height


def _split_joined_words(text):
    """
    分割连在一起的英文单词（基于词典的动态规划分割）
    
    Args:
        text: 可能包含连写单词的文本
        
    Returns:
        str: 分割后的文本
    """
    # 常用英文单词集合（用于分割）
    common_words = {
        'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'from', 'by', 'with', 
        'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 
        'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 
        'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 
        'so', 'than', 'too', 'very', 'just', 'but', 'and', 'or', 'if', 'because', 
        'until', 'while', 'this', 'that', 'these', 'those', 'i', 'me', 'my', 
        'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 
        'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 
        'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'whose', 'is', 
        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
        'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 
        'shall', 'need', 'dare', 'used', 'get', 'got', 'give', 'gave', 'taken', 
        'take', 'come', 'came', 'go', 'went', 'seen', 'see', 'knew', 'know', 
        'thought', 'think', 'look', 'looked', 'want', 'wanted', 'use', 'used', 
        'find', 'found', 'told', 'tell', 'asked', 'ask', 'work', 'worked', 
        'feel', 'felt', 'tried', 'try', 'left', 'leave', 'called', 'call', 
        'moved', 'move', 'lived', 'live', 'believed', 'believe', 'brought', 
        'bring', 'happened', 'happen', 'wrote', 'write', 'provided', 'provide', 
        'sat', 'sit', 'stood', 'stand', 'lost', 'lose', 'paid', 'pay', 'met', 
        'meet', 'included', 'include', 'continued', 'continue', 'learned', 
        'learn', 'changed', 'change', 'led', 'lead', 'understood', 'understand', 
        'watched', 'watch', 'followed', 'follow', 'stopped', 'stop', 'created', 
        'create', 'spoke', 'speak', 'read', 'allowed', 'allow', 'added', 'add', 
        'spent', 'spend', 'grew', 'grow', 'opened', 'open', 'walked', 'walk', 
        'won', 'win', 'offered', 'offer', 'remembered', 'remember', 'loved', 
        'love', 'considered', 'consider', 'appeared', 'appear', 'bought', 'buy', 
        'waited', 'wait', 'served', 'serve', 'died', 'die', 'sent', 'send', 
        'expected', 'expect', 'built', 'build', 'stayed', 'stay', 'fell', 'fall', 
        'cut', 'reached', 'reach', 'killed', 'kill', 'remained', 'remain', 
        'suggested', 'suggest', 'raised', 'raise', 'passed', 'pass', 'sold', 
        'sell', 'required', 'require', 'reported', 'report', 'decided', 'decide', 
        'pulled', 'pull', 'returned', 'return', 'explained', 'explain', 'hoped', 
        'hope', 'developed', 'develop', 'carried', 'carry', 'broke', 'break', 
        'received', 'receive', 'agreed', 'agree', 'supported', 'support', 'hit', 
        'produced', 'produce', 'ate', 'eat', 'covered', 'cover', 'caught', 'catch', 
        'drew', 'draw', 'chose', 'choose', 'narcissus', 'echo', 'nymph', 'nymphs', 
        'maiden', 'goddess', 'prayer', 'cruelty', 'case', 'instance', 'rest', 
        'poor', 'day', 'endeavored', 'attract', 'uttered', 'avenging', 'heard', 
        'granted', 'feel', 'meet', 'return', 'affection', 'vain', 'time', 'other', 
        'what', 'was', 'to', 'love'
    }
    
    def split_word(joined):
        """使用动态规划分割单个连写单词"""
        n = len(joined)
        dp = [float('inf')] * (n + 1)
        dp[0] = 0
        prev = [-1] * (n + 1)
        
        for i in range(1, n + 1):
            for j in range(i):
                word = joined[j:i].lower()
                if word in common_words and dp[j] + 1 < dp[i]:
                    dp[i] = dp[j] + 1
                    prev[i] = j
        
        if dp[n] == float('inf'):
            return joined
        
        words = []
        i = n
        while i > 0:
            j = prev[i]
            words.append(joined[j:i])
            i = j
        
        return ' '.join(reversed(words))
    
    # 分割文本中的连写单词
    words = re.findall(r'[a-zA-Z]+', text)
    new_words = []
    for word in words:
        if len(word) > 6:
            split_result = split_word(word)
            if ' ' in split_result:
                new_words.extend(split_result.split())
            else:
                new_words.append(word)
        else:
            new_words.append(word)
    
    # 保留非字母内容
    result = []
    word_idx = 0
    for match in re.finditer(r'([a-zA-Z]+)|([^a-zA-Z]+)', text):
        if match.group(1):
            if word_idx < len(new_words):
                result.append(new_words[word_idx])
                word_idx += 1
        else:
            result.append(match.group(2))
    
    return ''.join(result)


def _fix_punctuation(text):
    """
    修复标点：大写首字母、补全句末标点、修复常见OCR错误
    
    Args:
        text: 输入文本
        
    Returns:
        str: 修复后的文本
    """
    # 修复常见OCR错误
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('，', ',').replace('。', '.')
    text = text.replace('！', '!').replace('？', '?')
    text = text.replace('；', ';').replace('：', ':')
    text = text.replace('（', '(').replace('）', ')')
    text = text.replace('—', '-').replace('–', '-')

    # 修复连续的标点
    text = re.sub(r',+', ',', text)
    text = re.sub(r'\.+', '.', text)
    text = re.sub(r'!+', '!', text)
    text = re.sub(r'\?+', '?', text)

    # 修复句首小写字母（非引号内）
    sentences = re.split(r'(?<=[.!?])\s+', text)
    fixed_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # 去掉开头的引号
        stripped = sentence.lstrip('"\'')
        if stripped and stripped[0].islower():
            if len(stripped) == 1:
                fixed = sentence[:-len(stripped)] + stripped[0].upper()
            else:
                fixed = sentence[:-len(stripped)] + stripped[0].upper() + stripped[1:]
            fixed_sentences.append(fixed)
        else:
            fixed_sentences.append(sentence)

    return ' '.join(fixed_sentences)


def _reconstruct_sentences(text):
    """
    断句重组：按句子边界拆分，重组完整句子
    
    Args:
        text: 输入文本
        
    Returns:
        str: 重组后的文本
    """
    # 按句子边界拆分
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # 清理空句子
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 确保每个句子以大写字母开头，以标点结尾
    fixed_sentences = []
    for sentence in sentences:
        if not sentence:
            continue
        
        # 确保句首大写
        stripped = sentence.lstrip('"\'([')
        if stripped and stripped[0].islower():
            prefix = sentence[:-len(stripped)]
            sentence = prefix + stripped[0].upper() + stripped[1:]
        
        # 确保句末有标点（如果看起来像一个完整句子）
        last_char = sentence[-1]
        if last_char not in '.!?":;\')':
            # 判断是否是完整句子（包含动词等）
            if re.search(r'\b(is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|can|could|may|might|must|should|shall|need|dare|used|get|give|take|come|go|see|know|think|look|want|use|find|tell|ask|work|feel|try|leave|call|move|live|believe|bring|happen|write|provide|sit|stand|lose|pay|meet|include|continue|set|learn|change|lead|understand|watch|follow|stop|create|speak|read|allow|add|spend|grow|open|walk|win|offer|remember|love|consider|appear|buy|wait|serve|die|send|expect|build|stay|fall|cut|reach|kill|remain|suggest|raise|pass|sell|require|report|decide|pull|return|explain|hope|develop|carry|break|receive|agree|support|hit|produce|eat|cover|catch|draw|choose)\b', sentence, re.IGNORECASE):
                sentence += '.'
        
        fixed_sentences.append(sentence)
    
    return ' '.join(fixed_sentences)


def _postprocess_ocr_text(lines):
    """
    OCR文本后处理：合并行、修复标点、重组句子
    
    Args:
        lines: 每行的信息列表
        
    Returns:
        str: 处理后的最终文本
    """
    if not lines:
        return ''

    # 步骤1：智能合并行
    paragraphs, avg_height = _merge_lines(lines)
    print(f'[OCR后处理] 合并前行数: {len(lines)}, 合并后段落数: {len(paragraphs)}')
    print(f'[OCR后处理] 合并前的行列表:')
    for i, line in enumerate(sorted(lines, key=lambda l: (l['y'], l['x']))):
        print(f'  [{i}] y={line["y"]:.1f} h={line["height"]:.1f} x={line["x"]:.1f} score={line["score"]:.2f} | {line["text"]}')
    print(f'[OCR后处理] 合并后的段落:')
    for i, para in enumerate(paragraphs):
        print(f'  [{i}] {para}')

    # 步骤2：拼接所有段落（段落间用换行）
    full_text = '\n'.join(paragraphs)

    # 步骤3：分割连在一起的单词
    text_after_splitting = _split_joined_words(full_text)
    print(f'[OCR后处理] 分割连写单词后:')
    print(f'  {text_after_splitting}')

    # 步骤4：修复标点
    text_after_punctuation = _fix_punctuation(text_after_splitting)
    print(f'[OCR后处理] 修复标点后:')
    print(f'  {text_after_punctuation}')

    # 步骤5：断句重组
    final_text = _reconstruct_sentences(text_after_punctuation)
    print(f'[OCR后处理] 断句重组后最终文本:')
    print(f'  {final_text}')

    return final_text


def _parse_ocr_result(result):
    """
    解析PaddleOCR返回结果（带后处理优化）
    
    Args:
        result: PaddleOCR返回的结果
        
    Returns:
        tuple: (识别出的文本, 平均置信度)
    """
    if not result or not result[0]:
        return '', 0.0

    # 提取行信息（包含坐标）
    lines = _extract_lines_with_coords(result)
    
    if not lines:
        return '', 0.0

    # 计算平均置信度
    total_confidence = sum(line['score'] for line in lines)
    avg_confidence = total_confidence / len(lines)

    # 后处理
    final_text = _postprocess_ocr_text(lines)

    return final_text, avg_confidence


def perform_ocr(image_path):
    """
    使用PaddleOCR对图片进行文字识别

    Args:
        image_path: 图片文件路径

    Returns:
        tuple: (识别出的文本, 平均置信度)
    """
    ocr = init_ocr()
    result = ocr.ocr(image_path)
    return _parse_ocr_result(result)


def perform_ocr_from_bytes(image_bytes):
    """
    使用PaddleOCR对图片字节流进行文字识别

    Args:
        image_bytes: 图片字节数据

    Returns:
        tuple: (识别出的文本, 平均置信度)
    """
    ocr = init_ocr()

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result = ocr.ocr(img)
    return _parse_ocr_result(result)
