# 客户端
import asyncio

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from mcp.shared.context import RequestContext
from mcp.types import (
    TextContent,
    CreateMessageRequestParams,
    CreateMessageResult
)
from rich import print as rprint
from mcp.shared.memory import (
     create_connected_server_and_client_session as create_session
)

from file_server import app 

server_params = StdioServerParameters(
    command='uv',
    args=['run', 'file_server.py']
)

async def sampling_callback(content: RequestContext[ClientSession, None], params: CreateMessageRequestParams) -> CreateMessageResult:
    # 获取工具发送的消息并显示给用户
    input_message = input(params.messages[0].content.text)
    # 将用户的输入发送回工具
    return CreateMessageResult(
        role='user',
        content=TextContent(
            type='text',
            text=input_message.strip().upper() or 'Y'
        ),
        model='user-input',
        stopReason='endTurn'
    )

async def main() -> None:
    async with create_session (
         app._mcp_server,
         sampling_callback=sampling_callback
    ) as client_session:
    # async with stdio_client(server_params) as (stdio, write):
    #     async with ClientSession(
    #         stdio, write,
    #         # 设置sampling_callback对应方法
    #         sampling_callback=sampling_callback
    #     ) as session:
                # await session.initialize()
                
                res = await client_session.call_tool(
                    'delete_file',
                    {'file_path': r'D:\my\PythonApplicationTmps\MCP\mcp_client2\text.txt'}
                )
                # 获取工具后最后执行的返回结果
                rprint(f'[green] res: {res} [/green]')


if __name__ == '__main__':
     asyncio.run(main())

