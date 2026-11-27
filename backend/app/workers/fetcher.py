## The fetcher makes requests based on the instructions from the official https://www.consumer.vic.gov.au/robots.txt file

import requests
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from datetime import date
import xml.etree.ElementTree as ET
from time import sleep

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ingestion")
MELBOURNE = ZoneInfo("Australia/Melbourne")


SITEMAP_URL = "https://www.consumer.vic.gov.au/sitemap.xml"
RENTING_PREFIX = "https://www.consumer.vic.gov.au/housing/renting"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
HEADERS = {"User-Agent": "VicRentingRAG/0.1 (personal research project)"}
CRAWL_DELAY = 5

def get_rental_pages() -> dict[str, date | None]:
    response = requests.get(SITEMAP_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    pages: dict[str, date | None] = {}

    for url_el in root.findall("sm:url", NS):
        loc = (url_el.findtext("sm:loc", default="", namespaces=NS) or "").strip()
        if loc == RENTING_PREFIX or loc.startswith(RENTING_PREFIX + "/"):
            lastmod = url_el.findtext("sm:lastmod", namespaces=NS)
            pages[loc] = date.fromisoformat(lastmod.strip()) if lastmod else None

    return pages

def populate_tables(html_pages):
    pass


def run_ingestion():
    renting_page_urls = get_rental_pages()
    html_pages = []

    for url in renting_page_urls:
        response = requests.get(url)

        html = response.content.decode("utf-8")
        html_pages.append((url, html))

        # Sleep for 5 seconds based on robots.txt file
        sleep(CRAWL_DELAY)

    populate_tables(html_pages)
    


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=MELBOURNE)
    scheduler.add_job(
        run_ingestion,
        CronTrigger(day_of_week="sun", hour=3, minute=0),
        next_run_time=datetime.now(MELBOURNE),
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()