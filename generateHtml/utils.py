import re
import importlib
from collections import Counter

def check_max_occurences(item_list: list, max_occurences: int=1) -> tuple[object, int] | None:
    count = Counter(type(item) for item in item_list)
    max_occured = count.most_common(1)
    max_occured = max_occured[0] if max_occured else None
    return  max_occured if max_occured and max_occured[1] > max_occurences else None

def prepend_dash_before_uppercase(input_str: str) -> str:
    return re.sub(r'([A-Z])', r'-\1', input_str)

def escape_html(text:str):
    return text.replace('&', '&amp;')\
                .replace('>', '&gt;')\
                .replace('<', '&lt;')\
                .replace('\'','&#39;')\
                .replace('"','&#34;')

def get_class_from_string(module_name: str, class_name: str) -> callable:
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_
