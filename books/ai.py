import json
import os

import requests
from openai import OpenAI

WIKI_API = 'https://ko.wikipedia.org/w/api.php'
WIKI_HEADERS = {'User-Agent': 'ThReadStudyProject/1.0 (student project)'}


def get_client():
    return OpenAI(
        api_key=os.getenv('GMS_KEY'),
        base_url=os.getenv('GMS_BASE_URL'),
        timeout=60,
    )

AUTHOR_KEYWORDS = ('작가', '소설가', '시인', '저술가', '극작가', '수필가',
                   '평론가', '작사가', '저자', '학자', '교수', '목사', '사상가', '번역가')


def search_wikipedia(name):
    """'이름 작가'로 검색해서, 첫 문장이 사람(작가)을 설명하는 문서만 고른다. 없으면 None."""
    params = {
        'action': 'query', 'format': 'json', 'redirects': 1,
        'generator': 'search', 'gsrsearch': f'{name} 작가', 'gsrlimit': 5,
        'prop': 'extracts|pageimages', 'exintro': 1, 'explaintext': 1, 'exlimit': 'max',
        'piprop': 'thumbnail', 'pithumbsize': 300,
    }
    try:
        res = requests.get(WIKI_API, params=params, headers=WIKI_HEADERS, timeout=5)
        res.raise_for_status()
        pages = res.json().get('query', {}).get('pages', {})
    except (requests.RequestException, ValueError):
        return None

    # 검색 순위 순으로 정렬
    for page in sorted(pages.values(), key=lambda p: p.get('index', 99)):
        extract = page.get('extract', '')
        # 문서 첫머리에 작가 관련 단어가 있고, 문서 제목에 이름이 들어 있어야 통과
        if name in page.get('title', '') and any(k in extract[:150] for k in AUTHOR_KEYWORDS):
            return {
                'title': page.get('title', ''),
                'extract': extract[:1500],
                'image': page.get('thumbnail', {}).get('source', ''),
            }
    return None


def parse_json(text):
    """응답에서 JSON 부분만 꺼내 파싱한다. 실패하면 예외가 난다."""
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError('JSON을 찾을 수 없습니다.')
    return json.loads(text[start:end + 1])


def ask_gpt(book, wiki):
    if wiki and wiki['extract']:
        wiki_text = f"[위키피디아 문서: {wiki['title']}]\n{wiki['extract']}"
    else:
        wiki_text = '위키피디아 검색 결과 없음'

    prompt = f"""너는 도서 정보 도우미야. 아래 도서 정보와 위키피디아 검색 결과를 바탕으로 작가 정보를 알려줘.

[도서 정보]
- 제목: {book.title}
- 저자: {book.author}
- 설명: {book.description}

{wiki_text}

규칙:
- 위키피디아 결과가 이 저자와 무관해 보이면 무시해.
- 확실하지 않은 내용은 지어내지 말고, 모르면 author_info에 "정보를 찾을 수 없습니다."라고 써.
- 반드시 아래 JSON 형식으로만 답하고, 다른 말은 쓰지 마.

{{"author_info": "작가 소개 3~5문장(한국어)", "author_works": ["대표작1", "대표작2", "대표작3"]}}
"""
    response = get_client().chat.completions.create(
        model='gpt-5-nano',
        messages=[{'role': 'user', 'content': prompt}],
    )
    return parse_json(response.choices[0].message.content)


def fill_author_info(book):
    """작가 정보를 생성해 book에 저장한다. 어떤 오류가 나도 예외를 밖으로 내보내지 않는다."""
    try:
        wiki = search_wikipedia(book.author)
        data = ask_gpt(book, wiki)

        works = data.get('author_works', [])
        if not isinstance(works, list):
            works = []

        book.author_info = str(data.get('author_info', '')).strip()
        book.author_works = [str(w) for w in works][:5]
        book.author_image = wiki['image'] if wiki else ''
        book.save(update_fields=['author_info', 'author_works', 'author_image'])
        return True
    except Exception as e:
        print(f'[AI 작가 정보 생성 실패] {e}')
        return False