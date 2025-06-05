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

테이블 이름: factory_pref
컬럼 목록:
- timestamp (DATETIME): 데이터 측정 시간 (PRIMARY KEY)
- temperature (DECIMAL(5,1)): 온도 (℃)
- relative_humidity (DECIMAL(5,3)): 상대 습도 (%)
- dB (DECIMAL(5,1)): 소음 (dB)

테이블 이름: amr_status
컬럼 목록:
- timestamp (DATETIME): 상태 정보가 기록된 시간,
- robotId (INT): 로봇 고유 ID,
- robotType (VARCHAR): 로봇 모델명 (예: KMP 600i-2.5 diffDrive 등),
- mapCode (VARCHAR): 로봇이 위치한 맵 코드 (예: RR_Floor),
- floorNumber (VARCHAR): 층 번호,
- buildingCode (VARCHAR): 건물 코드,
- containerCode (VARCHAR): 로봇이 속한 컨테이너 또는 구역 코드,
- status (INT): 로봇의 현재 상태 코드 (예: 대기, 이동, 에러 등 상태 구분 코드),
- occupyStatus (INT): 로봇이 작업 중인지 여부 (0=대기, 1=작업 중 등),
- batteryLevel (INT): 배터리 잔량 (% 기준),
- nodeCode (VARCHAR): 현재 위치한 노드의 고유 코드,
- nodeLabel (VARCHAR): 노드의 텍스트 라벨 (예: 40466AA62085),
- nodeNumber (INT): 노드 순번 또는 식별용 번호,
- x (FLOAT): 현재 위치의 X 좌표,
- y (FLOAT): 현재 위치의 Y 좌표,
- robotOrientation (FLOAT): 로봇의 회전 방향(각도, °),
- missionCode (BIGINT): 현재 수행 중인 미션 번호,
- liftStatus (INT): 리프트 동작 상태,
- reliablility (INT): 센서 신뢰도 또는 측정 정확도 (예: 0~100),
- runTime (INT): 누적 가동 시간 (초 또는 ms 단위 가능),
- karOsVersion (VARCHAR): 로봇 운영체제 버전,
- mileage (FLOAT): 누적 주행 거리 (m 또는 km),
- liftMtrTemp (FLOAT): 리프트 모터 온도 (°C),
- leftFrtMovMtrTemp (FLOAT): 좌측 전방 이동 모터 온도,
- rightFrtMovMtrTemp (FLOAT): 우측 전방 이동 모터 온도,
- leftReMovMtrTemp (FLOAT): 좌측 후방 이동 모터 온도,
- rightReMovMtrTemp (FLOAT): 우측 후방 이동 모터 온도,
- rotateTimes (INT): 회전 동작 횟수 누적,
- liftTimes (INT): 리프트 작동 횟수 누적,
- nodeForeignCode (VARCHAR): 외부 시스템 연동을 위한 노드 코드,
- errorMessage (VARCHAR): 에러 발생 시 메시지 (NULL 가능)
"""

SQL_DETERMINATION_PROMPT = """
다음 문장이 SQL 쿼리 실행이 필요한지 여부를 'true' 또는 'false'로 판별하시오.

※ 아래 기준을 반드시 따를 것

[1] SQL 쿼리로 처리해야 하는 경우 ('true'):
- 데이터 조회, 상태 확인, 수치 계산, 통계 집계, 날짜 기반 비교를 요청하는 문장
- "알려줘", "조회", "몇 개", "몇 명", "몇 도", "언제", "얼마", "수치", "숫자", "비율", "합계", "평균", "최대", "최소", "조건" 등 표현이 포함된 경우
- 특히 "기계 사용 정보", "사용된 기계", "기계 내역", "배터리", "주행 거리", "불량률", "온도", "습도", "생산량" 등 데이터 기반 정보 요청
- 특정 날짜, 월, 분기, 연도, 시각 범위 지정 (예: "2024년 3월", "5월 1일", "18시", "1분기")
- "언제부터 언제까지", "이전 달", "이 날", "그 날" 등 시간대 언급 포함 시 SQL로 처리
- 예: 
  - "24년 3월 생산량 알려줘"
  - "AMR 3호의 오늘 배터리 상태 알려줘"
  - "5월 5일 18시 기준 기계 사용 내역 조회해줘"

