from bs4 import Tag
from bs4 import BeautifulSoup

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
     "li"
}

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



    def extract_body_content(self, soup: BeautifulSoup):
        main = soup.find_all(["main"])[0]
        main_children = []

        self._iterate_children(main, main_children)

        return {
            "node": main.name,
            "children": main_children
        }