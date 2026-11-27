from sqlalchemy.orm import Session
from app.core.db import Sessionlocal
from datetime import date
from sqlalchemy import select, func
from app.models import Document, Chunk
from bs4 import BeautifulSoup
from app.modules.ingestion import Ingester
from app.core.embedder import embedder


class DB_Worker:

    def __init__(self):
        self.__ingester = Ingester()
        self.__embedder = embedder

    def get_lastmods(self) -> dict[str, date]:
        with Sessionlocal() as db:
            return {url: lastmod for url, lastmod in db.execute(select(Document.url, Document.lastmod))}

    def sync_documents(self, pages: list[tuple[str, str, date]], sitemap_urls: set[str]) -> None:
        if not sitemap_urls:
            raise ValueError("Empty sitemap; refusing to sync")

        with Sessionlocal() as db:
            existing = {doc.url: doc for doc in db.scalars(select(Document))}

            for url, html, lastmod in pages:
                doc = existing.get(url)
                if doc is None:
                    doc = Document(url=url, title=self.__extract_title(html), lastmod=lastmod)
                    db.add(doc)
                else:
                    doc.title = self.__extract_title(html)
                    doc.lastmod = lastmod
                    doc.fetched_last = func.now()
                doc.chunks = self.__build_chunks(html, url)

            for url in existing.keys() - sitemap_urls:
                db.delete(existing[url])

            db.commit()

    def __extract_title(self, html:str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.title.get_text(strip=True) if soup.title else ""

    def __build_chunks(self, html: str, url: str) -> list[Chunk]:
        lc_chunks = self.__ingester.create_chunks(html=html, url=url)
        texts = [c.page_content for c in lc_chunks]
        vectors = self.__embedder.embed_documents(texts)
        return [
            Chunk(content=c.page_content, meta=c.metadata, embedding=v)
            for c, v in zip(lc_chunks, vectors)
        ]