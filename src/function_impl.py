import pandas as pd
import os
from datetime import datetime
from typing import List, Optional

# 현재 파일(function_impl.py) 기준 상위 폴더로 이동
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "production_data.csv")
df = pd.read_csv(csv_path)

# 1. 특정 기계를 사용하는 작업자 조회 (오늘 날짜 또는 지정한 날짜 기준)
def get_worker_by_machine(machine_id: str, date: Optional[str] = None) -> List[str]:
    if date is None:
        today = datetime.now().strftime("%Y-%m-%d")
    else:
        today = date

    df['date_only'] = pd.to_datetime(df['timestamp']).dt.strftime("%Y-%m-%d")
    filtered = df[(df['machine_id'] == machine_id) & (df['date_only'] == today)]
    
    if filtered.empty:
        return [f"{today} 기준으로 '{machine_id}' 기계를 사용하는 작업자가 없습니다."]
    
    return filtered['worker'].unique().tolist()


# 2. 생산량 조회
def get_production_summary(date: Optional[str] = None) -> dict:
    if df.empty:
        return {"error": "생산 데이터가 없습니다."}

    today = date or datetime.now().strftime("%Y-%m-%d")
    
    local_df = df.copy()
    local_df['date_only'] = pd.to_datetime(local_df['timestamp']).dt.strftime("%Y-%m-%d")
    filtered = local_df[local_df['date_only'] == today]

    if filtered.empty:
        return {"error": f"{today} 기준 생산 데이터가 없습니다."}

    total_planned = filtered['planned_qty'].iloc[0]
    latest_completed = filtered['completed_qty'].iloc[-1]
    status = filtered['production_status'].iloc[-1]

    # 시간별로 상태가 담김.
    time_details = [
        {
            "timestamp": row['timestamp'],
            "completed_quantity": int(row['completed_qty']),
            "production_status": row['production_status']
        }
        for _, row in filtered.iterrows()
    ]

    return {
        "planned_quantity": int(total_planned),
        "completed_quantity": int(latest_completed),
        "production_status": status,
        "time_details": time_details
    }
    
# 3. 생산량 평균을 구하는 함수수
def get_average_daily_completed_quantity(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    if df.empty:
        return {"error": "생산 데이터가 없습니다."}

    local_df = df.copy()
    local_df['date_only'] = pd.to_datetime(local_df['timestamp']).dt.strftime("%Y-%m-%d")

    # 시작 날짜 없으면 1일로, 종료 날짜 없으면 오늘로 설정
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    except Exception:
        return {"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요."}

    if start > end:
        return {"error": "시작 날짜가 종료 날짜보다 늦습니다."}

    # 지정한 날짜 범위
    mask = (pd.to_datetime(local_df['date_only']) >= start) & (pd.to_datetime(local_df['date_only']) <= end)
    period_df = local_df[mask]

    if period_df.empty:
        return {"error": f"{start_date} ~ {end_date} 사이의 생산 데이터가 없습니다."}

    # 날짜 별로 마지막 완료 기록만 추출
    daily_completed = []
    for day in pd.date_range(start, end):
        day_str = day.strftime("%Y-%m-%d")
        day_df = period_df[(period_df['date_only'] == day_str) & (period_df['production_status'] == '완료')]
        if not day_df.empty:
            last_completed = day_df.sort_values('timestamp').iloc[-1]['completed_qty']
            daily_completed.append(int(last_completed))

    if not daily_completed:
        return {"error": "해당 기간에 완료된 작업이 없습니다."}

    avg_completed = round(sum(daily_completed) / len(daily_completed), 2)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "days_with_data": len(daily_completed),
        "average_daily_completed_quantity": avg_completed
    }

