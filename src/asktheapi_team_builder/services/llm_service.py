from asktheapi_team_builder.services.open_ai_service import OpenAIService


class LLMService():
    def __init__(self, openai_service: OpenAIService, llm_headers: dict = {}):
        self.openai_service = openai_service
        self.llm_headers = llm_headers
    
    async def chat_completion(self, model, messages, stream):
        return await self.openai_service.completion_with_headers(
            model=model, messages=messages, stream=stream, headers=self.llm_headers)