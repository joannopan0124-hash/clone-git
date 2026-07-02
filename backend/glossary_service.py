"""
术语表服务模块

作为翻译记忆库，支持自定义术语的规则翻译
"""

import os
import json
import re
from typing import List, Dict, Optional, Tuple


# 术语表存储路径
GLOSSARY_DIR = '/tmp/glossary'
GLOSSARY_FILE = os.path.join(GLOSSARY_DIR, 'glossary.json')


def _ensure_glossary_dir():
    """确保术语表目录存在"""
    os.makedirs(GLOSSARY_DIR, exist_ok=True)


def _load_glossary() -> List[Dict]:
    """
    加载术语表

    Returns:
        List[Dict]: 术语列表
    """
    _ensure_glossary_dir()
    if not os.path.exists(GLOSSARY_FILE):
        return []
    try:
        with open(GLOSSARY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_glossary(glossary: List[Dict]):
    """
    保存术语表

    Args:
        glossary: 术语列表
    """
    _ensure_glossary_dir()
    with open(GLOSSARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)


def get_glossary_list(source_lang: str = None, target_lang: str = None) -> List[Dict]:
    """
    获取术语表列表

    Args:
        source_lang: 源语言过滤（可选）
        target_lang: 目标语言过滤（可选）

    Returns:
        List[Dict]: 术语列表
    """
    glossary = _load_glossary()
    
    if source_lang:
        glossary = [g for g in glossary if g.get('source_lang') == source_lang]
    if target_lang:
        glossary = [g for g in glossary if g.get('target_lang') == target_lang]
    
    return glossary


def add_glossary_term(
    source_term: str,
    target_term: str,
    source_lang: str,
    target_lang: str,
    description: str = '',
    case_sensitive: bool = False,
    priority: int = 0
) -> Dict:
    """
    添加术语

    Args:
        source_term: 源术语
        target_term: 目标术语（译文）
        source_lang: 源语言
        target_lang: 目标语言
        description: 描述说明（可选）
        case_sensitive: 是否区分大小写
        priority: 优先级（数字越大优先级越高）

    Returns:
        Dict: 添加的术语条目
    """
    glossary = _load_glossary()
    
    # 检查是否已存在相同术语
    for g in glossary:
        if g['source_term'] == source_term and g['source_lang'] == source_lang and g['target_lang'] == target_lang:
            # 更新现有术语
            g['target_term'] = target_term
            g['description'] = description
            g['case_sensitive'] = case_sensitive
            g['priority'] = priority
            g['updated_at'] = _get_timestamp()
            _save_glossary(glossary)
            return g
    
    # 添加新术语
    term = {
        'id': _generate_id(),
        'source_term': source_term,
        'target_term': target_term,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'description': description,
        'case_sensitive': case_sensitive,
        'priority': priority,
        'created_at': _get_timestamp(),
        'updated_at': _get_timestamp()
    }
    glossary.append(term)
    _save_glossary(glossary)
    return term


def update_glossary_term(
    term_id: str,
    source_term: str = None,
    target_term: str = None,
    source_lang: str = None,
    target_lang: str = None,
    description: str = None,
    case_sensitive: bool = None,
    priority: int = None
) -> Optional[Dict]:
    """
    更新术语

    Args:
        term_id: 术语ID
        其他参数: 要更新的字段（可选）

    Returns:
        Dict: 更新后的术语条目，如果不存在返回None
    """
    glossary = _load_glossary()
    
    for g in glossary:
        if g['id'] == term_id:
            if source_term is not None:
                g['source_term'] = source_term
            if target_term is not None:
                g['target_term'] = target_term
            if source_lang is not None:
                g['source_lang'] = source_lang
            if target_lang is not None:
                g['target_lang'] = target_lang
            if description is not None:
                g['description'] = description
            if case_sensitive is not None:
                g['case_sensitive'] = case_sensitive
            if priority is not None:
                g['priority'] = priority
            g['updated_at'] = _get_timestamp()
            _save_glossary(glossary)
            return g
    
    return None


def delete_glossary_term(term_id: str) -> bool:
    """
    删除术语

    Args:
        term_id: 术语ID

    Returns:
        bool: 是否删除成功
    """
    glossary = _load_glossary()
    
    new_glossary = [g for g in glossary if g['id'] != term_id]
    
    if len(new_glossary) < len(glossary):
        _save_glossary(new_glossary)
        return True
    
    return False


def apply_glossary(text: str, source_lang: str, target_lang: str) -> Tuple[str, List[Dict]]:
    """
    应用术语表到源文本，返回替换后的文本和匹配的术语列表

    Args:
        text: 源文本
        source_lang: 源语言
        target_lang: 目标语言

    Returns:
        Tuple[str, List[Dict]: (替换后的文本, 匹配的术语列表)
    """
    glossary = get_glossary_list(source_lang, target_lang)
    
    if not glossary:
        return text, []
    
    # 按优先级排序（高优先级先处理）
    glossary.sort(key=lambda g: g.get('priority', 0), reverse=True)
    
    matched_terms = []
    result_text = text
    
    for term in glossary:
        source_term = term['source_term']
        case_sensitive = term.get('case_sensitive', False)
        
        # 构建正则表达式模式
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(r'\b' + re.escape(source_term) + r'\b', flags)
        
        # 检查是否匹配
        matches = pattern.findall(result_text)
        if matches:
            matched_terms.append(term)
            # 替换（保留原文的大小写风格）
            result_text = pattern.sub(term['target_term'], result_text)
    
    return result_text, matched_terms


def apply_glossary_to_translation(text: str, source_lang: str, target_lang: str) -> Tuple[str, List[Dict]]:
    """
    在翻译前预处理文本，标记需要特殊翻译的术语
    返回处理后的文本和术语映射，用于翻译后还原

    Args:
        text: 源文本
        source_lang: 源语言
        target_lang: 目标语言

    Returns:
        Tuple[str, Dict]: (处理后的文本, 术语映射字典)
    """
    glossary = get_glossary_list(source_lang, target_lang)
    
    if not glossary:
        return text, {}
    
    # 按优先级排序
    glossary.sort(key=lambda g: g.get('priority', 0), reverse=True)
    
    term_mapping = {}
    result_text = text
    placeholder_index = 0
    
    for term in glossary:
        source_term = term['source_term']
        case_sensitive = term.get('case_sensitive', False)
        
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(r'\b' + re.escape(source_term) + r'\b', flags)
        
        matches = pattern.findall(result_text)
        if matches:
            # 使用占位符替换，避免被翻译
            placeholder = f"__GLOSSARY_{placeholder_index}__"
            term_mapping[placeholder] = term['target_term']
            placeholder_index += 1
            
            # 替换为占位符
            result_text = pattern.sub(placeholder, result_text)
    
    return result_text, term_mapping


def restore_glossary_terms(text: str, term_mapping: Dict) -> str:
    """
    在翻译后还原术语

    Args:
        text: 翻译后的文本
        term_mapping: 术语映射字典

    Returns:
        str: 还原后的文本
    """
    result = text
    for placeholder, target_term in term_mapping.items():
        result = result.replace(placeholder, target_term)
    return result


def _generate_id() -> str:
    """生成唯一ID"""
    import uuid
    return str(uuid.uuid4())[:8]


def _get_timestamp() -> str:
    """获取时间戳"""
    from datetime import datetime
    return datetime.now().isoformat()


def import_glossary(terms: List[Dict]) -> int:
    """
    批量导入术语

    Args:
        terms: 术语列表

    Returns:
        int: 成功导入的数量
    """
    count = 0
    for term in terms:
        try:
            add_glossary_term(
                source_term=term.get('source_term'),
                target_term=term.get('target_term'),
                source_lang=term.get('source_lang'),
                target_lang=term.get('target_lang'),
                description=term.get('description', ''),
                case_sensitive=term.get('case_sensitive', False),
                priority=term.get('priority', 0)
            )
            count += 1
        except Exception:
            pass
    return count


def export_glossary(source_lang: str = None, target_lang: str = None) -> List[Dict]:
    """
    导出术语表

    Args:
        source_lang: 源语言过滤（可选）
        target_lang: 目标语言过滤（可选）

    Returns:
        List[Dict]: 术语列表
    """
    return get_glossary_list(source_lang, target_lang)