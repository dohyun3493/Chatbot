import mysql.connector
from datetime import datetime
from typing import Optional, List
from db.sql_connection import get_connection


# 1. 생산량 조회 함수
def get_production_summary(date: Optional[str] = None) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    today = date or datetime.now().strftime("%Y-%m-%d")

    query = """
        SELECT timestamp, planned_qty, completed_qty, production_status
        FROM production_data
        WHERE DATE(timestamp) = %s
        ORDER BY timestamp
    """
    cursor.execute(query, (today,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        return {"error": f"{today} 기준 생산 데이터가 없습니다."}

    total_planned = rows[0]['planned_qty']
    latest_completed = rows[-1]['completed_qty']
    status = rows[-1]['production_status']

    time_details = [
        {
            "timestamp": row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            "completed_quantity": int(row['completed_qty']),
            "production_status": row['production_status']
        }
        for row in rows
    ]

    return {
        "planned_quantity": int(total_planned),
        "completed_quantity": int(latest_completed),
        "production_status": status,
        "time_details": time_details
    }

# 2. 평균 생산량 조회 함수
def get_average_daily_completed_quantity(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except Exception:
        return {"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요."}

    if start > end:
        return {"error": "시작 날짜가 종료 날짜보다 늦습니다."}

    # 날짜별 마지막 '완료' 상태의 timestamp 추출
    query = """
        SELECT DATE(timestamp) AS date_only, MAX(timestamp) AS latest_time
        FROM production_data
        WHERE DATE(timestamp) BETWEEN %s AND %s
          AND production_status = '완료'
        GROUP BY DATE(timestamp)
    """
    cursor.execute(query, (start_date, end_date))
    date_rows = cursor.fetchall()

    if not date_rows:
        return {"error": f"{start_date} ~ {end_date} 사이의 생산 데이터가 없습니다."}

    # 각 날짜의 마지막 완료 수량 조회
    daily_completed = []
    for row in date_rows:
        cursor.execute(
            "SELECT completed_qty FROM production_data WHERE timestamp = %s",
            (row['latest_time'],)
        )
        result = cursor.fetchone()
        if result:
            daily_completed.append(int(result['completed_qty']))

    cursor.close()
    conn.close()

    if not daily_completed:
        return {"error": "해당 기간에 완료된 작업이 없습니다."}

    avg_completed = round(sum(daily_completed) / len(daily_completed), 2)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "days_with_data": len(daily_completed),
        "average_daily_completed_quantity": avg_completed
    }

