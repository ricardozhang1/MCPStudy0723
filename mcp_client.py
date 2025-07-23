import json
import asyncio
import os
import sys
from rich import print as rprint
from dataclasses import dataclass, field
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from openai import AsyncOpenAI
from mcp.client.stdio import stdio_client
from openai.types.chat import (
   ChatCompletionSystemMessageParam,
   ChatCompletionUserMessageParam,
   ChatCompletionToolParam
)
import dotenv

dotenv.load_dotenv()

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

@dataclass
class MCPClient:
    session: Optional[ClientSession] = field(default_factory=list)
    exit_stack: AsyncExitStack = AsyncExitStack()
    client: AsyncOpenAI = field(init=False)

    def __post_init__(self):
        self.client = AsyncOpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command='uv',
            args=['run', 'web_search.py'],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        await self.session.initialize()

    async def process_query(self, query: str = "") -> str:
        """
        这里需要通过system prompt来约束一下大语言模型
        """
        system_prompt = (
            '你是一个乐于助人的助手。'
            '你具备在线搜索的功能。'
            '在回答问题之前，请务必调用 web_search 工具进行互联网搜索。'
            '请在搜索时不要丢失用户的问题信息，尽量保持问题内容的完整性。'
            '在调用名为 "web_search" 的工具时，请确保传入参数名为 "query"，'
            '它应当是用户的问题内容，且是一个字符串。'
            '例如：{ "query": "今天天气如何？" }'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
            # ChatCompletionSystemMessageParam(role="system", content=system_prompt),
            # ChatCompletionUserMessageParam(role="user", content=query)
        ]

        # 获取所有的mcp服务器 工具列表信息
        response = await self.session.list_tools()
        rprint(f"[blue]Available tools: {response.tools}[/blue]")

        # 生成function_call的描述信息
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]

        rprint(f"[green]Available tools: {available_tools}[/green]")

        # 请求大模型，function call的描述信息通过tools参数传入
        resp = await self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            tools=available_tools
        )

        rprint(f"[yellow]Response: {resp}[/yellow]")

        # 处理返回的内容
        content = resp.choices[0]
        rprint(f"\n\n[purple][Model response: {content}][/purple]")
        if content.finish_reason == 'tool_calls':
            # 如果是需要使用工具的，就解析工具
            tool_call = content.message.tool_calls[0]
            rprint(f'[white]tool_call:  {tool_call}[/white]')
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            rprint(f'-------------{tool_name} {tool_args}----------')

            # 执行工具
            result = await self.session.call_tool(tool_name, tool_args)
            rprint(f"[red][Calling tool {result}][/red]")

            # 将大语言模型返回的调用哪个工具和执行完成后的数据都存入message中
            messages.append({
                'role': 'assistant',
                'content': None,
                'tool_calls': [
                    {
                        'id': tool_call.id,
                        'type': 'function',
                        'function': {
                            'name': tool_name,
                            'arguments': tool_call.function.arguments
                        }
                    }
                ]
            })
            messages.append({
                'role': 'tool',
                'content': result.content[0].text,
                'tool_call_id': tool_call.id,
                'name': tool_name
            })

            rprint(f"[cyan]Messages after tool call: {messages}[/cyan]")

            # 将上面的结果再返回给大语言模型 用于产生最终的结果
            respData = await self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
                stream=False,
            )

            rprint(f"[magenta]Final response: {respData}[/magenta]")

            return respData.choices[0].message.content
        
        return content.message.content
    
    async def chat_loop(self) -> None:
        while True:
            try:
                query = input("\nQuery:").strip()
                if query.lower() == 'quit':
                    break
                resp = await self.process_query(query=query)
                rprint('\n' + resp)

            except Exception as e:
                import traceback
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resource"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
