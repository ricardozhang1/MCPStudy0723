from mcp.server import FastMCP

app = FastMCP('prompt_and_resources')

@app.prompt('翻译专家')
async def transport_export(target_language: str = 'Chinese') -> str:
    return f'你是一个翻译专家，擅长将任何语言翻译成{target_language}。请翻译以下内容：'


@app.resource('echo://static')
async def echo_resource() -> str:
    """
    返回静态资源
    """
    # 返回的是 当用户使用这个资源时候，资源的内容
    return 'Echo!'

@app.resource('greeting://{name}')
async def get_greeting(name: str) -> str:
    """
    问候语句
    Args:
        name: str 问候的对象
    Return:
        问候语句
    """
    return f'Hello, {name}'

if __name__ == '__main__':
    app.run(transport='stdio')