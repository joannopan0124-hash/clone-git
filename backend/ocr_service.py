import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os


def perform_ocr(file_path):
    """
    对文件进行OCR识别

    Args:
        file_path: 文件路径

    Returns:
        tuple: (识别出的文本, 置信度)
    """
    file_ext = file_path.rsplit('.', 1)[1].lower()

    if file_ext == 'pdf':
        # PDF文件处理
        images = convert_from_path(file_path)
        text_parts = []
        total_confidence = 0

        for image in images:
            # 使用tesseract进行OCR
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            text = pytesseract.image_to_string(image)

            # 计算平均置信度
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            text_parts.append(text)
            total_confidence += avg_confidence

        full_text = '\n'.join(text_parts)
        avg_confidence = total_confidence / len(images) if images else 0

        return full_text, avg_confidence / 100  # 转换为0-1范围

    else:
        # 图片文件处理
        image = Image.open(file_path)

        # 使用tesseract进行OCR
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        text = pytesseract.image_to_string(image)

        # 计算平均置信度
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return text, avg_confidence / 100  # 转换为0-1范围