공장 자체 DB(데이터)를 활용한 공장용 챗봇  
OpenAI GPT API를 사용하여 사용자 질문을 이해하고, 공장 DB 스키마에 기반한 SQL 쿼리를 생성

전체적인 구조, 흐름도(방향성)

- 사용자 자연어 질문  
  ↓  
- LLM이 질문 분석 → SQL 생성  
  ↓  
- 실제 SQL DB에 쿼리 실행  
  ↓  
- 결과 반환 → LLM이 말로 포장  
  ↓  
- 최종 챗봇 응답 제공

**4/25 구조 변경**
연구원님이 주신 참고 자료를 통해 functon calling 방식으로 개발 방향성 변경

사용자 자연어 질문  
  ↓  
LLM이 질문 분석 → 적절한 함수 호출(여기서 SQL도 정의하면 될 듯)

openai function calling
https://platform.openai.com/docs/guides/function-calling?api-mode=responses
https://landing.sellease.io/post/function-call-enterprise-ai-agent-rag-limitations-overcome