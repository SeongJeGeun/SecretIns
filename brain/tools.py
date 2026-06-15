import os
import sys
import requests
from bs4 import BeautifulSoup

# RAG 엔진 임포트 제거 (안티그래비티 2.0 내장 툴 활용)
BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BRAIN_DIR)

class ScraperTool:
    """기사 URL에서 본문 내용을 크롤링하여 텍스트를 추출하는 도구"""
    @staticmethod
    def scrape(url):
        print(f"  [Tool] URL 스크래핑 시도: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                return f"URL 접속 실패 (Status Code: {r.status_code})"
                
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 불필요한 태그 제거 (스크립트, 스타일, 헤더, 푸터 등)
            for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe']):
                s.decompose()
                
            # 본문일 확률이 높은 구획 찾기 (article, main, 혹은 class명에 content가 들어간 div)
            body_element = soup.find('article') or soup.find('main')
            if not body_element:
                # content나 article이 포함된 div 탐색
                body_element = soup.find('div', class_=lambda c: c and ('content' in c or 'article' in c))
                
            # 없으면 전체 body에서 추출
            if not body_element:
                body_element = soup.body
                
            if not body_element:
                return "본문 콘텐츠를 찾을 수 없습니다."
                
            # 문장별 줄바꿈을 주며 텍스트 추출
            text = body_element.get_text(separator='\n')
            
            # 연속된 빈 줄 및 공백 제거, 불필요한 저작권/광고/기자 메일 라인 제거
            cleaned_lines = []
            stopwords_patterns = [
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # 이메일 주소만 있는 라인
                r"^[cC]opyright",                                    # Copyright 라인
                r"무단.*전재.*재배포.*금지",                           # 저작권 경고 라인
                r"▶.*구독하기",                                       # 구독 유도 라인
                r"^[gG]oogle.*[aA]nalytics",
                r"^[fF]acebook.*[sS]hare"
            ]
            import re
            for line in text.split('\n'):
                line_strip = line.strip()
                if not line_strip:
                    continue
                # 불용어 패턴 매칭 검사
                skip = False
                for pattern in stopwords_patterns:
                    if re.search(pattern, line_strip, re.IGNORECASE):
                        skip = True
                        break
                if not skip:
                    cleaned_lines.append(line_strip)
                    
            cleaned_text = '\n'.join(cleaned_lines)
            
            # 너무 길면 4000자에서 잘라 전달
            return cleaned_text[:4000]
            
        except Exception as e:
            return f"URL 스크래핑 중 에러 발생: {e}"



class DuckDuckGoSearchTool:
    """DuckDuckGo 무료 API를 사용하여 관련 웹 검색을 수행하는 도구"""
    @staticmethod
    def search(query):
        print(f"  [Tool] 웹 검색 쿼리: {query}")
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                if not results:
                    return "검색 결과가 없습니다."
                
                formatted = []
                for idx, r in enumerate(results):
                    formatted.append(
                        f"[{idx+1}] {r.get('title')}\n"
                        f"링크: {r.get('href')}\n"
                        f"내용: {r.get('body')}\n"
                    )
                return "\n".join(formatted)
        except ImportError:
            return "duckduckgo_search 패키지가 설치되지 않았습니다."
        except Exception as e:
            return f"웹 검색 중 오류 발생: {e}"
