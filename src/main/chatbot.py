from openai import OpenAI
from config.config import Config
from functions.prompts import (
    SQL_PROMPT_TEMPLATE, FUNCTION_SYSTEM_MSG,
    NLG_SYSTEM_MSG, NLG_USER_TEMPLATE, SQL_DETERMINATION_PROMPT
)
from functions.functions_base_def import function_definitions as functions
from functions import function_base_impl
from db.sql_connection import get_connection
from utils.json_encoder import JSONEncoder
import json
import os
import datetime

client = OpenAI(api_key=Config.OPENAI_API_KEY)

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "chat_history.json")
HISTORY_FILE = os.path.normpath(HISTORY_FILE)
MAX_HISTORY = 50

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
            if isinstance(history, list):
                return history
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-MAX_HISTORY:], f, ensure_ascii=False, indent=2)

def execute_sql_query_multi(query):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        results = []
        queries = [q.strip() for q in query.split(';') if q.strip()]
        for q in queries:
            cursor.execute(q)
            results.append(cursor.fetchall())
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        return f"데이터베이스 오류: {str(e)}"

def generate_nlg_response(question, raw_data, history=None):
    messages = []
    if history:
        messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "system", "content": NLG_SYSTEM_MSG})
    messages.append({"role": "user", "content": NLG_USER_TEMPLATE.format(
        question=question,
        data=json.dumps(raw_data, ensure_ascii=False, cls=JSONEncoder)
    )})

    nlg_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return nlg_response.choices[0].message.content.strip()

def determine_sql_usage(user_msg, history=None):
    messages = []
    if history:
        messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "system", "content": SQL_DETERMINATION_PROMPT})
    messages.append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.0,
    )
    result = response.choices[0].message.content.strip().lower()
    return result

def generate_sql_query(user_msg, history=None):
    messages = []
    if history:
        messages.extend(history[-MAX_HISTORY:])
    prompt = SQL_PROMPT_TEMPLATE.format(user_msg=user_msg)
    messages.append({"role": "system", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.2,
    )
    sql_query = response.choices[0].message.content.strip()
    return sql_query

def generate_sql_response(user_msg, history=None):
    sql_query = generate_sql_query(user_msg, history)
    queries = [q.strip() for q in sql_query.split(';') if q.strip()]
    for q in queries:
        if not q.lower().startswith("select"):
            return "SQL이 잘못됐습니다."

    result = execute_sql_query_multi(sql_query)

    if isinstance(result, str) and "데이터베이스 오류" in result:
        return result

    if result:
        combined_result = []
        for res in result:
            combined_result.extend(tuplelist_to_strlist(res))
        return generate_nlg_response(user_msg, combined_result, history)
    else:
        return "데이터가 없습니다."

def tuplelist_to_strlist(result):
    strlist = []
    for row in result:
        values = [
            val.strftime('%Y-%m-%d') if isinstance(val, datetime.date) else
            val.strftime('%H:%M:%S') if isinstance(val, datetime.time) else
            str(val)
            for val in row
        ]
        if len(values) == 1:
            strlist.append(values[0])
        else:
            strlist.append(", ".join(values))
    return strlist

def ask_function_call(system_msg, user_msg, history=None, temp=0.3):
    messages = []
    if history:
        messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=temp,
    )
    return response.choices[0].message

def process_user_message(message):
    history = load_history()
    history.append({"role": "user", "content": message})

    sql_usage = determine_sql_usage(message, history)

    if sql_usage == "true":
        try:
            sql_response = generate_sql_response(message, history)
            print(sql_response)
            history.append({"role": "assistant", "content": sql_response})
            save_history(history)
            return
        except Exception as e:
            print(f"SQL 처리 중 오류 발생: {e}")
            return

    try:
        result = ask_function_call(FUNCTION_SYSTEM_MSG, message, history)
        if result and result.function_call:
            fn = result.function_call.name
            args = json.loads(result.function_call.arguments)
            try:
                func = getattr(function_base_impl, fn)
                raw_data = func(**args) if args else func()

                if isinstance(raw_data, str) and os.path.isfile(raw_data):
                    print(raw_data)
                    history.append({"role": "assistant", "content": raw_data})
                else:
                    nlg_resp = generate_nlg_response(message, raw_data, history)
                    print(nlg_resp)
                    history.append({"role": "assistant", "content": nlg_resp})

                save_history(history)

            except AttributeError:
                print(f"정의되지 않은 함수: {fn}")
            except Exception as e:
                print(f"Function 호출 중 오류 발생: {e}")

    except Exception as e:
        print(f"Function 처리 중 오류 발생: {e}")

def run_chat():
    while True:
        message = input("질문하세요 (종료: exit): ")
        if message.strip().lower() == "exit":
            break
        process_user_message(message)
