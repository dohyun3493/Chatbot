# DB 스키마
DB_SCHEMA = """
`테이블: production
- timestamp (DATETIME): 데이터가 기록된 날짜와 시간
- work_order (VARCHAR): 생산 작업을 식별하는 고유 번호
- product_code (VARCHAR): 생산 중인 제품 코드
- machine_id (VARCHAR): 작업에 사용된 설비 ID
- planned_qty (INT): 계획된 생산량 수
- completed_qty (INT): 실제 완료된 생산 수량
- production_status (VARCHAR): 작업 상태 (예: 진행 중, 완료, 에러 등)
- worker (VARCHAR): 작업자 이름

테이블: amr
- timestamp (DATETIME): 데이터가 기록된 날짜와 시간
- amr_id (VARCHAR): 자율이동로봇의 식별자
- node_label (VARCHAR): AMR의 현재 위치를 나타내는 라벨
- amr_status (VARCHAR): AMR의 현재 상태 (예: 이동 중, 대기 등)
- battery (DECIMAL): AMR의 현재 배터리 잔량 (%)
- mission (VARCHAR): 수행 중인 작업 내용
- lift_status (VARCHAR): 리프트 장치 상태 (예: 올림, 내림 등)
- speed (DECIMAL): AMR의 현재 이동 속도 (m/s)
"""

GENERAL_SYSTEM_MSG = """
너는 공장의 운영을 돕는 친절한 비서야.
"""

FUNCTION_SYSTEM_MSG = """
너는 아래 데이터베이스를 기반으로 사용자의 질문을 분석하여 적절한 함수를 호출해야 하는 AI 비서야.

- 사용자 질문을 읽고, 적절한 함수 이름과 인자를 포함한 function_call을 반환해.
- 직접 SQL을 작성하지 마.
- 정의된 함수 외의 요청은 처리하지 않아도 된다.
"""

NLG_SYSTEM_MSG = "다음 데이터를 보고 자연스럽고 친절한 문장으로 요약해줘."

NLG_USER_TEMPLATE = "질문: {question}\n데이터: {data}"