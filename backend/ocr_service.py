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

    if not result or not result[0]:
        return '', 0.0

    ocr_result = result[0]
    rec_texts = ocr_result.get('rec_texts', [])
    rec_scores = ocr_result.get('rec_scores', [])

    text_parts = []
    total_confidence = 0
    count = 0

    for text, score in zip(rec_texts, rec_scores):
        if text.strip():
            text_parts.append(text)
            total_confidence += score
            count += 1

    full_text = '\n'.join(text_parts)
    avg_confidence = total_confidence / count if count > 0 else 0.0

    return full_text, avg_confidence


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

    if not result or not result[0]:
        return '', 0.0

    ocr_result = result[0]
    rec_texts = ocr_result.get('rec_texts', [])
    rec_scores = ocr_result.get('rec_scores', [])

    text_parts = []
    total_confidence = 0
    count = 0

    for text, score in zip(rec_texts, rec_scores):
        if text.strip():
            text_parts.append(text)
            total_confidence += score
            count += 1

    full_text = '\n'.join(text_parts)
    avg_confidence = total_confidence / count if count > 0 else 0.0

    return full_text, avg_confidence
