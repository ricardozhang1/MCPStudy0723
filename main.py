import httpx
import os
import dotenv
from rich import print as rprint
import asyncio
import json

dotenv.load_dotenv()

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

async def main():
    print("Hello from mcp-client2!")
    # data = await testPost()
    # rprint(f'data: {data}')
    await pic_gen('there is  a bird which is green, cartoon and cute.')



async def testPost() -> str:
    rprint(os.getenv('ZHI_PU_API_KEY'))
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
                        'content': "深圳今天天气怎么样。"
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
            rprint(res_data)
            return "".join(res_data)

            
async def pic_gen(image_prompt: str):
    async with httpx.AsyncClient() as client:
        data = {'data': [image_prompt, 0, True, 512, 512, 3]}

        # 创建生成图片任务
        response1 = await client.stream(
            method='POST',
            url='https://black-forest-labs-flux-1-schnell.hf.space/call/infer',
            json=data,
            headers={"Content-Type": "application/json"}
        )

        # 解析响应获取事件ID
        rprint(f'[green]{response1}[/green]')



if __name__ == "__main__":
    asyncio.run(main())
