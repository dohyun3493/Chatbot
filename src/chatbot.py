from openai import OpenAI
from config import Config
from prompts import FUNCTION_SYSTEM_MSG, GENERAL_SYSTEM_MSG, NLG_SYSTEM_MSG, NLG_USER_TEMPLATE
from functions_def import function_definitions as functions
import function_impl
import json

client = OpenAI(api_key=Config.OPENAI_API_KEY)

# GPT 호출 함수 (FunctionCalling 포함)
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

# 유니티에 올릴 때는 while 무한루프 돌리면 안된다.. 
def run_chat():
    while True:
        message = input("질문하세요 (종료: exit): ")
        if message.strip().lower() == "exit":
            break

        result = ask_function_call(FUNCTION_SYSTEM_MSG, message)

        if result.function_call:
            fn = result.function_call.name
            args = json.loads(result.function_call.arguments)
            try:
                func = getattr(function_impl, fn)
                raw_data = func(**args) if args else func()

                # 자연어 응답 생성
                nlg_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": NLG_SYSTEM_MSG},
                        {"role": "user", "content": NLG_USER_TEMPLATE.format(question=message, data=json.dumps(raw_data, ensure_ascii=False))}
                    ]
                )
                print(nlg_response.choices[0].message.content.strip())
            except AttributeError:
                print(f"정의되지 않은 함수: {fn}")
        else:
            print("(일반 채팅)")
            print(ask_general_response(GENERAL_SYSTEM_MSG, message))