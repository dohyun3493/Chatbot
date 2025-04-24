from openai import OpenAI
from config import Config
from prompts import DB_SCHEMA, SQL_SYSTEM_MSG, GENERAL_SYSTEM_MSG

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def ask_gpt(system_msg, user_msg, temp=0.7):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=temp,
    )
    return response.choices[0].message.content.strip()

def run_chat():
    while True:
        message = input("질문하세요 (종료: exit): ")
        if message.strip().lower() == "exit":
            break

        #  일반 응답
        general_response = ask_gpt(GENERAL_SYSTEM_MSG, message)
        print("\nGPT의 일반 응답:")
        print(general_response)

        #  SQL 쿼리 생성
        sql_user_msg = f"{DB_SCHEMA}\n\n사용자 질문: {message}"
        sql_response = ask_gpt(SQL_SYSTEM_MSG, sql_user_msg, temp=0.3)
        print("\nGPT가 생성한 SQL 쿼리:")
        print(sql_response)
        print("-" * 100)
