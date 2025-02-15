# SEO_analyses/head_parser.py
import urllib.request
from bs4 import BeautifulSoup

def parse_head(html_content: str) -> str:
    """
    Извлекает содержимое тега <head> из переданного HTML-контента.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    head_tag = soup.find("head")
    return head_tag.prettify() if head_tag else ""

def fetch_and_parse_head(url: str) -> str:
    """
    Загружает страницу по указанному URL и возвращает содержимое тега <head>.
    """
    with urllib.request.urlopen(url) as response:
        html_content = response.read()
    return parse_head(html_content)
