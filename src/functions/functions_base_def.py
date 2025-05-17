function_definitions = [
    {
        "name": "generate_production_chart",
        "description": "기간별 생산량 조회하여 그래프를 생성하여 이미지 파일 경로를 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "조회 시작 날짜 (YYYY-MM-DD 형식)",
                },
                "end_date": {
                    "type": "string",
                    "description": "조회 종료 날짜 (YYYY-MM-DD 형식)",
                },
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "generate_monthly_average_production_chart",
        "description": "주어진 기간 동안 월별 평균 생산량을 계산하여 막대 그래프를 생성하고, 이미지 파일 경로를 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "조회 시작 날짜 (YYYY-MM-DD 형식)",
                },
                "end_date": {
                    "type": "string",
                    "description": "조회 종료 날짜 (YYYY-MM-DD 형식)",
                },
            },
            "required": ["start_date", "end_date"],
        },
    }
]
