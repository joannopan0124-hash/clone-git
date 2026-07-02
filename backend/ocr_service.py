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

    # 步骤3：修复标点
    text_after_punctuation = _fix_punctuation(full_text)
    print(f'[OCR后处理] 修复标点后:')
    print(f'  {text_after_punctuation}')

    # 步骤4：断句重组
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
