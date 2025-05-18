from typing import Optional, Dict

class Article:
    def __init__(self, id: Optional[int] = None, title: str = '', language: str = '', content: str = ''):
        self.id = id
        self.title = title
        self.language = language
        self.content = content

class Element:
    def __init__(self, id: Optional[int] = None, article_id: int = 0, type: str = '', path: str = ''):
        self.id = id
        self.article_id = article_id
        self.type = type
        self.path = path


class Fragment:
    def __init__(self, id: Optional[int] = None, article_id: int = 0, element_id: int = 0, content: str = ''):
        self.id = id
        self.article_id = article_id
        self.element_id = element_id
        self.content = content


class PreprocessingResult:
    def __init__(self, id: Optional[int] = None, fragment_id: int = 0, step: str = '', processed_text: str = ''):
        self.id = id
        self.fragment_id = fragment_id
        self.step = step
        self.processed_text = processed_text

class Graph:
    def __init__(self, id: Optional[int] = None, fragment_id: int = 0, name: str = '', type: str = '', graph_data: Dict = None):
        self.id = id
        self.fragment_id = fragment_id
        self.name = name
        self.type = type
        self.graph_data = graph_data or {}