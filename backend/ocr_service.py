import os
# 禁用OneDNN以避免PaddlePaddle兼容性问题
os.environ['FLAGS_use_mkldnn'] = '0'

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
            use_angle_cls=True,
            show_log=False
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


def _build_word_dictionary():
    """构建英文单词词典（用于分割连写单词）"""
    word_set = set()
    # 从 translate_service.py 源文件中提取词典键
    try:
        import os
        ts_path = os.path.join(os.path.dirname(__file__), 'translate_service.py')
        with open(ts_path, 'r', encoding='utf-8') as f:
            source = f.read()
        # 提取 'word': '翻译' 格式的键
        for match in re.finditer(r"'([a-zA-Z]+)':\s*'", source):
            word_set.add(match.group(1).lower())
    except Exception as e:
        print(f'[词典加载] 从 translate_service.py 提取失败: {e}')

    # 补充常见单词（确保覆盖基础词汇）
    extra_words = """
    the be to of and a in that have i it for not on with he as you do at
    this but his by from they we say her she or an will my one all would
    there their what so up out if about who get which go me when make can
    like time no just him know take people into year your good some could
    them see other than then now look only come its over think also back
    after use two how our work first well way even new want because any
    these give day most us is are was were been being am had has have does
    did will would should could may might must shall need dare said says
    one two three four five six seven eight nine ten hundred thousand
    he she it they we you i me him her them us my your his its our their
    this that these those here there where when why how what which who whom
    has had was were is are am be been being do does did done doing
    get got gotten give gave given go went gone come came see saw seen
    know knew known think thought take took taken make made find found
    tell told say said want wanted use used feel felt try tried leave left
    call called move moved live lived believe believed bring brought happen happened
    write wrote provide provided sit sat stand stood lose lost pay paid
    meet met include included continue continued learn learned change changed
    lead led understand understood watch watched follow followed stop stopped
    create created speak spoke read allow allowed add added spend spent
    grow grew open opened walk walked win won offer offered remember remembered
    love loved consider considered appear appeared buy bought wait waited
    serve served die died send sent expect expected build built stay stayed
    fall fell cut reach reached kill killed remain remained suggest suggested
    raise raised pass passed sell sold require required report reported
    decide decided pull pulled return returned explain explained hope hoped
    develop developed carry carried break broke receive received agree agreed
    support supported hit produce produced eat ate cover covered catch caught
    draw drew choose chose
    shun shunned shuns shunning done doing
    who whom whose which that what where when why how
    all any some no not nor only own same so than too very
    can could may might must shall should will would need dare
    about above across after against along among around at before behind
    below beneath beside between beyond by down during except for from in
    inside into near of off on onto out outside over past through throughout
    to toward under underneath up upon with within without
    case instance rest poor day vain time other return affection
    prayer goddess maiden nymph echo narcissus cruelty avenging
    heard granted feel meet uttered endeavored attract
    might some sometime one another him her his their
    had done was were has have been is are am
    to of and the in on at for with as by from
    it its it's that this these those
    not no nor or but and if because while until when where
    would could should might must may will shall
    him her them us you me it
    his her their our your my its
    all some any no every each few more most other
    one two three first second last next
    here there now then today tomorrow yesterday
    great small large big little good bad new old young
    love hate like want need feel think know see hear
    man woman boy girl child children people person
    day night morning evening week month year time
    water air fire earth sun moon star sky
    hand foot head eye ear nose mouth
    heart mind soul body life death
    home house room door window
    food drink eat cook make build
    walk run jump swim fly drive ride
    read write speak talk tell ask answer
    work play rest sleep wake dream
    open close start stop begin end finish
    come go arrive leave return stay
    give take send receive bring carry
    buy sell pay cost spend save
    make do have get put set
    look see watch find search
    hear listen sound noise music
    beauty beautiful ugly pretty handsome
    true false right wrong good bad
    happy sad angry afraid scared
    hot cold warm cool dry wet
    fast slow quick easy hard difficult
    full empty open close shut
    light dark bright black white
    long short tall high low
    wide narrow thick thin deep
    heavy light hard soft
    strong weak power energy
    young old new ancient modern
    first last next previous
    single double half whole
    public private secret open
    free busy empty full
    clean dirty dry wet
    safe dangerous wild
    sound voice word letter
    book page chapter story tale
    mountain hill valley river lake sea ocean
    tree flower grass forest wood
    bird fish horse cow dog cat
    red blue green yellow black white
    north south east west
    spring summer autumn winter
    monday tuesday wednesday thursday friday saturday sunday
    january february march april may june july august september october november december
    """.split()
    for w in extra_words:
        w = w.strip().lower()
        if w and w.isalpha():
            word_set.add(w)

    return word_set


