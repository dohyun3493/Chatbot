from openai import OpenAI
from config.config import Config
from functions.prompts import (
    SQL_PROMPT_TEMPLATE, GENERAL_SYSTEM_MSG, FUNCTION_SYSTEM_MSG,
    NLG_SYSTEM_MSG, NLG_USER_TEMPLATE, SQL_DETERMINATION_PROMPT
)
from functions.functions_base_def import function_definitions as functions
from functions import function_base_impl
from db.sql_connection import get_connection
from utils.json_encoder import JSONEncoder
import json

client = OpenAI(api_key=Config.OPENAI_API_KEY)

# 자연어 응답 생성 함수
def generate_nlg_response(question, raw_data):
    nlg_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": NLG_SYSTEM_MSG},
            {"role": "user", "content": NLG_USER_TEMPLATE.format(
                question=question,
                data=json.dumps(raw_data, ensure_ascii=False, cls=JSONEncoder)
            )}
        ]
    )
    return nlg_response.choices[0].message.content.strip()

# SQL 사용 여부 판단 함수
def determine_sql_usage(user_msg):
    prompt = SQL_DETERMINATION_PROMPT
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": user_msg}   
        ],
        temperature=0.0,
    )
    result = response.choices[0].message.content.strip()
    print(f"모델 응답: {result}")  # 실제 모델 응답 확인용
    # 예상 값인 'true' 또는 'false'로 변환
    return result.lower()


# SQL 쿼리 생성 함수
def generate_sql_query(user_msg):
    prompt = SQL_PROMPT_TEMPLATE.format(user_msg=user_msg)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

# SQL 실행 함수
def execute_sql_query(query):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return f"데이터베이스 오류: {str(e)}"

# SQL 응답 생성 함수
def generate_sql_response(user_msg):
    sql_query = generate_sql_query(user_msg)
    print(f"생성된 SQL 쿼리: {sql_query}")

    if not sql_query.lower().startswith("select"):
        return "SQL이 잘못됐습니다."

    result = execute_sql_query(sql_query)

    if isinstance(result, str) and "데이터베이스 오류" in result:
        return result

    if result:
        return generate_nlg_response(user_msg, result)
    else:
        return "데이터가 없습니다."

# GPT 호출 함수 (Function Calling 포함)
def ask_function_call(system_msg, user_msg, temp=0.3):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        functions=functions,
        function_call="auto",
        temperature=temp,
    )
    return response.choices[0].message

# 일반 질문 처리용 함수
def ask_general_response(system_msg, user_msg, temp=0.7):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=temp,
    )
    return response.choices[0].message.content.strip()

# 사용자 메시지 처리 함수
def process_user_message(message):
    # SQL 사용 여부 확인
    sql_usage = determine_sql_usage(message)
    print(f"SQL 사용 여부 판단 결과: {sql_usage}") 

    # SQL 사용 여부 확인이 'true'일 때만 SQL 응답 처리
    if sql_usage == "true":
        try:
            sql_response = generate_sql_response(message)
            print(f"(SQL 응답)\n{sql_response}")
            return
        except Exception as e:
            print(f"SQL 처리 중 오류 발생: {e}")
            return

    # Function Call 여부 확인
    try:
        result = ask_function_call(FUNCTION_SYSTEM_MSG, message)
        if result and result.function_call:
            fn = result.function_call.name
            args = json.loads(result.function_call.arguments)
            try:
                func = getattr(function_base_impl, fn)
                raw_data = func(**args) if args else func()
                print(f"(Function 호출 응답)\n{generate_nlg_response(message, raw_data)}")
            except AttributeError:
                print(f"정의되지 않은 함수: {fn}")
            except Exception as e:
                print(f"Function 호출 중 오류 발생: {e}")
        else:
            print("(일반 채팅)")
            print(ask_general_response(GENERAL_SYSTEM_MSG, message))
    except Exception as e:
        print(f"Function 처리 중 오류 발생: {e}")

# 메인 실행 함수
def run_chat():
    while True:
        message = input("질문하세요 (종료: exit): ")
        if message.strip().lower() == "exit":
            break
        process_user_message(message)