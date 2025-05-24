function_definitions = [
    {
    "name": "get_current_amr_location",
    "description": "현재 시뮬레이션 시간 기준으로 특정 AMR의 위치를 조회합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "robot_id": {
                "type": "integer",
                "description": "위치를 확인할 AMR의 ID (예: 1, 2, 3)"
                }
            },
        "required": ["robot_id"]
        }
    }
]