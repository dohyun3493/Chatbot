import time
from datetime import datetime
from db.sql_connection import get_connection
from collections import defaultdict
import functions.function_amr_impl

def amr_alert():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM amr_status
        WHERE DATE(timestamp) = '2025-05-18'
        ORDER BY timestamp ASC
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    grouped = defaultdict(list)
    for row in data:
        key_time = row['timestamp'].strftime('%Y-%m-%d %H:%M:00')
        grouped[key_time].append(row)

    for timestamp_str in sorted(grouped.keys()):
        functions.function_amr_impl.current_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        rows = grouped[timestamp_str]

        warnings = [
            row for row in rows
            if row['batteryLevel'] <= 20 or row['liftMtrTemp'] >= 70
        ]

        warnings.sort(key=lambda r: r['robotId'])

        if not warnings:
            time.sleep(10)
            continue

        print(f"\n⚠️  [경고 발생 시각] {timestamp_str} ⚠️")
        for row in warnings:
            robot_id = row['robotId']
            battery = row['batteryLevel']
            temp = row['liftMtrTemp']

            details = []
            if battery <= 20:
                details.append(f"배터리 용량: {battery}%")
            if temp >= 70:
                details.append(f"모터 온도: {temp}°C")

            print(f"  - AMR {robot_id} ▶ " + ", ".join(details))

        time.sleep(10)
