#Function calling 함수 정의
functions = [
    {
        "name": "get_production_summary",
        "description": "지정된 날짜 범위의 생산 수량 요약 정보를 조회합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "조회 시작일 (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "조회 종료일 (YYYY-MM-DD)"}
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "get_amr_status_by_node",
        "description": "각 위치(node)별 AMR 대수를 조회합니다.",
        "parameters": {"type": "object", "properties": {}}
    }
]