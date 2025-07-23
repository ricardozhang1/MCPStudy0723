import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from rich import print as rprint

# 为stdio连接创建客户端
server_params = StdioServerParameters(
    # 服务器执行的命令
    command='uv',
    # 运行的参数
    args = ['run', 'web_search.py']
    # 环境变量， 默认是None
    # env=None
)

async def example() -> None:
    # 创建sidio客户端
    async with stdio_client(server_params) as (stido, write):
        # 创建ClientSession对象
        async with ClientSession(stido, write) as session:
            # 初始化ClientSession
            await session.initialize()

            # 列出可用的工具
            response = await session.list_tools()
            rprint('[green]---------------------------------------[/green]')
            rprint(response)

            # 调用工具
            resp = await session.call_tool('web-search', {'query': '杭州今天天气'})
            rprint('[purple]---------------------------------------[/purple]')
            rprint(resp)

if __name__ == '__main__':
    asyncio.run(example())
