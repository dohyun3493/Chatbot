# functions/prompts.py

# DB 스키마 정보
DB_SCHEMA = """
테이블 이름: production_data
컬럼 목록:
- timestamp (DATETIME): 생산 시작 시간
- work_order (VARCHAR): 작업 지시 번호
- product_code (VARCHAR): 생산 제품 코드
- machine_id (VARCHAR): 기계 ID (도메인: MCH001, MCH002, MCH003, MCH004)
- planned_qty (INT): 계획된 생산 수량
- completed_qty (INT): 누적 완료된 생산 수량 (이전 값 포함)
- production_status (VARCHAR): 생산 상태 (도메인: 진행 중, 완료, 초과 생산, 생산 미달)
"""

SQL_DETERMINATION_PROMPT = """
다음 문장이 SQL 쿼리 실행이 필요한지 여부를 'true' 또는 'false'로 판별하시오.
Function Calling으로 처리할 경우에는 'false'를 반환하십시오.

- 반드시 영어 소문자로만 'true' 또는 'false'를 응답해야 하며, 그 외 다른 단어는 포함하지 않습니다.
- "그래프", "차트", "분석", "시각화" 등이 포함된 문장은 반드시 Function Calling으로 처리합니다.
- "시간대별", "일별", "월별", "연도별" 등 특정 기간 또는 시간 단위로 데이터를 조회하는 경우는 SQL 처리 대상입니다.
- 생산량, 기계 번호, 생산 상태 등 공장 관련 데이터를 조회하거나 특정 값을 얻는 경우는 SQL 처리 대상입니다.
- "생산량 조회", "기계 상태 확인", "데이터 목록 요청", "평균 계산", "전체 데이터 출력" 등의 요청도 SQL 쿼리 실행이 필요합니다.
- 평균, 합계, 데이터 목록을 구하는 연산 역시 SQL로 처리합니다.
- "그래프 그리기", "통계 분석", "데이터 시각화", "트렌드 확인" 등은 Function Calling으로 처리합니다.

예시:
1. "1월달 생산량 그래프로 보여줘." -> false (Function Calling)
2. "1월달 생산량을 조회해줘." -> true (SQL)
3. "기계 상태를 알려줘." -> true (SQL)
4. "생산 데이터를 모두 보여줘." -> true (SQL)
5. "생산 데이터 평균을 계산해줘." -> true (SQL)
6. "생산 데이터를 분석해서 그래프로 보여줘." -> false (Function Calling)
7. "시간대별 생산량을 보여줘." -> true (SQL)
8. "1월달 시간대별 생산량 그래프로 보여줘." -> false (Function Calling)

문장: "{user_msg}"
"""

