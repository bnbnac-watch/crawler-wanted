import os
from watch_contract import BaseCrawler, Item, CrawlerException

_SEARCH_URL = "https://www.wanted.co.kr/search?query={keyword}&tab=position"

# 아래 셀렉터는 실제 페이지 구조 확인 후 수정 필요
_JOB_SELECTOR = "li.JobCard_container__REty6"
_TITLE_SELECTOR = "strong.JobCard_title__HBpZf"
_COMPANY_SELECTOR = "span.JobCard_companyName__vZMqJ"
_TAGS_SELECTOR = "span.JobCard_skillLabel__yDFBt"


class WantedCrawler(BaseCrawler):
    def __init__(self):
        self._keyword = os.getenv("SEARCH_KEYWORD", "SLAM")

    async def crawl(self, page) -> list[Item]:
        url = _SEARCH_URL.format(keyword=self._keyword)
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector(_JOB_SELECTOR, timeout=10000)

            jobs = await page.query_selector_all(_JOB_SELECTOR)
            items = []
            for job in jobs:
                try:
                    title_el = await job.query_selector(_TITLE_SELECTOR)
                    if not title_el:
                        continue
                    title = (await title_el.inner_text()).strip()

                    # 원티드는 카드 자체가 링크
                    href = await job.get_attribute("href")
                    if not href:
                        a_el = await job.query_selector("a")
                        href = await a_el.get_attribute("href") if a_el else None
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"https://www.wanted.co.kr{href}"

                    company_el = await job.query_selector(_COMPANY_SELECTOR)
                    company = (await company_el.inner_text()).strip() if company_el else ""

                    tag_els = await job.query_selector_all(_TAGS_SELECTOR)
                    tags = [await el.inner_text() for el in tag_els]

                    items.append(Item(
                        id=href,
                        title=title,
                        url=href,
                        data={"company": company, "tags": tags},
                    ))
                except Exception:
                    continue

            return items
        except Exception as e:
            raise CrawlerException(str(e)) from e
