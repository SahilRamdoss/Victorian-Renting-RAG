from langchain_text_splitters import HTMLSemanticPreservingSplitter
from langchain_core.documents import Document
from bs4 import BeautifulSoup
import re


HEADINGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
INLINE_TAGS = ["a", "span", "strong", "b", "em", "i", "u", "abbr"]
EXCLUDED_HEADINGS = {"share this page"}
HEADER_KEY = re.compile(r"^h[1-6]$")
HEADERS_TO_SPLIT_ON = [("h1", "h1"), ("h2", "h2"), ("h3", "h3"), ("h4", "h4"), ("h5", "h5"), ("h6", "h6")]


class Ingester:

    def __init__(self):
        # Using it as an instance variable rather than a class variable because of concerns over parallel processing
        self.html_semantic_splitter = HTMLSemanticPreservingSplitter(
            headers_to_split_on=HEADERS_TO_SPLIT_ON,
            max_chunk_size=1500,
            chunk_overlap=0,
            separators=["\n\n", "\n", ".", " "],
            elements_to_preserve=["table", "ul", "ol"],
            preserve_links=False,
        )

    def create_chunks(self,html: str, url:str):
        # Extract tables separately
        table_docs, soup = self.__extract_table_docs(html, url)
        # Get the page title
        title = soup.find_all("title")[0].get_text().strip()
        # Set the origin url of the html
        self.html_semantic_splitter._external_metadata = {"title": title, "url": url}
        # Convert all embedded links to normal text
        soup = self.__strip_links(soup)
        # Create the chunks
        semantic_chunks = self.html_semantic_splitter.split_text(str(soup))
        # Remove noisy chunks
        cleaned_semantic_chunks = self.__clean_chunks(semantic_chunks)
        # Add header hierarchy of each chunk as a prefix to its page_content
        self.__post_process_header_tags(cleaned_semantic_chunks)
        # Add the extracted table chunks
        cleaned_semantic_chunks.extend(table_docs)

        return cleaned_semantic_chunks


    def __clean(self, text):
        return " ".join(text.replace("\xa0", " ").split())


    def __cell_text(self, cell):
        for tag in cell.find_all(INLINE_TAGS):
            tag.unwrap()
        cell.smooth()
        return self.__clean(cell.get_text(" ", strip=True))


    def __heading_hierarchy(self, table):
        hierarchy = {}
        current_level = 7
        for h in table.find_all_previous(HEADINGS):
            level = int(h.name[1])
            if level < current_level:
                hierarchy[f"h{level}"] = self.__clean(h.get_text(" ", strip=True))
                current_level = level
                if level == 1:
                    break
        return dict(sorted(hierarchy.items()))


    def __table_to_docs(self, table, url):
        hierarchy = self.__heading_hierarchy(table)

        hierarchy = {
            level: text
            for level, text in hierarchy.items()
            if text.lower() not in EXCLUDED_HEADINGS
        }

        prefix = " - ".join(hierarchy.values())

        metadata_base = {"url": url}
        if hierarchy:
            deepest = list(hierarchy)[-1]
            metadata_base = {deepest: hierarchy[deepest], "url": url}

        rows = table.find_all("tr")
        if not rows:
            return []
        headers = [self.__cell_text(c) for c in rows[0].find_all(["th", "td"])]

        docs = []
        for tr in rows[1:]:
            cells = [self.__cell_text(c) for c in tr.find_all(["td", "th"])]
            if len(cells) != len(headers):
                print(f"Skipping irregular row (colspan/rowspan?): {cells}")
                continue
            body = "; ".join(f"{h}: {v}" for h, v in zip(headers, cells))
            page_content = f"{prefix} - {body}" if prefix else body
            docs.append(Document(page_content=page_content, metadata=dict(metadata_base)))
        return docs


    def __extract_table_docs(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        body = soup.body
        if body is None:
            return [], soup

        tables = [t for t in body.find_all("table") if not t.find_parent("table")]

        docs = []
        for t in tables:
            docs.extend(self.__table_to_docs(t, url))

        for t in tables:
            t.decompose()

        return docs, soup

    def __clean_chunks(self, semantic_chunks):
        new_chunks = []
        header_1_met = False
        share_chunk_met = False
        footer_reached = False

        for i in range(0, len(semantic_chunks)):
            chunk = semantic_chunks[i]
            share_this_page_chunk = False
            if chunk.metadata:
                for key, value in chunk.metadata.items():
                        if not header_1_met and HEADER_KEY.match(key):
                                if key == "h1":
                                    header_1_met = True
                                    break

                        if not share_chunk_met and value == "Sharethis page":
                                share_chunk_met = True
                                new_chunks[-1].page_content = chunk.page_content[20:].strip()
                                share_this_page_chunk = True
                                break

                        if key == "h3" and value == "About us":
                            footer_reached = True
                            break

            # If we reached the footer, there is no need to continue
            if footer_reached:
                break

            # Skip the chunk if we have not encountered our first header yet
            if not header_1_met or share_this_page_chunk:
                continue

            # Remove meaningless encodings from the chunk page_content
            chunk.page_content.replace("\xa0", " ")

            # Add the chunk
            new_chunks.append(chunk)

        return new_chunks

    def __post_process_header_tags(self, semantic_chunks):
        # List to contain header texts of h1-h6.
        headers = []
        # Variable to hold current smallest header traversed
        curr_smallest_header_traversed = 0
        for chunk in semantic_chunks:
            if chunk.metadata:
                for key, value in chunk.metadata.items():
                    if HEADER_KEY.match(key):
                        header_index = int(key[-1])

                        # Adjust the header hierarchy for the chunk
                        if header_index == curr_smallest_header_traversed:
                            headers.pop()
                            headers.append((header_index,value))
                        elif header_index > curr_smallest_header_traversed:
                            curr_smallest_header_traversed = header_index
                            headers.append((header_index, value))
                        else:
                            curr_smallest_header_traversed = header_index
                            for i in range(1, len(headers) + 1):
                                if headers[-1][0] >= header_index:
                                    headers.pop()
                                else:
                                    break

                            headers.append((header_index, value))

                        chunk_header = ""

                        # Create the chunk header string
                        for header in headers:
                            chunk_header = chunk_header + header[1] + " - "

                        # Append all ancestor headers to the chunk content
                        chunk.page_content = chunk_header + chunk.page_content

    def __strip_links(self, soup):
        for a in soup.find_all("a"):
            a.unwrap()
        soup.smooth()
        return soup