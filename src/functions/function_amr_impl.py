from db.sql_connection import get_connection

current_time = None 

def get_current_amr_location(robot_id):
    if current_time is None:
        return "시뮬레이션이 아직 시작되지 않았습니다."

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT nodeCode, nodeLabel, nodeNumber, x, y FROM amr_status
        WHERE robotId = %s AND timestamp = %s
    """, (robot_id, current_time))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return {
            "robot_id": robot_id,
            "nodeCode": row["nodeCode"],
            "nodeLabel": row["nodeLabel"],
            "nodeNumber": row["nodeNumber"],
            "x": row["x"],
            "y": row["y"],
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        return f"AMR {robot_id}의 위치 정보를 찾을 수 없습니다."
