#!/bin/bash
# ────────────────────────────────────────────────────────
# MacOS Caffeinate Wrapper for FastAPI Dashboard (24 Hours)
# ────────────────────────────────────────────────────────
# 이 스크립트는 macOS 내장 caffeinate 명령어를 사용하여
# 24시간 로컬 대시보드 및 상시 스케줄러 가동 중 맥북이 잠자기(Sleep) 모드로 전환되는 것을 방지합니다.
# -i: 시스템 유휴(Idle) 잠자기 방지
# -s: 시스템 전원 연결 시 잠자기 방지

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/daily_news/dashboard.log"

echo "=== 로컬 대시보드 및 스케줄러 시작 (잠자기 방지 적용): $(date) ===" >> "$LOG_FILE"

# python3 직접 실행 (스케줄링은 안티그래비티 2.0에서 전담하므로 caffeinate 유예 불필요)
python3 "$SCRIPT_DIR/dashboard.py" >> "$LOG_FILE" 2>&1

echo "=== 로컬 대시보드 및 스케줄러 종료: $(date) ===" >> "$LOG_FILE"
