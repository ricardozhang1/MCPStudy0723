import asyncio
from pydantic import AnyUrl

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from rich import print as rprint

server_params = StdioServerParameters(
    command='uv',
    args=['run', 'prompts_server.py']
)


async def main() -> None:
    async with stdio_client(server=server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            await session.initialize()

            # 获取无通配符的资源列表
            res = await session.list_resources()
            rprint(f'[red]res: {res}[/red]')

            # 获取有通配符的资源列表（资源模版）
            res = await session.list_resource_templates()
            rprint(f'[yellow]res: {res}[/yellow]')

            # 读取资源，会匹配通配符
            res = await session.read_resource(AnyUrl('greeting://zhangsan'))
            rprint(f'[green]res: {res}[/green]')

            # 使用Prompt模版
            res = await session.get_prompt('翻译专家', arguments={'target_language': '西班牙语'})
            rprint(f'[purple]res: {res}[/purple]')



if __name__ == '__main__':
    asyncio.run(main())
