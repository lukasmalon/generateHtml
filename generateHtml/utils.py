import re
import importlib
from typing import Type, Any


def prepend_dash_before_uppercase(input_str: str) -> str:
    return re.sub(r"([A-Z])", r"-\1", input_str)


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace(">", "&gt;")
        .replace("<", "&lt;")
        .replace("'", "&#39;")
        .replace('"', "&#34;")
    )


def unescape_html(text: str) -> str:
    return (
        text.replace("&#34;", '"')
        .replace("&#39;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
    )


def get_class_from_string(module_name: str, class_name: str) -> Type[Any]:
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_
