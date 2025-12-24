from sqlalchemy import create_engine,text

engine = create_engine(
    "mssql+pyodbc://sd:sd12345@WIN-746EJ365LOT\\SQL2019/EmployeeManagement"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

from  mcp.server.fastmcp import FastMCP

mcp = FastMCP('demoSqlTest')

@mcp.tool()
def db_tool(query:str) -> str:
    """
    Executes sql server query on sql server and returns result
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()

            if not rows:
                return "No rows returned"
            
            return "\n".join(str(row) for row in rows)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    mcp.run(transport='stdio')