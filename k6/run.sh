#!/bin/bash

# K6 부하 테스트 실행 스크립트
# Prometheus로 메트릭 전송

# ## 환경변수 설명

# - **K6_PROMETHEUS_RW_SERVER_URL**: Prometheus Remote Write 엔드포인트 (필수)
# - **K6_PROMETHEUS_RW_TREND_STATS**: Prometheus로 전송할 메트릭 통계 (선택, 기본값: p(99),min,max,avg)
#   - `p(0.5)`: 중앙값 (50%)
#   - `p(0.9)`: 90 퍼센타일
#   - `p(0.95)`: 95 퍼센타일
#   - `p(0.99)`: 99 퍼센타일
#   - `min`, `max`, `avg`, `count`: 최소/최대/평균/횟수

# ## Grafana 모니터링

# 테스트 실행 후 Grafana에서 실시간 모니터링:
# - URL: http://192.168.80.90:30090
# - Test ID로 필터링: `testid="run-02"`

# Prometheus 설정
export K6_PROMETHEUS_RW_SERVER_URL="http://192.168.80.90:30090/api/v1/write"
export K6_PROMETHEUS_RW_TREND_STATS="p(0.5),p(0.9),p(0.95),p(0.99),min,max,avg,count"

# K6 실행
k6 run -o experimental-prometheus-rw --tag testid="run-02" shopping.js
