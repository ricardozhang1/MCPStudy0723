import httpx
from dataclasses import dataclass
from contextlib import asynccontextmanager

from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from rich import print as rprint
import json, os


@dataclass
# 初始化一个生命周期上下文
class AppContext:
    # historis用于存储请求历史
    histories: dict


@asynccontextmanager
async def app_lifespan(server):
    # 在MCP初始化时候执行
    histories = {}
    try:
        # 每次通信会把这个上下文通过参数传入给工具
        yield AppContext(histories=histories)
    finally:
        # 当MCP服务关闭时执行
        rprint(histories)

app = FastMCP(
    name='web-search',
    lifespan=app_lifespan
)

@app.tool()
# 第一个参数会被传入上下文对象
async def web_search(ctx: Context, query: str) -> str:
    """
    搜索互联网内容

    Args:
        query: 查询内容

    Returns:
        返回搜索结果
    """
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream(
            method="POST", 
            url='https://open.bigmodel.cn/api/paas/v4/tools', 
            headers={
                "Accept": "text/event-stream",
                'Authorization': os.getenv('ZHI_PU_API_KEY')
            },
            json={
                'tool': 'web-search-pro',
                'messages': [
                    {
                        'role': 'user',
                        'content': query
                    }
                ],
                'stream': True
            }
        ) as response:
            res_data = []
            async for line in response.aiter_lines():
                if line.startswith('data:'):
                    data = line.removeprefix('data:').strip()
                    # rprint(data)
                    if data != '[DONE]':
                        msg = json.loads(data)
                        for d in msg['choices']:
                            # rprint(f'd: {d}')
                            for k, v in d['delta'].items():
                                if k == 'tool_calls':
                                    # rprint(f'v: {v}')
                                    for c in v:
                                        g = c.get('search_result')
                                        if c and g is not None:
                                            # rprint(f'c: {c}')
                                            for m in g:
                                                # rprint(f'm: {m}')
                                                res_data.append(m.get('content'))
            return_data = '\n\n\n'.join(res_data)
            # 将查询值和返回值存到histories中
            ctx.request_context.lifespan_context.histories[query] = return_data
            return return_data
            

        
if __name__ == '__main__':
    app.run()