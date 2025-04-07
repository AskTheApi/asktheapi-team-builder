from openai import AsyncOpenAI
import os


class OpenAIService():
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=os.environ['OPENAI_API_KEY'],
            base_url=os.environ['OPENAI_BASE_URL']
            )
    
    async def completion_with_headers(self, model, messages, stream: bool, headers: dict):
        return await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            extra_headers=headers,
            response_format={
                'type': 'json_object'
            }
        )