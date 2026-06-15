import os
import re
import json
import threading
import subprocess
import sys
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# 경로 설정
BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BRAIN_DIR)
DAILY_NEWS_DIR = os.path.join(PROJECT_ROOT, "daily_news")
WIKI_DIR = os.path.join(BRAIN_DIR, "wiki")
STATUS_PATH = os.path.join(DAILY_NEWS_DIR, "pipeline_status.json")
DRAFT_PATH = os.path.join(DAILY_NEWS_DIR, "news_data_draft.json")
REPORT_PATH = os.path.join(DAILY_NEWS_DIR, "briefing_report.md")
METRICS_PATH = os.path.join(PROJECT_ROOT, "analytics", "social", "social_metrics.xlsx")

app = FastAPI(title="IT Media OS Dashboard")

class DraftUpdate(BaseModel):
    cards: list

# ────────────────────────────────────────────────────────
# 1. API Endpoints
# ────────────────────────────────────────────────────────

@app.get("/api/status")
def get_status():
    if os.path.exists(STATUS_PATH):
        try:
            with open(STATUS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    # 기본값
    return {
        "status": "IDLE",
        "current_step": "대기 중",
        "progress_percentage": 0,
        "started_at": "-",
        "updated_at": "-"
    }

@app.get("/api/draft")
def get_draft():
    if os.path.exists(DRAFT_PATH):
        try:
            with open(DRAFT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"초안 로드 실패: {e}")
    return {"date": datetime.now().strftime("%Y-%m-%d"), "mode": "daily", "cards": []}

@app.post("/api/draft/save")
def save_draft(data: DraftUpdate):
    try:
        # 기존 메타데이터 유지하면서 cards만 갱신
        meta = {"date": datetime.now().strftime("%Y-%m-%d"), "mode": "daily"}
        if os.path.exists(DRAFT_PATH):
            try:
                with open(DRAFT_PATH, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    meta["date"] = old_data.get("date", meta["date"])
                    meta["mode"] = old_data.get("mode", meta["mode"])
                    meta["event_title"] = old_data.get("event_title", "")
            except Exception:
                pass
        
        meta["cards"] = data.cards
        
        with open(DRAFT_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        return {"status": "success", "message": "초안이 성공적으로 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"초안 저장 실패: {e}")

@app.get("/api/report")
def get_report():
    if os.path.exists(REPORT_PATH):
        try:
            with open(REPORT_PATH, "r", encoding="utf-8") as f:
                return {"content": f.read()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"리포트 읽기 실패: {e}")
    return {"content": "# 오늘 자 브리핑 리포트가 생성되지 않았습니다."}

@app.get("/api/wiki")
def get_wiki_graph():
    """brain/wiki 내 마크다운 파일을 파싱하여 D3.js 노드/링크 JSON을 만듭니다."""
    nodes = []
    links = []
    node_set = set()
    
    # 위키 폴더 탐색
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith(".md") and file != "SCHEMA.md":
                node_name = file[:-3] # 확장자 제거
                category = os.path.basename(root)
                if node_name not in node_set:
                    nodes.append({"id": node_name, "group": category})
                    node_set.add(node_name)
                
                # 파일 내용 읽어서 [[wikilink]] 파싱
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # wikilink 추출
                    matches = re.findall(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]", content)
                    for target in matches:
                        target = target.strip()
                        if target:
                            links.append({"source": node_name, "target": target})
                            # 타겟 노드가 노드 리스트에 없는 경우 임시 추가
                            if target not in node_set:
                                nodes.append({"id": target, "group": "unclassified"})
                                node_set.add(target)
                except Exception:
                    pass
                    
    return {"nodes": nodes, "links": links}

@app.get("/api/analytics")
def get_analytics():
    """metrics.csv 또는 social_metrics.xlsx 파일을 파싱하여 조회수 및 저장수 추이를 차트용 JSON으로 가공합니다."""
    csv_path = os.path.join(DAILY_NEWS_DIR, "metrics.csv")
    
    # 1. metrics.csv가 있으면 우선 읽음
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # 결측치 제거
            df = df.dropna(subset=["date", "reach"])
            
            # 날짜별로 reach와 saves 집계 (하루에 여러 기사가 올라가므로 날짜별 sum 처리)
            daily_grouped = df.groupby("date").agg({
                "reach": "sum",
                "saves": "sum"
            }).reset_index()
            
            # 날짜 정렬 (오름차순)
            daily_grouped = daily_grouped.sort_values("date")
            
            # 날짜 포맷 변경 (YYYY-MM-DD -> MM-DD)
            def format_date(d_str):
                try:
                    return datetime.strptime(d_str, "%Y-%m-%d").strftime("%m-%d")
                except Exception:
                    return d_str[-5:]
                    
            labels = daily_grouped["date"].apply(format_date).tolist()
            views = daily_grouped["reach"].tolist()
            saves = daily_grouped["saves"].tolist()
            
            return {
                "labels": labels[-30:],
                "views": views[-30:],
                "saves": saves[-30:]
            }
        except Exception as e:
            print(f"CSV analytics parsing error: {e}")

    # 2. 엑셀 파일 폴백
    if os.path.exists(METRICS_PATH):
        try:
            df = pd.read_excel(METRICS_PATH)
            date_col = None
            views_col = None
            saves_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if "date" in col_lower or "날짜" in col_lower:
                    date_col = col
                elif "view" in col_lower or "조회" in col_lower or "노출" in col_lower or "reach" in col_lower:
                    views_col = col
                elif "save" in col_lower or "저장" in col_lower:
                    saves_col = col
            
            if date_col and views_col:
                df = df.dropna(subset=[date_col, views_col])
                df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%m-%d')
                
                labels = df[date_col].tolist()
                views = df[views_col].tolist()
                saves = df[saves_col].tolist() if saves_col else [0] * len(labels)
                
                return {
                    "labels": labels[-30:],
                    "views": views[-30:],
                    "saves": saves[-30:]
                }
        except Exception as e:
            print(f"Excel analytics parsing error: {e}")
            
    # 3. 데이터 가공 실패 또는 파일 없을 시 가상 샘플 데이터 반환
    return {
        "labels": ["06-03", "06-04", "06-05", "06-06", "06-07", "06-08", "06-09"],
        "views": [1200, 2400, 1900, 4300, 3100, 5200, 7100],
        "saves": [45, 120, 80, 250, 180, 320, 450]
    }


# 로컬 오케스트라 구동부 제거 (안티그래비티 2.0 클라우드 오케스트레이션으로 이관)

# ────────────────────────────────────────────────────────
# 2. Main Dashboard Page (Rich HTML + CSS + JS)
# ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Media OS Local AI Dashboard</title>
  <!-- Google Fonts & Chart.js & D3.js -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    :root {
      --bg-color: #0b0c10;
      --panel-bg: rgba(31, 40, 51, 0.4);
      --panel-border: rgba(102, 252, 241, 0.15);
      --accent-cyan: #66fcf1;
      --accent-cyan-hover: #45c2ba;
      --accent-purple: #bb86fc;
      --text-color: #c5c6c7;
      --text-bright: #ffffff;
      --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-color);
      color: var(--text-color);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      background-image: radial-gradient(circle at 10% 20%, rgba(102, 252, 241, 0.05) 0%, transparent 40%),
                        radial-gradient(circle at 90% 80%, rgba(187, 134, 252, 0.05) 0%, transparent 40%);
    }

    header {
      background: rgba(11, 12, 16, 0.85);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--panel-border);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    header h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 1.5rem;
      color: var(--text-bright);
      font-weight: 800;
      letter-spacing: 1px;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    header h1 span {
      color: var(--accent-cyan);
    }

    .btn-run {
      background: linear-gradient(135deg, var(--accent-cyan), #00b4d8);
      color: #000;
      border: none;
      padding: 0.6rem 1.2rem;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
      font-family: 'Outfit', sans-serif;
      transition: all 0.3s ease;
      box-shadow: 0 0 15px rgba(102, 252, 241, 0.4);
    }

    .btn-run:hover {
      transform: translateY(-2px);
      box-shadow: 0 0 25px rgba(102, 252, 241, 0.8);
    }
    
    .btn-run:disabled {
      background: #444;
      color: #888;
      cursor: not-allowed;
      box-shadow: none;
      transform: none;
    }

    main {
      flex: 1;
      padding: 2rem;
      max-width: 1600px;
      width: 100%;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-gap: 2rem;
    }

    @media (max-width: 1024px) {
      main {
        grid-template-columns: 1fr;
      }
    }

    .glass-card {
      background: var(--panel-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--panel-border);
      border-radius: 16px;
      padding: 1.5rem;
      box-shadow: var(--glass-shadow);
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .span-2 {
      grid-column: span 2;
    }

    @media (max-width: 1024px) {
      .span-2 {
        grid-column: span 1;
      }
    }

    h2 {
      font-family: 'Outfit', sans-serif;
      font-size: 1.25rem;
      color: var(--text-bright);
      border-left: 4px solid var(--accent-cyan);
      padding-left: 0.5rem;
      margin-bottom: 0.5rem;
    }

    /* 파이프라인 진행률 */
    .status-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .progress-bar-bg {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 999px;
      height: 10px;
      width: 100%;
      overflow: hidden;
      position: relative;
    }

    .progress-bar-fill {
      background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
      height: 100%;
      width: 0%;
      transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 0 10px rgba(102, 252, 241, 0.5);
    }

    /* 카드 뉴스 에디터 */
    .cards-container {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      max-height: 500px;
      overflow-y: auto;
      padding-right: 0.5rem;
    }

    .card-item {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
      transition: all 0.3s ease;
    }

    .card-item:hover {
      border-color: rgba(102, 252, 241, 0.3);
      background: rgba(255, 255, 255, 0.05);
    }

    .card-header-inputs {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      grid-gap: 0.5rem;
    }

    input, select, textarea {
      background: rgba(11, 12, 16, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      color: var(--text-bright);
      padding: 0.5rem;
      font-family: inherit;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.3s ease;
    }

    input:focus, select:focus, textarea:focus {
      border-color: var(--accent-cyan);
    }

    textarea {
      resize: vertical;
      min-height: 60px;
    }

    .threads-inputs {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-gap: 0.5rem;
    }

    .btn-save {
      background: var(--accent-purple);
      color: #000;
      border: none;
      padding: 0.6rem 1rem;
      border-radius: 6px;
      font-weight: 700;
      cursor: pointer;
      font-family: 'Outfit', sans-serif;
      transition: all 0.3s ease;
      align-self: flex-end;
    }

    .btn-save:hover {
      box-shadow: 0 0 15px rgba(187, 134, 252, 0.6);
      transform: translateY(-1px);
    }

    /* 위키 네트워크 그래프 */
    #wiki-graph {
      height: 400px;
      width: 100%;
      background: rgba(11, 12, 16, 0.4);
      border-radius: 12px;
      position: relative;
    }

    /* 마크다운 리포트 프리뷰 */
    #report-content {
      white-space: pre-wrap;
      font-size: 0.95rem;
      line-height: 1.6;
      max-height: 400px;
      overflow-y: auto;
      padding: 1rem;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* 스크롤바 커스텀 */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(0,0,0,0.1);
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.1);
      border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--accent-cyan);
    }
  </style>
</head>
<body>

  <header>
    <h1>IT Media OS <span>AI Dashboard</span></h1>
    <div style="font-size: 0.9rem; color: var(--accent-cyan); border: 1px solid var(--accent-cyan); padding: 0.4rem 0.8rem; border-radius: 4px; font-family: 'Outfit', sans-serif;">
      ⚡ 스케줄러: Antigravity 2.0 관리
    </div>
  </header>

  <main>
    <!-- 1. 파이프라인 진행률 -->
    <div class="glass-card span-2">
      <h2>실시간 에이전트 파이프라인 모니터링</h2>
      <div class="status-row">
        <div>상태: <span id="pipeline-status" style="font-weight: 700;">-</span></div>
        <div>현재 단계: <span id="pipeline-step" style="color: var(--accent-cyan); font-weight: 700;">-</span></div>
        <div id="pipeline-time" style="font-size: 0.85rem; color: #888;">업데이트: -</div>
      </div>
      <div class="progress-bar-bg">
        <div id="pipeline-progress" class="progress-bar-fill"></div>
      </div>
    </div>

    <!-- 2. 오늘 자 카드뉴스 에디터 & 프리뷰 -->
    <div class="glass-card">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>오늘의 카드뉴스 초안 (Draft Editor)</h2>
        <button class="btn-save" onclick="saveDraft()">💾 초안 저장하기</button>
      </div>
      <div class="cards-container" id="cardsContainer">
        <!-- JS로 동적 로드 -->
      </div>
    </div>

    <!-- 3. 마크다운 분석 리포트 -->
    <div class="glass-card">
      <h2>오늘의 분석 브리핑 리포트 (briefing_report.md)</h2>
      <div id="report-content">로딩 중...</div>
    </div>

    <!-- 4. RAG 지식 그래프 시각화 -->
    <div class="glass-card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h2 style="margin: 0;">RAG Wiki 지식 그래프 (Obsidian-style)</h2>
        <a href="obsidian://open?path=%2FUsers%2Fseongjegeun%2FDocuments%2FSNS_CAN_DO%2Fmedia-os%2Fbrain%2Fwiki" class="btn-save" style="text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; padding: 0.4rem 0.8rem;">
          💜 Obsidian 앱에서 열기
        </a>
      </div>
      <div id="wiki-graph"></div>
    </div>

    <!-- 5. SNS 성과 지표 모니터링 -->
    <div class="glass-card">
      <h2>인스타그램 / 스레드 성과 추이 (Analytics)</h2>
      <canvas id="performanceChart" style="max-height: 350px;"></canvas>
    </div>
  </main>

  <script>
    // ────────────────────────────────────────────────────────
    // 상태 및 데이터 풀링
    // ────────────────────────────────────────────────────────
    async function updateStatus() {
      try {
        const res = await fetch("/api/status");
        const data = await res.json();
        
        document.getElementById("pipeline-status").innerText = data.status;
        document.getElementById("pipeline-step").innerText = data.current_step;
        document.getElementById("pipeline-time").innerText = "업데이트: " + data.updated_at;
        document.getElementById("pipeline-progress").style.width = data.progress_percentage + "%";
        
        if (data.status === "RUNNING") {
          document.getElementById("pipeline-status").style.color = "var(--accent-cyan)";
        } else if (data.status === "COMPLETED") {
          document.getElementById("pipeline-status").style.color = "#4caf50";
        } else if (data.status === "ERROR") {
          document.getElementById("pipeline-status").style.color = "#f44336";
        } else {
          document.getElementById("pipeline-status").style.color = "#fff";
        }
      } catch (e) {
        console.error("Status fetch error", e);
      }
    }

    // ────────────────────────────────────────────────────────
    // 드래프트 데이터 로드 & 바인딩
    // ────────────────────────────────────────────────────────
    let currentCards = [];
    async function loadDraft() {
      try {
        const res = await fetch("/api/draft");
        const data = await res.json();
        currentCards = data.cards || [];
        renderCards();
      } catch (e) {
        console.error("Draft load error", e);
      }
    }

    function renderCards() {
      const container = document.getElementById("cardsContainer");
      if (currentCards.length === 0) {
        container.innerHTML = "<p style='color: #666; padding: 2rem; text-align:center;'>아직 생성된 카드뉴스 초안이 없습니다.</p>";
        return;
      }

      container.innerHTML = currentCards.map((card, idx) => `
        <div class="card-item" data-index="${idx}">
          <div class="card-header-inputs">
            <input type="text" placeholder="회사/주제" value="${card.company || ''}" onchange="updateCardField(${idx}, 'company', this.value)">
            <select onchange="updateCardField(${idx}, 'status', this.value)">
              <option value="official" ${card.status === 'official' ? 'selected' : ''}>공식 확인</option>
              <option value="reported" ${card.status === 'reported' ? 'selected' : ''}>보도 기준</option>
            </select>
            <input type="text" placeholder="테마 (예: apple)" value="${card.theme || ''}" onchange="updateCardField(${idx}, 'theme', this.value)">
          </div>
          <input type="text" placeholder="카드 제목 (초압축 20자 내외)" value="${card.title || ''}" onchange="updateCardField(${idx}, 'title', this.value)">
          <textarea placeholder="카드 요약 본문 (두 문장 내외)" onchange="updateCardField(${idx}, 'body', this.value)">${card.body || ''}</textarea>
          <input type="text" placeholder="출처" value="${card.source || ''}" onchange="updateCardField(${idx}, 'source', this.value)">
          <input type="text" placeholder="이미지 검색어 (영문)" value="${card.image_search || ''}" onchange="updateCardField(${idx}, 'image_search', this.value)">
          
          <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--accent-purple); font-weight: bold;">스레드(Threads) 발행 본문</div>
          <div class="threads-inputs">
            <textarea placeholder="1. 훅 (Hook)" onchange="updateThreadsField(${idx}, 'hook', this.value)">${card.threads?.hook || ''}</textarea>
            <textarea placeholder="2. 상세 요약" onchange="updateThreadsField(${idx}, 'detail', this.value)">${card.threads?.detail || ''}</textarea>
            <textarea placeholder="3. 맥락 및 해시태그" onchange="updateThreadsField(${idx}, 'context', this.value)">${card.threads?.context || ''}</textarea>
            <textarea placeholder="4. 질문 유도" onchange="updateThreadsField(${idx}, 'question', this.value)">${card.threads?.question || ''}</textarea>
          </div>
        </div>
      `).join("");
    }

    function updateCardField(idx, field, value) {
      currentCards[idx][field] = value;
    }

    function updateThreadsField(idx, field, value) {
      if (!currentCards[idx].threads) currentCards[idx].threads = {};
      currentCards[idx].threads[field] = value;
    }

    async function saveDraft() {
      try {
        const res = await fetch("/api/draft/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ cards: currentCards })
        });
        const data = await res.json();
        alert(data.message);
      } catch (e) {
        alert("저장 실패: " + e);
      }
    }

    // ────────────────────────────────────────────────────────
    // 리포트 로드
    // ────────────────────────────────────────────────────────
    async function loadReport() {
      try {
        const res = await fetch("/api/report");
        const data = await res.json();
        document.getElementById("report-content").innerText = data.content;
      } catch (e) {
        document.getElementById("report-content").innerText = "리포트 로드 실패: " + e;
      }
    }

    // ────────────────────────────────────────────────────────
    // 지식 그래프 렌더링 (D3.js)
    // ────────────────────────────────────────────────────────
    async function renderWikiGraph() {
      const width = document.getElementById("wiki-graph").clientWidth;
      const height = 400;
      
      const svg = d3.select("#wiki-graph")
        .html("") // 초기화
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // 줌/팬을 받아주는 최상위 컨테이너 생성
      const container = svg.append("g");

      const zoom = d3.zoom()
        .scaleExtent([0.1, 8]) // 줌 범위: 10% ~ 800%
        .on("zoom", (event) => {
          container.attr("transform", event.transform);
        });

      svg.call(zoom);

      try {
        const res = await fetch("/api/wiki");
        const graph = await res.json();
        
        if (graph.nodes.length === 0) {
          svg.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "#666")
            .text("위키 노드가 존재하지 않습니다.");
          return;
        }

        const simulation = d3.forceSimulation(graph.nodes)
          .force("link", d3.forceLink(graph.links).id(d => d.id).distance(60))
          .force("charge", d3.forceManyBody().strength(-120))
          .force("center", d3.forceCenter(width / 2, height / 2));

        const link = container.append("g")
          .selectAll("line")
          .data(graph.links)
          .join("line")
          .attr("stroke", "rgba(255,255,255,0.15)")
          .attr("stroke-width", 1.5);

        const node = container.append("g")
          .selectAll("circle")
          .data(graph.nodes)
          .join("circle")
          .attr("r", 8)
          .attr("fill", d => {
            if (d.group === "topics") return "var(--accent-cyan)";
            if (d.group === "entities") return "var(--accent-purple)";
            if (d.group === "trends") return "#f44336";
            return "#aaa";
          })
          .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

        const label = container.append("g")
          .selectAll("text")
          .data(graph.nodes)
          .join("text")
          .attr("dy", -10)
          .attr("text-anchor", "middle")
          .attr("fill", "rgba(255,255,255,0.7)")
          .attr("font-size", "10px")
          .text(d => d.id);

        simulation.on("tick", () => {
          link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

          node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

          label
            .attr("x", d => d.x)
            .attr("y", d => d.y);
        });

        function dragstarted(event, d) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        }

        function dragged(event, d) {
          d.fx = event.x;
          d.fy = event.y;
        }

        function dragended(event, d) {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }

      } catch (e) {
        console.error("Wiki graph error", e);
      }
    }

    // ────────────────────────────────────────────────────────
    // 차트 그리기 (Chart.js)
    // ────────────────────────────────────────────────────────
    let performanceChart = null;
    async function renderChart() {
      try {
        const res = await fetch("/api/analytics");
        const data = await res.json();
        
        const ctx = document.getElementById("performanceChart").getContext("2d");
        
        if (performanceChart) performanceChart.destroy();
        
        performanceChart = new Chart(ctx, {
          type: "line",
          data: {
            labels: data.labels,
            datasets: [
              {
                label: "조회수 (Reach)",
                data: data.views,
                borderColor: "rgba(102, 252, 241, 1)",
                backgroundColor: "rgba(102, 252, 241, 0.1)",
                borderWidth: 2,
                tension: 0.3,
                fill: true
              },
              {
                label: "저장수 (Saves)",
                data: data.saves,
                borderColor: "rgba(187, 134, 252, 1)",
                backgroundColor: "rgba(187, 134, 252, 0.1)",
                borderWidth: 2,
                tension: 0.3,
                fill: true
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: {
                grid: { color: "rgba(255, 255, 255, 0.05)" },
                ticks: { color: "#888" }
              },
              y: {
                grid: { color: "rgba(255, 255, 255, 0.05)" },
                ticks: { color: "#888" }
              }
            },
            plugins: {
              legend: {
                labels: { color: "#fff" }
              }
            }
          }
        });
      } catch (e) {
        console.error("Chart render error", e);
      }
    }

    // ────────────────────────────────────────────────────────
    // 초기화
    // ────────────────────────────────────────────────────────
    window.addEventListener("load", () => {
      updateStatus();
      loadDraft();
      loadReport();
      renderWikiGraph();
      renderChart();
      
      // 파이프라인 모니터링: 10초마다 풀링
      setInterval(updateStatus, 10000);
      
      // 초안 및 리포트: 30초마다 풀링 (수동 갱신 보완)
      setInterval(() => {
        loadDraft();
        loadReport();
        renderWikiGraph();
      }, 30000);
    });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

# uvicorn 실행만 포함 (스케줄링은 안티그래비티 2.0 UI 스케줄러에서 전담)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
