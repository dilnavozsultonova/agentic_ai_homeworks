import subprocess
from  mcp.server.fastmcp import FastMCP

mcp = FastMCP('demo')

# web server -> endpoints
# MCP server -> Tools

@mcp.tool()
def terminal(command:str) -> str:
    """
    Run a terminal command inside the workspace directory.
    It is windows operating system.So linux commands like 'ls','pwd' does not work.
    Args:
        command: the terminal command to run.
    Returns:
        the command output or an error message.
    """ 
    try:
        result = subprocess.run(command,shell=True,capture_output=True,
                                cwd="D:\Agentic_ai\output")
        if result is not None:
            try:
                return result.stdout.decode("utf-8")
            except Exception:
                return ''
    except Exception as e:
        return str(e)  

if __name__ == '__main__':
    print("Running...")
    mcp.run(transport='stdio')

