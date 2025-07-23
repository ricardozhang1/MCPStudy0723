# 服务端
from mcp.server import FastMCP
from mcp.types import SamplingMessage, TextContent
import os
from rich import print as rprint

app = FastMCP('file_server')

@app.tool('delete_file')
async def delete_file(file_path: str):
    """
    删除指定文件夹下的文件

    Args:
        file_path: str 指定的文件路径
    Retuens:
        str 返回信息
    """
    # 创建SamplingMessage用于触发sample callback 函数
    message = [
        SamplingMessage(role='user', content=TextContent(
            type='text', text=f'是否删除文件：{file_path} (Y)'
        ))
    ]
    result = await app.get_context().session.create_message(messages=message, max_tokens=100)

    # 获取到sampling callback函数的返回值，并根据返回值进行处理
    if result.content.text == 'Y':
        rprint("[green]执行删除操作[/green]")
        os.remove(file_path)
        return f'文件 {file_path} 已经被删除！'
    

if __name__ == '__main__':
    app.run(transport='stdio')






