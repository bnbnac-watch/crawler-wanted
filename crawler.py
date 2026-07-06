import logging

from bs4 import BeautifulSoup
from watch_contract import RenderCrawler, Item, CrawlerException

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://www.wanted.co.kr/search?query={keyword}&tab=position"

# CSS Module 클래스명은 프론트 배포마다 해시가 바뀌므로 안정적인 data-* 속성으로 선택
_JOB_SELECTOR = "a[data-position-id]"


class WantedCrawler(RenderCrawler):
    def render_request(self, params: dict) -> dict:
        keyword = params.get("keyword", "SLAM")
        return {
            "url": _SEARCH_URL.format(keyword=keyword),
            "wait_for": _JOB_SELECTOR,
        }

    def parse(self, html: str, params: dict) -> list[Item]:
        try:
            soup = BeautifulSoup(html, "html.parser")
            items = []
            for job in soup.select(_JOB_SELECTOR):
                try:
                    title = job.get("data-position-name")
                    if not title:
                        continue

                    href = job.get("href")
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"https://www.wanted.co.kr{href}"

                    company = job.get("data-company-name", "")

                    items.append(Item(
                        id=href,
                        title=title,
                        url=href,
                        data={"company": company},
                    ))
                except Exception:
                    continue

            logger.info("파싱 완료: %d개", len(items))
            return items
        except Exception as e:
            logger.error("parse 예외: %s", e)
            raise CrawlerException(str(e)) from e