# 构建词典（模块加载时执行一次）
_WORD_DICT = None
def _get_word_dict():
    global _WORD_DICT
    if _WORD_DICT is None:
        _WORD_DICT = _build_word_dictionary()
    return _WORD_DICT


def _split_joined_words(text):
    """
    分割连在一起的英文单词（基于词典的动态规划分割）
    
    Args:
        text: 可能包含连写单词的文本
        
    Returns:
        str: 分割后的文本
    """
    word_dict = _get_word_dict()
    
    def split_word(joined):
        """使用动态规划分割单个连写单词，返回最优分割
        
        代价函数设计：
        - 每个词的基础代价 = 1.0（鼓励更少的词）
        - 长词折扣 = 1.0/length（长词代价更低，鼓励长词）
        - 短词惩罚：1-2字符的词额外加 3.0 惩罚（避免过度分割成 a, th 等）
        - 总代价 = sum(1.0 + 1.0/length + penalty)
        这样 'that|he|might' (3.25+2.5+2.2=7.95) 会优于 'th|a|the|might' (5.5+5.0+3.33+2.2=16.03)
        """
        n = len(joined)
        if n <= 3:
            return joined

        MAX_WORD_LEN = 20

        # dp[i] = (最小代价, 上一个分割点j)
        dp = [None] * (n + 1)
        dp[0] = (0.0, -1)

        for i in range(1, n + 1):
            best = None
            # 尝试所有可能的单词长度（1~MAX_WORD_LEN）
            for length in range(1, min(i, MAX_WORD_LEN) + 1):
                j = i - length
                if dp[j] is None:
                    continue
                word = joined[j:i].lower()
                if word in word_dict:
                    # 基础代价1.0 + 长词折扣1.0/length
                    word_cost = 1.0 + 1.0 / length
                    # 短词惩罚（1-2字符的词很可能是误分割）
                    if length <= 2:
                        word_cost += 3.0
                    total_cost = dp[j][0] + word_cost
                    if best is None or total_cost < best[0]:
                        best = (total_cost, j)

            if best is not None:
                dp[i] = best

        # 回溯找分割方案
        if dp[n] is None:
            return joined

        words = []
        i = n
        while i > 0:
            if dp[i] is None:
                return joined
            j = dp[i][1]
            if j < 0:
                words.append(joined[:i])
                break
            words.append(joined[j:i])
            i = j

        words.reverse()

        # 验证：所有分割出的词都在词典中
        for w in words:
            if w.lower() not in word_dict:
                return joined

        # 只有分割成2个以上词时才返回分割结果
        if len(words) >= 2:
            return ' '.join(words)
        return joined
    
    # 使用正则分割文本：字母序列 和 非字母序列
    result = []
    for match in re.finditer(r'[a-zA-Z]+|[^a-zA-Z]+', text):
        token = match.group()
        if token[0].isalpha() and len(token) > 4:
            # 尝试分割连写单词
            split_result = split_word(token)
            result.append(split_result)
        else:
            result.append(token)
    
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

    # 在标点后插入缺失的空格（OCR常见问题：标点后直接跟字母，无空格）
    # 句号/问号/感叹号 后跟大写字母 → 句子边界，插入空格
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    # 逗号/分号/冒号 后跟任意字母 → 插入空格
    text = re.sub(r'([,;:])([a-zA-Z])', r'\1 \2', text)
    # 句号后跟小写字母也插入空格（可能是OCR漏掉的空格）
    text = re.sub(r'([.])([a-z])', r'\1 \2', text)

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