SQL_PROMPT_TEMPLATE = f"""
아래 질문을 SQL 쿼리로 변환하시오.
SQL 문법만 작성하며, 일반 답변은 작성하지 마십시오.
코드 블록 없이 순수 SQL 문장만 작성하십시오.
복수 쿼리 작성도 가능합니다.

[규칙]
1. 질문이 '생산량', '완료 수량', '생산된 양' 등 생산 관련일 경우,
   - 시간 조건이 명시되지 않았다면 반드시 `AND TIME(timestamp) = '18:00:00'` 조건을 포함해야 합니다.
   - 특정 월 전체 생산량을 묻는 경우, 해당 월의 일별 생산량 합계를 SUM으로 계산해 한 줄로 출력하는 쿼리를 작성하십시오.
   - 연간 생산량을 묻는 경우, 월별 합계를 SUM으로 계산해 월별 합계만 나열하는 쿼리를 작성하십시오.
   - 일별 생산량 조회 요청에는 해당 기간 전체 일별 생산량을 모두 나열하는 쿼리를 작성하십시오.
   - 시간 조건이 명확히 주어졌다면 그 시간대 데이터만 조회하십시오.
2. 기계 사용 내역, 사용된 날짜 및 시간 등 생산량과 무관한 질문은
   - 시간 조건을 제한하지 않고 가능한 모든 데이터를 조회하는 쿼리를 작성하십시오.

[예시]
- 질문: "24년 1월 생산량 알려줘"
  SQL:
  SELECT SUM(completed_qty) FROM production_data
  WHERE timestamp >= '2024-01-01 18:00:00'
    AND timestamp < '2024-02-01 18:00:00'
    AND TIME(timestamp) = '18:00:00';

- 질문: "24년 생산량 알려줘"
  SQL:
  SELECT DATE_FORMAT(timestamp, '%Y-%m') AS month, SUM(completed_qty) AS monthly_sum
  FROM production_data
  WHERE timestamp >= '2024-01-01 18:00:00'
    AND timestamp < '2025-01-01 18:00:00'
    AND TIME(timestamp) = '18:00:00'
  GROUP BY DATE_FORMAT(timestamp, '%Y-%m')
  ORDER BY month;

- 질문: "24년 1월 생산량을 일별로 보여줘"
  SQL:
  SELECT DATE(timestamp) AS day, completed_qty
  FROM production_data
  WHERE timestamp >= '2024-01-01 18:00:00'
    AND timestamp < '2024-02-01 18:00:00'
    AND TIME(timestamp) = '18:00:00'
  ORDER BY day;

- 질문: "24년 생산량을 일별로 보여줘"
  SQL:
  SELECT DATE(timestamp) AS day, completed_qty
  FROM production_data
  WHERE timestamp >= '2024-01-01 18:00:00'
    AND timestamp < '2025-01-01 18:00:00'
    AND TIME(timestamp) = '18:00:00'
  ORDER BY day;

- 질문: "24년 1월에 기계4번 사용된 날짜 보여줘"
  SQL:
  SELECT DISTINCT DATE(timestamp) FROM production_data
  WHERE machine_id = 'MCH004'
    AND timestamp >= '2024-01-01 00:00:00'
    AND timestamp < '2024-02-01 00:00:00'
  ORDER BY DATE(timestamp);

- 질문: "24년 1월에 기계4번 사용된 날짜와 사용 시각 보여줘"
  SQL:
  SELECT DATE(timestamp), TIME(timestamp) FROM production_data
  WHERE machine_id = 'MCH004'
    AND timestamp >= '2024-01-01 00:00:00'
    AND timestamp < '2024-02-01 00:00:00'
  ORDER BY timestamp;

테이블 정보: {DB_SCHEMA}
질문: {{user_msg}}
간단하고 효율적인 SQL:
"""

FUNCTION_SYSTEM_MSG = """
당신은 아래 데이터베이스 정보를 기반으로 사용자 질문을 분석하여 적절한 함수 호출을 수행하는 AI 비서입니다.
- 사용자가 '4월 5일'과 같은 날짜를 말하면, 반드시 '2025-04-05' 형식의 ISO 날짜 포맷으로 함수 인자에 전달해야 합니다.
- 사용자 질문을 읽고 적절한 함수명과 인자를 포함한 function_call을 반환하십시오.
- 직접 SQL 쿼리를 작성하지 마십시오.
- 정의된 함수 외 요청은 처리하지 마십시오.
"""

NLG_SYSTEM_MSG = """
당신은 데이터 분석 결과를 사용자에게 전달하는 보고서 생성기입니다.

기본 원칙:
- 사용자가 '요약해줘', '간단히 알려줘' 요청이 없으면, 항상 **모든 데이터를 빠짐없이 전부 나열**하십시오.
- 데이터 생략이나 요약 표현("...", "등", "이하 생략")을 사용하지 마십시오.
- 데이터가 많으면 10개 단위로 줄을 바꾸어 가독성을 높이십시오.
- 여러 열(예: 기계ID, 날짜, 시간)이 있는 경우, 각 행을 "기계ID, 날짜, 시간" 순서로 쉼표 구분하여 나열하십시오.

출력 예시:
2025년 1월에 생산된 제품 양은 다음과 같습니다:
116, 39, 78, 117, 158, 44, 88, 132, 178, 41
82, 123, 164, 44, 88, 132, 177, 30, 60, 90

여러 열 데이터 예시:
기계ID, 날짜, 시간:
MCH003, 2024-01-01, 09:00:00
MCH003, 2024-01-02, 15:00:00
MCH003, 2024-01-03, 09:00:00
MCH003, 2024-01-03, 12:00:00
MCH003, 2024-01-03, 18:00:00
... (존재하는 데이터는 모두 보여주세요)
"""

NLG_USER_TEMPLATE = """
질문: {question}
데이터: {data}
"""
