function_definitions = [
    {
        "name": "get_worker_by_machine",
        "description": (
            "특정 기계를 사용하는 작업자 목록을 반환합니다. "
            "예를 들어 '기계1 누가 썼어?', 'MCH003 사용한 사람은?', "
            "'기계3번 작업자는 누구야?' 같은 질문에 대응합니다. "
            "machine_id는 반드시 입력해야 하며, 날짜(date)가 없으면 기본적으로 오늘 기준으로 조회됩니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "machine_id": {
                    "type": "string",
                    "description": "조회할 기계 ID입니다. 예: 'MCH001', 'MCH003'"
                },
                "date": {
                    "type": "string",
                    "description": "조회할 날짜. 예: '2025-04-05'. 생략 시 오늘 날짜 기준으로 처리됩니다."
                }
            },
            "required": ["machine_id"]
        }
    },
    {
        "name": "get_production_summary",
        "description": (
            "특정 날짜(date)에 대한 생산 계획 수량, 실제 완료 수량, 생산 상태를 요약해 반환합니다. "
            "예를 들어 '4월 5일 생산 현황은?', '오늘 생산 얼마나 됐어?', '생산 완료됐어?' 같은 질문에 대응합니다. "
            "날짜를 입력하지 않으면 오늘 날짜 기준으로 자동 조회합니다. "
            "결과에는 시간대별 완료 수량도 함께 포함됩니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "조회할 날짜. 형식은 'YYYY-MM-DD' (예: '2025-04-05'). 생략하면 오늘 날짜로 조회됩니다."
                }
            }
        }
    },
    {
        "name": "get_average_daily_completed_quantity",
        "description": (
            "지정한 기간(start_date ~ end_date) 동안 매일 완료된 생산량의 평균을 계산합니다. "
            "start_date와 end_date를 생략하면 이번 달 전체 기준으로 계산합니다. "
            "예: '4월 한 달 평균 생산량은?', '4월 10일부터 15일까지 평균은?' 같은 질문에 대응합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "조회 시작 날짜. 예: '2025-04-01'. 생략 가능."
                },
                "end_date": {
                    "type": "string",
                    "description": "조회 종료 날짜. 예: '2025-04-30'. 생략 가능."
                }
            }
        }
    }
]
