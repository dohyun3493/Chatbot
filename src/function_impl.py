#Function calling 함수 정의된 파일

#현재 함수는 정의하지 않음
def get_production_summary(start_date, end_date):
    # 실제 query 결과값이 return에 들어간다고 가정.
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_completed": 1234
    }

def get_amr_status_by_node():
    return {
        "A지점": 2,
        "B지점": 1
    }