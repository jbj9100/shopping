#!/bin/bash

# 테스트 계정 생성 스크립트 (디버그 모드)
# users.csv 파일의 모든 계정을 읽어서 백엔드에 회원가입 요청

BASE_URL="https://shopping.project.com/api/shop"
CSV_FILE="users.csv"

echo "======================================"
echo "Creating Load Test Users (DEBUG)"
echo "Reading from: $CSV_FILE"
echo "======================================"

# CSV 파일 존재 확인
if [ ! -f "$CSV_FILE" ]; then
  echo "Error: $CSV_FILE not found!"
  exit 1
fi

SUCCESS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
TOTAL=0

# CSV 파일 헤더 제외하고 모든 라인 읽기
while IFS=',' read -r EMAIL PASSWORD; do
  # 공백 및 개행 제거
  EMAIL=$(echo "$EMAIL" | tr -d ' \r\n')
  PASSWORD=$(echo "$PASSWORD" | tr -d ' \r\n')
  
  # 이메일에서 username 생성 (소문자로 - 백엔드 스키마 요구사항)
  # loadtest1@test.com -> loadtest1
  USERNAME=$(echo "$EMAIL" | sed 's/@.*//' | tr -d ' \r\n')
  
  TOTAL=$((TOTAL + 1))
  echo ""
  echo "[$TOTAL] Creating: $EMAIL"
  
  # 요청 데이터 출력 (디버깅용)
  REQUEST_DATA="{\"email\":\"${EMAIL}\",\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}"
  echo "  Request: $REQUEST_DATA"
  
  # 회원가입 API 호출
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/signup/" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_DATA")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  echo "  HTTP Code: $HTTP_CODE"
  
  # 응답 코드에 따라 처리
  if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    echo "  Result: ✓ Created"
  elif echo "$BODY" | grep -iq "already"; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
    echo "  Result: ○ Already exists"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo "  Result: ✗ Failed"
    echo "  Response: $BODY"
  fi
  
  # 처음 3개만 디버깅하고 중단 (전체 실행은 -d 옵션으로)
  if [ $TOTAL -eq 3 ] && [ "$1" != "-all" ]; then
    echo ""
    echo "======================================"
    echo "DEBUG MODE: Stopped after 3 attempts"
    echo "Run with -all flag to create all users"
    echo "======================================"
    break
  fi
  
  # Rate limiting 방지
  sleep 0.2
  
done < <(tail -n +2 "$CSV_FILE")

echo ""
echo "======================================"
echo "Summary:"
echo "  Total: $TOTAL"
echo "  Created: $SUCCESS_COUNT"
echo "  Skipped: $SKIP_COUNT"
echo "  Failed: $FAIL_COUNT"
echo "======================================"

if [ $TOTAL -eq 0 ]; then
  echo "✗ No users in CSV file!"
  exit 1
elif [ $FAIL_COUNT -gt 0 ]; then
  echo "✗ Some requests failed. Check error messages above."
  exit 1
else
  echo "✓ All users created successfully!"
  exit 0
fi
