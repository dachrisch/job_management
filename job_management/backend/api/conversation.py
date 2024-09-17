from __future__ import annotations

import json
from datetime import datetime
from functools import reduce
from typing import Literal, List, Dict, Any, Callable, Awaitable

import requests
from attr import define
from openai import OpenAI, AsyncOpenAI
from openai.types import ChatModel
from openai.types.chat import ChatCompletionMessageParam


@define
class Usage:
    context_tokens: int
    generated_tokens: int
    model: ChatModel

    model_costs: Dict[ChatModel, Dict[Literal['generated', 'context'], int]] = {
        'gpt-4o-mini': {'generated': 0.0000006, 'context': 0.00000015}}

    @property
    def generated_costs(self) -> int:
        return self.generated_tokens * self.model_costs[self.model]['generated']

    @property
    def context_costs(self) -> int:
        return self.context_tokens * self.model_costs[self.model]['context']


class Conversation:
    def __init__(self, openai_api_key: str, model: ChatModel = "gpt-4o-mini",
                 response_format: Literal["text", "json_object"] = "json_object"):
        self.messages: List[ChatCompletionMessageParam] = []
        self.response_format = response_format
        self.model = model
        self.openai_api_key = openai_api_key

        self.processor: Dict[Literal["text", "json_object"], Callable[[str], Any]] = {
            'text': lambda x: x,
            'json_object': json.loads
        }

    def as_system(self, system_prompt: str) -> Conversation:
        self.messages.append({
            "role": "system",
            "content": system_prompt,
        })
        return self

    def as_user(self, user_prompt: str) -> Conversation:
        self.messages.append({
            "role": "user",
            "content": user_prompt,
        })
        return self

    async def complete_async(self) -> Dict[str, Any]:
        client = AsyncOpenAI(api_key=self.openai_api_key)
        chat_completion = await client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            response_format={"type": self.response_format},
        )
        return self.processor[self.response_format](chat_completion.choices[0].message.content)

    def complete(self) -> Dict[str, Any]:
        client = OpenAI(api_key=self.openai_api_key)
        chat_completion = client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            response_format={"type": self.response_format},
        )
        return self.processor[self.response_format](chat_completion.choices[0].message.content)

    def usage(self, date: datetime) -> Usage:
        usage_response = requests.get('https://api.openai.com/v1/usage',
                                      headers={'Authorization': f'Bearer {self.openai_api_key}'},
                                      params={'date': date.strftime('%Y-%m-%d')})
        if 429 == usage_response.status_code:
            context_tokens, generated_tokens = (0, 0)
        else:
            context_tokens = reduce(lambda total, entry: total + entry['n_context_tokens_total'],
                                    usage_response.json()['data'], 0)
            generated_tokens = reduce(lambda total, entry: total + entry['n_generated_tokens_total'],
                                      usage_response.json()['data'], 0)
        return Usage(context_tokens=context_tokens, generated_tokens=generated_tokens, model=self.model)

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model}, messages={self.messages})"
