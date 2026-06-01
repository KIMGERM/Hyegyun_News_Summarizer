import os
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from deep_translator import GoogleTranslator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def translate_text(text, target_lang='ko'):
    try:
        if not text: return ""
        if len(text) > 1500: text = text[:1500]
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception:
        return text

def crawl_realtime_google_market_news():
    # [인증/방화벽 무력화] 구글 뉴스의 글로벌 비즈니스/테크 실시간 RSS 피드를 타겟팅합니다.
    rss_url = "https://news.google.com/rss/search?q=Nvidia+OR+Semiconductor+OR+Fed+OR+AI&hl=en-US&gl=US&ceid=US:en"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print("▶ [1단계] 구글 실시간 금융·테크 RSS 피드 다이렉트 수집 시작...")
        response = requests.get(rss_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'xml') # RSS 규격 파싱
        
        items = soup.find_all('item')[:5] # 정확하게 실시간 최신 뉴스 5개 추출
        
        if not items:
            print("⚠️ 최신 기사를 찾지 못했습니다.")
            return []
            
        analyzed_dataset = []
        print(f"▶ [2단계] 총 {len(items)}개 실시간 마켓 기사 한글화 및 투자 정보 도출 진입...")
        
        for idx, item in enumerate(items):
            raw_title = item.title.text if item.title else "Realtime Market Update"
            article_url = item.link.text if item.link else "https://news.google.com"
            description = item.description.text if item.description else ""
            
            # 언론사 이름 제거 깔끔한 타이틀 정제
            if " - " in raw_title:
                article_title = raw_title.split(" - ")[0]
            else:
                article_title = raw_title

            # 투자 섹터 카테고리 자동 분류
            cat = 'ai'
            title_lower = article_title.lower()
            if any(k in title_lower for k in ['nvidia', 'chip', 'semiconductor', 'tsmc', 'intel', 'hbm', 'samsung', 'hynix']):
                cat = 'semiconductor'
            elif any(k in title_lower for k in ['cloud', 'server', 'datacenter', 'amazon', 'microsoft', 'google']):
                cat = 'datacenter'
            elif any(k in title_lower for k in ['fed', 'rate', 'inflation', 'macro', 'powell', 'stocks']):
                cat = 'computing' # 거시 시황용

            # 실시간 뉴스 한글 번역 및 3줄 요약문 구축
            ko_title = translate_text(article_title)
            ko_desc = translate_text(BeautifulSoup(description, 'html.parser').get_text()) if description else "실시간 마켓 피드 수집 완료."
            
            p1 = f"구글 뉴스 파이프라인을 통해 실시간 수집된 글로벌 외신 헤드라인입니다."
            p2 = f"원문 이슈: {ko_desc}"
            p3 = f"해당 매크로 동향이 국내 증시 섹터 및 핵심 종목들의 수급에 직간접적인 영향을 미칠 가능성이 포착되었습니다."

            news_data = {
                "title": ko_title,
                "url": article_url,
                "summary": [p1, p2, p3],
                "keywords": [cat.upper(), "MARKET", "LIVE"],
                "opportunity": f"글로벌 시장의 {ko_title} 모멘텀에 대응하여 국내 관련 대장주 및 밸류체인 수혜주의 선제적 포트폴리오 편입 기회.",
                "risk": "미국 거시경제 매크로 지표의 변동성 릴리즈 및 단기 오버슈팅에 따른 차익실현 매물 출회 리스크 상존."
            }
            analyzed_dataset.append(news_data)
            print(f"✅ [{idx+1}/5] 실시간 마켓 뉴스 연동 완료: {article_title}")
            
        return analyzed_dataset

    except Exception as e:
        print(f"⚠️ 시스템 오류: {e}")
        return []

@app.get("/api/latest-tech-news")
async def get_latest_news_dashboard():
    return crawl_realtime_google_market_news()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)