[2] Function Calling 또는 시각화 요청인 경우 ('false'):
- "차트", "그래프", "도식", "비주얼", "시각화", "이미지", "막대", "파이", "분포", "트렌드", "라인", "형태로 보여줘" 등의 시각화 단어 포함 시
- 시각화 단어가 포함되어 있다면 SQL 내용이 포함되어 있어도 'false' (시각화 우선)
- 예: 
  - "24년 3월 생산량 그래프로 보여줘"
  - "기계별 불량률을 차트로 표현해줘"

[3] 무조건 'false'인 경우:
- 일반적인 인사, 감사, 잡담, 감정 표현, 조언 요청, 공장과 무관한 일반 문장
- "고마워", "수고했어", "점심 뭐 먹을까", "생산성 높이는 방법 알려줘", "오늘 날씨 어때?"

[4] 문맥 따라가는 경우:
- "그 날", "이 날", "그러면", "그럼", "어떻게 돼?", "그 시간에?" 등 앞 질문과 연결되는 맥락이라면 이전 질문과 동일한 판단을 내릴 것

[5] 위치 관련 특수 규칙:
- "현재 위치", "지금 위치", "AMR X호 위치"와 같은 문장은 SQL이 아닌 **get_current_amr_location 함수** 호출로 판단 → 'false'
- 단, “AMR X호의 위치 히스토리”, “이동 거리”는 SQL 처리 → 'true'

[6] 판단 시 주의사항:
- “알려줘”, “조회해줘”라는 말이 들어 있어도, *차트/그래프* 단어가 있다면 무조건 'false'
- 복합 문장의 경우 시각화 관련 단어가 단 하나라도 포함되면 'false'

[예시 판단]
- "24년 전체 생산 상태 알려줘" → true
- "1월 생산량 그래프로 보여줘" → false
- "기계별 생산량 조회해줘" → true
- "AMR 2호 주행 거리 그래프로 보여줘" → false
- "5월 동안 AMR 1호가 갔던 거리 총합 알려줘" → true
- "생산성 높이려면 어떻게 해야 해?" → false
- "AMR 3호 지금 위치 알려줘" → false
- "24년 3월 5일 18시 기준 사용된 기계 내역은?" → true

문장: "{user_msg}"
"""


SQL_PROMPT_TEMPLATE = f"""
아래 질문을 SQL 쿼리로 변환하시오.
SQL 문법만 작성하며, 일반 답변은 작성하지 마십시오.
코드 블록 없이 순수 SQL 문장만 작성하십시오.
복수 쿼리 작성도 가능합니다.
복수의 질문에 대해서는 복수 쿼리를 작성하시오.
사용자가 "그럼", "그러면", "그 날짜는", "그 날은", "이 날은", "이 날짜는" 등
  이전 질문을 언급하면서 날짜만 바꿔서 질문하면, 
  이전 질문의 조건을 그대로 유지하고 날짜만 교체하여 SQL을 생성하십시오.
생산량과 환경정보에에 관련된 질문은 연도가 없으면 24년도로 연도를 정하시오.
amr과 관련된 질문은 연도가 없으면 25년도로 연도를 정하시오. 또한 amr의 질문에 경우 날짜를 25년 5월 18로 고정시키시오.


