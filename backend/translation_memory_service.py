"""
翻译记忆库服务模块

自动保存翻译历史记录，支持快速检索和复用
"""

import os
import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime


MEMORY_DIR = '/tmp/translation_memory'
MEMORY_FILE = os.path.join(MEMORY_DIR, 'memory.json')


def _ensure_memory_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def _load_memory() -> List[Dict]:
    _ensure_memory_dir()
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_memory(memory: List[Dict]):
    _ensure_memory_dir()
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def add_memory_entry(
    source_text: str,
    target_text: str,
    source_lang: str,
    target_lang: str,
    confidence: float = 1.0,
    glossary_matches: List[Dict] = None
) -> Dict:
    memory = _load_memory()
    
    entry = {
        'id': _generate_id(),
        'source_text': source_text,
        'target_text': target_text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'confidence': confidence,
        'glossary_matches': glossary_matches or [],
        'created_at': _get_timestamp(),
        'used_count': 0,
        'last_used_at': None
    }
    
    memory.insert(0, entry)
    
    if len(memory) > 1000:
        memory = memory[:1000]
    
    _save_memory(memory)
    return entry


def get_memory_list(
    source_lang: str = None,
    target_lang: str = None,
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[Dict], int]:
    memory = _load_memory()
    
    if source_lang:
        memory = [m for m in memory if m.get('source_lang') == source_lang]
    if target_lang:
        memory = [m for m in memory if m.get('target_lang') == target_lang]
    
    total = len(memory)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = memory[start:end]
    
    return paginated, total


def search_memory(
    query: str,
    source_lang: str = None,
    target_lang: str = None,
    max_results: int = 10
) -> List[Dict]:
    memory = _load_memory()
    
    if source_lang:
        memory = [m for m in memory if m.get('source_lang') == source_lang]
    if target_lang:
        memory = [m for m in memory if m.get('target_lang') == target_lang]
    
    query_lower = query.lower().strip()
    results = []
    
    for entry in memory:
        source_lower = entry['source_text'].lower()
        target_lower = entry['target_text'].lower()
        
        if query_lower in source_lower or query_lower in target_lower:
            score = _calculate_match_score(query_lower, source_lower, target_lower)
            results.append({**entry, 'match_score': score})
    
    results.sort(key=lambda r: r['match_score'], reverse=True)
    return results[:max_results]


def _calculate_match_score(query: str, source: str, target: str) -> float:
    source_score = len(query) / len(source) if source else 0
    target_score = len(query) / len(target) if target else 0
    return max(source_score, target_score) * 0.5 + (1 if query in source or query in target else 0) * 0.5


def get_memory_entry(entry_id: str) -> Optional[Dict]:
    memory = _load_memory()
    for entry in memory:
        if entry['id'] == entry_id:
            return entry
    return None


def update_memory_entry(
    entry_id: str,
    target_text: str = None,
    confidence: float = None
) -> Optional[Dict]:
    memory = _load_memory()
    
    for entry in memory:
        if entry['id'] == entry_id:
            if target_text is not None:
                entry['target_text'] = target_text
            if confidence is not None:
                entry['confidence'] = confidence
            entry['updated_at'] = _get_timestamp()
            _save_memory(memory)
            return entry
    
    return None


def delete_memory_entry(entry_id: str) -> bool:
    memory = _load_memory()
    new_memory = [m for m in memory if m['id'] != entry_id]
    
    if len(new_memory) < len(memory):
        _save_memory(new_memory)
        return True
    
    return False


def increment_usage(entry_id: str):
    memory = _load_memory()
    
    for entry in memory:
        if entry['id'] == entry_id:
            entry['used_count'] = entry.get('used_count', 0) + 1
            entry['last_used_at'] = _get_timestamp()
            _save_memory(memory)
            break


def get_similar_translation(
    source_text: str,
    source_lang: str,
    target_lang: str,
    min_confidence: float = 0.7
) -> Optional[Dict]:
    memory = _load_memory()
    
    filtered = [
        m for m in memory
        if m.get('source_lang') == source_lang
        and m.get('target_lang') == target_lang
    ]
    
    best_match = None
    best_score = 0
    
    for entry in filtered:
        score = _calculate_similarity(source_text, entry['source_text'])
        if score > best_score and score >= min_confidence:
            best_score = score
            best_match = {**entry, 'similarity_score': score}
    
    return best_match


def _calculate_similarity(text1: str, text2: str) -> float:
    text1_clean = re.sub(r'[^\w\s]', '', text1.lower())
    text2_clean = re.sub(r'[^\w\s]', '', text2.lower())
    
    words1 = set(text1_clean.split())
    words2 = set(text2_clean.split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    jaccard = len(intersection) / len(union)
    
    length_diff = abs(len(text1) - len(text2)) / max(len(text1), len(text2))
    length_score = 1 - length_diff * 0.3
    
    return jaccard * 0.7 + length_score * 0.3


def _generate_id() -> str:
    import uuid
    return str(uuid.uuid4())[:8]


def _get_timestamp() -> str:
    return datetime.now().isoformat()


def export_memory(source_lang: str = None, target_lang: str = None) -> List[Dict]:
    memory = _load_memory()
    
    if source_lang:
        memory = [m for m in memory if m.get('source_lang') == source_lang]
    if target_lang:
        memory = [m for m in memory if m.get('target_lang') == target_lang]
    
    return memory


def import_memory(entries: List[Dict]) -> int:
    memory = _load_memory()
    count = 0
    
    for entry in entries:
        try:
            new_entry = {
                'id': entry.get('id') or _generate_id(),
                'source_text': entry['source_text'],
                'target_text': entry['target_text'],
                'source_lang': entry['source_lang'],
                'target_lang': entry['target_lang'],
                'confidence': entry.get('confidence', 1.0),
                'glossary_matches': entry.get('glossary_matches', []),
                'created_at': entry.get('created_at', _get_timestamp()),
                'used_count': entry.get('used_count', 0),
                'last_used_at': entry.get('last_used_at')
            }
            memory.insert(0, new_entry)
            count += 1
        except Exception:
            pass
    
    if len(memory) > 1000:
        memory = memory[:1000]
    
    _save_memory(memory)
    return count


def clear_memory() -> int:
    memory = _load_memory()
    count = len(memory)
    _save_memory([])
    return count
