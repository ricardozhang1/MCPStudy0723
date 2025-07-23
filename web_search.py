# _*_ coding: utf8 _*_

import httpx
from mcp.server import FastMCP
import os
import dotenv
from rich import print as rprint
import json

dotenv.load_dotenv()

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

# 初始化
app = FastMCP(name="web_search")


@app.tool()
async def web_search(query: str) -> str:
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
            return "".join(res_data)


if __name__ == "__main__":
    app.run(transport="stdio")


