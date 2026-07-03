import logging

from bs4 import BeautifulSoup
from watch_contract import RenderCrawler, Item, CrawlerException

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://www.wanted.co.kr/search?query={keyword}&tab=position"

# 아래 셀렉터는 실제 페이지 구조 확인 후 수정 필요
_JOB_SELECTOR = "li.JobCard_container__REty6"
_TITLE_SELECTOR = "strong.JobCard_title__HBpZf"
_COMPANY_SELECTOR = "span.JobCard_companyName__vZMqJ"
_TAGS_SELECTOR = "span.JobCard_skillLabel__yDFBt"


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
                    title_el = job.select_one(_TITLE_SELECTOR)
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)

                    # 원티드는 카드 자체가 링크
                    href = job.get("href")
                    if not href:
                        a_el = job.select_one("a")
                        href = a_el.get("href") if a_el else None
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"https://www.wanted.co.kr{href}"

                    company_el = job.select_one(_COMPANY_SELECTOR)
                    company = company_el.get_text(strip=True) if company_el else ""

                    tags = [el.get_text(strip=True) for el in job.select(_TAGS_SELECTOR)]

                    items.append(Item(
                        id=href,
                        title=title,
                        url=href,
                        data={"company": company, "tags": tags},
                    ))
                except Exception:
                    continue

            logger.info("파싱 완료: %d개", len(items))
            return items
        except Exception as e:
            logger.error("parse 예외: %s", e)
            raise CrawlerException(str(e)) from e