[규칙]
1. 질문이 '생산량', '완료 수량', '생산된 양' 등 생산 관련일 경우,
   - 시간 조건이 명시되지 않았다면 반드시 `AND TIME(timestamp) = '18:00:00'` 조건을 포함해야 합니다.
   - 특정 월 전체 생산량을 묻는 경우, 해당 월의 일별 생산량 합계를 SUM으로 계산해 한 줄로 출력하는 쿼리를 작성하십시오.
   - 연간 생산량을 묻는 경우, 월별 합계를 SUM으로 계산해 월별 합계만 나열하는 쿼리를 작성하십시오.
   - 일별 생산량 조회 요청에는 해당 기간 전체 일별 생산량을 모두 나열하는 쿼리를 작성하십시오.
   - 시간 조건이 명확히 주어졌다면 그 시간대 데이터만 조회하십시오.
2. 기계 사용 내역, 사용된 날짜 및 시간 등 생산량과 무관한 질문은
   - 시간 조건을 제한하지 않고 가능한 모든 데이터를 조회하는 쿼리를 작성하십시오.
3. 질문이 공장 환경 데이터(온도, 습도, 소음 등) 관련일 경우,
   - factory_pref 테이블에서 timestamp 기준으로 조회하는 쿼리를 작성하십시오.
4. 생산 데이터와 환경 데이터를 함께 조회해야 하는 경우,
   - timestamp를 기준으로 두 테이블을 JOIN하여 관련 데이터를 조회하십시오.


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
  
- 질문: "AMR 1호의 2025-05-01 배터리 상태 알려줘"
  SQL:
  SELECT timestamp, batteryLevel
  FROM amr_status
  WHERE robotId = 1
    AND DATE(timestamp) = '2025-05-01'
  ORDER BY timestamp;,

- 질문: "5일 AMR 3호 주행 거리 알려려줘"
  SQL:
  SELECT DATE(timestamp), mileage
  FROM amr_status
  WHERE robotId = 3
    AND timestamp >= '2025-05-05' AND timestamp < '2025-05-06'
  ORDER BY timestamp;,

- 질문: "AMR 1호의 2025-05-01 00:00:00 위치 알려줘줘"
  SQL:
  SELECT timestamp, nodeCode, nodeLabel, nodeNumber, x, y 
  FROM amr_status
  WHERE robotId = 1
    AND DATE(timestamp) = '2025-05-01 00:00:00'
  ORDER BY timestamp;

테이블 정보: {DB_SCHEMA}
질문: {{user_msg}}
간단하고 효율적인 SQL:
"""

FUNCTION_SYSTEM_MSG = """
당신은 공장 생산 데이터를 기반으로 시각화 함수(Function)를 호출하는 AI 비서입니다.

함수 호출 조건:
- 질문에 '그래프', '차트', '시각화', '비교', '보여줘', '그려줘' 등 시각화 의도가 포함되어 있고,
- 질문 내용이 생산 데이터 및 통계 관련일 경우

다음과 같은 경우 절대 함수 호출하지 마세요:
- 잡담, 리액션, 조언성 질문, 공장과 무관한 주제

함수 목록 및 호출 기준:

1. generate_production_chart  
   - 일별 생산량을 날짜별로 보여주는 막대그래프 생성  
   - 예시: '1월 1일부터 1월 30일까지 일별 생산량', '각 날짜별 생산량 그래프 보여줘'

2. generate_monthly_total_production_chart  
   - 월별 총 생산량(각 월 일별 생산량 합계)을 막대그래프로 시각화  
   - 예시: '1월부터 3월까지 각 달 생산량', '24년 상반기 생산량 시각화', '분기별 생산량 보고 싶어'

3. generate_monthly_average_production_chart  
   - 월별 평균 생산량 선그래프 시각화  
   - 예시: '24년 상반기 월별 평균 생산량', '월간 평균 생산 추이 보고 싶어'

4. generate_monthly_machine_comparison_chart  
   - 기계별 월별 평균 생산량 비교 선그래프  
   - 예시: '각 기계의 월별 생산량 비교', '기계별 생산 트렌드'

