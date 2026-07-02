import cv2
import numpy as np
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


def _parse_ocr_result(result):
    """
    解析PaddleOCR返回结果

    PaddleOCR返回格式:
    [
        [
            [bbox, (text, score)],
            [bbox, (text, score)],
            ...
        ]
    ]

    Args:
        result: PaddleOCR返回的结果

    Returns:
        tuple: (识别出的文本, 平均置信度)
    """
    if not result or not result[0]:
        return '', 0.0

    text_parts = []
    total_confidence = 0
    count = 0

    for item in result[0]:
        if len(item) >= 2:
            text_score = item[1]
            if isinstance(text_score, tuple) and len(text_score) >= 2:
                text = text_score[0]
                score = text_score[1]
                if text and text.strip():
                    text_parts.append(text.strip())
                    total_confidence += score
                    count += 1

    full_text = '\n'.join(text_parts)
    avg_confidence = total_confidence / count if count > 0 else 0.0

    return full_text, avg_confidence


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
