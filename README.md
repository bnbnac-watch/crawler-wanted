# crawler-wanted

원티드 채용공고 검색 결과 크롤러. `RenderCrawler` 구현 — 원티드 검색 페이지는 클라이언트사이드 렌더링(SPA)이라 `watch-playwright`로 JS를 실행한 뒤에야 결과가 DOM에 나타난다.

## API

### POST /crawl

```json
{"keyword": "SLAM"}
```

`keyword` 없으면 기본값 `"SLAM"`. `https://www.wanted.co.kr/search?query={keyword}&tab=position`을 `a[data-position-id]` 셀렉터가 나타날 때까지 대기(`wait_for`)한 뒤 렌더 결과를 파싱한다.

응답: `Item[]` — `data`에 `company` 포함

### GET /health

`{"status": "ok"}`

## 파싱 셀렉터

CSS Module 클래스명은 프론트 배포마다 해시가 바뀌므로 클래스 선택자 대신 안정적인 `data-*` 속성(`data-position-id`, `data-position-name`, `data-company-name`)으로 선택한다.

## id (중복 감지 키)

```python
position_id = job.get("data-position-id")
items.append(Item(id=position_id or href, ...))
```

href 대신 원티드가 공고 식별용으로 직접 부여하는 `data-position-id`를 `id`로 쓴다 — href의 쿼리스트링이 검색 세션마다 바뀔 가능성에 대비한 선택(사람인의 `search_uuid` 문제와 같은 유형의 리스크에 대한 예방적 조치이며, 실제 wanted에서 href가 불안정한 사례가 직접 관측된 것은 아니다). 추출 실패 시 href로 폴백.

## 환경변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `WATCH_PLAYWRIGHT_URL` | `http://watch-playwright:8080` | |

## 포트

| 포트 | 용도 |
|---|---|
| 8080 | aiohttp — 컴포즈 내부에서만 노출 |