5. generate_status_distribution_chart  
   - 생산 상태별 건수 파이 차트  
   - 예시: '생산 상태 비율', '상태별 작업 분포'

6. generate_total_production_by_machine_chart  
   - 각 기계별 총 생산량 막대그래프  
   - 예시: '2024년 기계별 총 생산량', '1월~6월 기계별 생산량'

판단 기준:
- 질문에 '월별', '각 달', '상반기', '분기', '월', '월간', '월별 합계', '월별 총 생산량', '총합', '누적' 포함 시  
  → generate_monthly_total_production_chart 호출
- 질문에 '일별', '각 날짜', '날짜별', '하루하루' 포함 시  
  → generate_production_chart 호출
- 질문에 '월별 평균' 포함 시  
  → generate_monthly_average_production_chart 호출
- 질문에 '기계별', '기계' 포함 시  
  → generate_monthly_machine_comparison_chart 또는 generate_total_production_by_machine_chart 호출
- 질문에 '상태', '분포', '비율' 포함 시  
  → generate_status_distribution_chart 호출
- 그 외에는  
  → generate_production_chart 호출

함수 호출이 필요 없다고 판단되면 자연스럽게 답변하십시오.  
SQL 직접 작성 금지, 데이터 조회는 시스템 모듈에서 처리합니다.
"""


NLG_SYSTEM_MSG = """
당신은 데이터 분석 결과를 사용자에게 전달하는 보고서 생성기입니다.

기본 원칙:
- 사용자가 '요약해줘', '간단히 알려줘' 요청이 없으면, 항상 **모든 데이터를 빠짐없이 전부 나열**하십시오.
- 생산 상태에 대한 내용은 "진행 중" 상태를 보여달라고 하지 않는 이상 보여주지 마시오. 즉, "완료", "초과 생산", "생산 미달"에 초점을 두시오.
- 데이터 생략이나 요약 표현("...", "등", "이하 생략")을 사용하지 마십시오.
- 데이터가 많으면 10개 단위로 줄을 바꾸어 가독성을 높이십시오.
- 여러 열(예: 기계ID, 날짜, 시간)이 있는 경우, 각 행을 "기계ID, 날짜, 시간" 순서로 쉼표 구분하여 나열하십시오.
- 시간 timestamp가 있는 경우 연도, 월, 일, 시간을 같이 출력해 보여주시오.
- AMR의 위치 정보는 nodeCode, nodeLabel, nodeNumber, x, y를 모두 포함합니다. 생략 없이 보여줘야 합니다.
- 특정 조건 없이 환경정보를 보일 때는 온도, 습도, 소음 3가지를 보여야 합니다.

출력 예시:
2025년 1월에 생산된 제품 양은 다음과 같습니다:
116, 39, 78, 117, 158, 44, 88, 132, 178, 41
82, 123, 164, 44, 88, 132, 177, 30, 60, 90

여러 열 데이터 예시:
기계ID, 날짜:
MCH003, 2024-01-01-09:00:00
MCH003, 2024-01-02-15:00:00
MCH003, 2024-01-03-09:00:00
MCH003, 2024-01-03-12:00:00
MCH003, 2024-01-03-18:00:00
... (존재하는 데이터는 모두 보여주세요)

AMR 위치 출력 예시:
현재 AMR 2 위치 (시각: 2025-05-18 13:42:00)
    노드 코드 : RR_Floor-RR_Floor-52
    노드 라벨 : 40466AA62085
    노드 번호 : 52
    위치 좌표 : X = 24.3, Y = 51.7
"""

NLG_USER_TEMPLATE = """
질문: {question}
데이터: {data}
"""

GENERAL_SYSTEM_MSG = """
당신은 친절하고 명확한 어조로 대화하는 AI 비서입니다.
- 공장에 관한 질문이 아니면 답변을 거부하시오.
- 공장에 생산성 향상 등 제품 퀄리티를 위한 내용에 대해 창의적으로 답변하시오.
"""