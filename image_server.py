from mcp.server import FastMCP
import httpx


app = FastMCP('image_server')


@app.tool()
async def image_generation(image_prompt: set):
    """
    生成图片
    :params iamge_prompt: 图片描述，需要英文
    :return: 图片保存到的本地路径
    """

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


if __name__ == '__main__':
    app.run(transport='stdio')


