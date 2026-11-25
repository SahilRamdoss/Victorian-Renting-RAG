from bs4 import Tag
from bs4 import BeautifulSoup
from datetime import datetime
import requests

ALLOWED_TAGS = {
     # Paragraph and headings
     "p",
     "h1",
     "h2",
     "h3",
     "h4",
     "h5",
     "h6",
     # Miscelanneous tags
     "div",
     "section",
     "main",
     "summary",
     "article",
     "body",
     # Table tags
     "table",
     "thead",
     "tbody",
     "tr",
     "th",
     "td",
     # List elements
     "ul",
     "ol",
     "li",
     "a"
}

NOISE_TAGS = [
    "script",
    "style", 
    "nav", 
    "footer", 
    "header"
]

DIRECT_TEXT_EXTRATION = {
     "p",
     "h1",
     "h2",
     "h3",
     "h4",
     "h5",
     "h6",
     "li",
     "th",
     "td",
}

class WebContentParser:

    def __init__(self):
        pass

    def _extract_content_aux(self, element):

        el_children = []

        if not element.find(True, recursive=False):
            return {
                "title": element.name,
                "content": element.contents
            }
        else:
            self._iterate_children(element, el_children)

            return {
                "node": element.name,
                "children": el_children
            }
        

    def _iterate_children(self, parent, children_list):
                for child in parent.children:
                    if isinstance(child, Tag) and (parent.name in ALLOWED_TAGS):
                        if parent.name in DIRECT_TEXT_EXTRATION:
                                children_list.append(parent.get_text(separator=" ", strip=True))
                                break
                        else:
                                if child.name in ALLOWED_TAGS:
                                    children_list.append(self._extract_content_aux(child))



    def extract_body_content(self, url: str|None = None, file_path: str|None = None):

        if url != None and file_path != None:
             raise Exception("Web_Content_Parser: Cannot provide both url and file path at the same time.")

        if url == None and file_path == None:
             raise Exception("Web_Content_Parser: Must provide either url of web page or file path for HTML content of web page.")

        soup = BeautifulSoup("", "html.parser")

        if url:
             response = requests.get(url)
             soup = BeautifulSoup(response.text, "html.parser")
        elif file_path:
             with open(file_path, "r") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
        else:
             raise Exception("Web_Content_Parser: Input is neither url nor file path!")

        for element in soup(NOISE_TAGS):
            element.decompose()

        title = soup.find_all("title")[0].decode_contents().strip()
        main = soup.find_all(["main"])[0]
        main_children = []

        self._iterate_children(main, main_children)

        return {
            "title": title,
            "last_fetched": datetime.now().isoformat(sep=" "),
            "node": main.name,
            "children": main_children
        }