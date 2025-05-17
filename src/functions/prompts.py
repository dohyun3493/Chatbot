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
다음 문장이 SQL 쿼리가 필요한지 여부를 'true' 또는 'false'로 답하시오.
Function Calling 으로 처리할 경우 false로 답하시오.:

- 반드시 응답은 **영어로** 'true' 또는 'false'로만 답합니다. 다른 단어를 포함하지 않습니다.
- "그래프", "차트", "분석", "시각화"라는 단어가 포함된 경우는 무조건 Function Calling으로 처리합니다.
- "시간대별", "일별", "월별", "연도별" 등 특정 기간 또는 시간 단위별 데이터를 요청하는 경우는 SQL로 처리합니다.
- 생산량, 기계 번호, 생산 상태 등 공장 데이터를 직접 조회하거나 특정 값을 가져오는 경우는 SQL 쿼리가 필요합니다.
- "생산량 조회", "기계 상태", "데이터 목록", "평균 구하기", "모든 데이터를 보여줘"와 같은 질문은 모두 SQL로 처리합니다.
- 평균값이나 합계, 데이터 목록을 구하는 연산도 SQL로 처리합니다.
- "그래프를 그려줘", "통계 분석", "데이터 시각화", "데이터 트렌드 보여줘" 같은 질문은 Function Calling으로 처리합니다.

예시:
1. "1월달 생산량 그래프로 보여줘." -> false (function calling)
2. "1월달 생산량을 조회해줘." -> true (SQL)
3. "기계 상태를 알려줘." -> true (SQL)
4. "생산 데이터를 모두 보여줘." -> true (SQL)
5. "생산 데이터의 평균을 계산해줘." -> true (SQL)
6. "생산 데이터를 분석해서 그래프로 보여줘." -> false (function calling)
7. "시간대별 생산량을 보여줘." -> true (SQL)
8. "1월달 시간대별 생산량 그래프로 보여줘." -> false (function calling)

문장: "{user_msg}"
"""

SQL_PROMPT_TEMPLATE = f"""
다음 질문을 SQL로 변환하세요.  
SQL만 작성하고, 일반 답변은 하지 마십시오.  
코드 블록 없이 순수 SQL만 작성하세요.  

조건:
- `completed_qty`는 **오전 9시부터 오후 6시까지 누적된 생산량**입니다.  
- **실제 하루 생산량은 `18:00:00` 시점의 `completed_qty`**로 간주합니다.
- **시간 조건이 명시되지 않은 경우, 반드시 `AND TIME(timestamp) = '18:00:00'` 조건을 명시적으로 SQL에 포함해야 합니다.**
- **월별 요청 시**, 해당 월의 모든 날짜에 대해 `18:00:00` 누적 생산량만 조회합니다.
- 시간 조건이 명시된 경우 해당 시간의 데이터를 조회하며, "시간대별" 요청은 하루 내 모든 시간대 데이터를 조회합니다.
- 월, 분기 단위 계산 시 종료일은 항상 **해당 기간의 다음 달 1일 18시**를 사용하여 `timestamp <` 방식으로 처리합니다.
- "알려줘", "보여줘", "알려줄래", "알려줘봐" 등은 모두 동일하게 취급하며, 리스트 형태로 날짜별 18시 생산량을 보여주는 쿼리를 작성합니다.
- 사용자 질문이 ‘24년 1월 ~ 12월 생산량 알려줘’처럼 연속된 월 전체 기간인 경우 SQL 쿼리로 생성되도록 유도하세요:

예시:
- 질문: "24년 1월 1일 생산량 알려줘"  
  SQL:  
  SELECT completed_qty FROM production_data  
  WHERE timestamp = '2024-01-01 18:00:00';

- 질문: "24년 1월 ~ 3월 평균 생산량 알려줘"  
  SQL:  
  SELECT AVG(completed_qty) FROM production_data  
  WHERE timestamp >= '2024-01-01 18:00:00'  
    AND timestamp < '2024-04-01 18:00:00'  
    AND TIME(timestamp) = '18:00:00';

- 질문: "24년 1월 생산량 보여줘"  
  SQL:  
  SELECT DATE(timestamp), completed_qty FROM production_data  
  WHERE timestamp >= '2024-01-01 18:00:00'  
    AND timestamp < '2024-02-01 18:00:00'  
    AND TIME(timestamp) = '18:00:00'  
  ORDER BY timestamp;

- 질문: "24년 각 달의 생산량 알려줘"
  SQL:
  SELECT DATE(timestamp), completed_qty  
  FROM production_data  
  WHERE timestamp >= '2024-01-01 18:00:00' AND timestamp < '2025-01-01 18:00:00'  
    AND TIME(timestamp) = '18:00:00'  
  ORDER BY timestamp;

테이블 정보: {DB_SCHEMA}  
질문: {{user_msg}}  
간단하고 효율적인 SQL:
"""

# 시스템 메시지
GENERAL_SYSTEM_MSG = """
너는 공장의 운영을 돕는 친절한 비서야.
- 일단 공장과 관련된 채팅 내역이 아니면 답변하지마.
"""

FUNCTION_SYSTEM_MSG = """
너는 아래 데이터베이스를 기반으로 사용자의 질문을 분석하여 적절한 함수를 호출해야 하는 AI 비서야.
- 사용자가 '4월 5일' 같이 말하면 반드시 '2025-04-05'와 같은 ISO 날짜 포맷으로 함수 인자에 넘겨.
- 사용자 질문을 읽고, 적절한 함수 이름과 인자를 포함한 function_call을 반환해.
- 직접 SQL을 작성하지 마.
- 정의된 함수 외의 요청은 처리하지 않아도 돼.
"""

NLG_SYSTEM_MSG = """
데이터를 모두 빠짐없이 나열하여 출력하십시오. 결과가 여러 개일 경우 전부 표기하고, 요약하지 마십시오.
- 데이터가 나오는데 요약해줘 라는 말이 없으면 요약하지 말고 전부 보여줘.
- 예시로 24년 1월 전체 생산량 알려줘 라고 하면 30일의 데이터를 전부 보여줘야 돼.
- 데이터가 많을 경우에는 10개 단위로 줄을 바꾸어 보기 좋게 정렬해줘.
- 출력 예시:
  - 25년 1월에 생산된 제품의 양은 다음과 같습니다:
    116, 39, 78, 117, 158, 44, 88, 132, 178, 41
    82, 123, 164, 44, 88, 132, 177, 30, 60, 90
"""

NLG_USER_TEMPLATE = """
질문: {question}
데이터: {data}
"""
