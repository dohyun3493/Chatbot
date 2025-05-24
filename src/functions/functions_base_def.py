function_definitions = [
    {
        "name": "generate_production_chart",
        "description": (
            "일별 생산량을 날짜별로 막대그래프로 시각화합니다. "
            "예: '2024년 1월부터 3월까지 각 날짜의 생산량 그래프로 보여줘', "
            "'1월 1일부터 1월 30일까지 일별 생산량', '각 날짜별 생산량 그래프' 요청에 적합합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "조회 시작 날짜 (YYYY-MM-DD 형식)"},
                "end_date": {"type": "string", "description": "조회 종료 날짜 (YYYY-MM-DD 형식)"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "generate_monthly_total_production_chart",
        "description": (
            "월별 총 생산량(각 월 일별 생산량 합계)을 그래프로 시각화합니다. "
            "예: '1월부터 3월까지 각 달 생산량', '24년 상반기 생산량 시각화', "
            "'분기별 생산량 보고 싶어', '월별 총 생산량', '월별 누적' 요청에 적합합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "조회 시작 날짜 (YYYY-MM-DD 형식)"},
                "end_date": {"type": "string", "description": "조회 종료 날짜 (YYYY-MM-DD 형식)"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "generate_monthly_average_production_chart",
        "description": (
            "월별 평균 생산량을 선그래프로 시각화합니다. "
            "예: '24년 상반기 월별 평균 생산량 그래프', '월간 평균 생산 추이 보고 싶어' 요청에 적합합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "조회 시작 날짜 (YYYY-MM-DD 형식)"},
                "end_date": {"type": "string", "description": "조회 종료 날짜 (YYYY-MM-DD 형식)"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "generate_monthly_machine_comparison_chart",
        "description": (
            "기계별 월별 평균 생산량을 선그래프로 비교 시각화합니다. "
            "예: '각 기계의 월별 생산량 비교', '기계별 생산 트렌드 보여줘' 요청에 적합합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "조회 시작 날짜 (YYYY-MM-DD 형식)"},
                "end_date": {"type": "string", "description": "조회 종료 날짜 (YYYY-MM-DD 형식)"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "generate_status_distribution_chart",
        "description": (
            "생산 상태별 건수를 파이 차트로 시각화합니다. "
            "예: '생산 상태 비율 보여줘', '상태별 작업 분포 알려줘' 요청에 적합합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "조회 시작 날짜 (YYYY-MM-DD 형식)"},
                "end_date": {"type": "string", "description": "조회 종료 날짜 (YYYY-MM-DD 형식)"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "generate_total_production_by_machine_chart",
        "description": (
            "각 기계별 총 생산량(합계)을 막대그래프로 시각화합니다. "
            "예: '2024년 기계별 총 생산량 그래프로 보여줘', '1월~6월 어떤 기계가 가장 많이 생산했는지 알려줘' 요청에 적합합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "조회 시작 날짜 (YYYY-MM-DD 형식)"},
                "end_date": {"type": "string", "description": "조회 종료 날짜 (YYYY-MM-DD 형식)"},
            },
            "required": ["start_date", "end_date"],
        },
    },
]
