from google.genai import Client, types

from db.repositoryB import DB_B
from agent.tools import create_db_tools


class Agent:
    def __init__(self, room_id, db):
        """
        room_id : chatroom id
        db      : main DB instance (users, chat history)
        """
        self.room_id = room_id
        self.db = db                      
        self.db_b = DB_B()               

        self.client = Client()

 
        history = self.db.load_history(room_id)

        tools, self.tool_handlers = create_db_tools(self.db_b)

        self.config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=(
            "You are an assistant connected to a company database. "
            "Whenever the user asks about employees, salaries, payroll, "
            "or compensation, you MUST use the provided tools to get data "
            "from the database instead of answering from general knowledge."
        )
)

      
        self.chat = self.client.chats.create(
            model="gemini-3-flash-preview",
            config=self.config,
            history=history
        )

    def ask(self, message: str) -> str:
       
        self.db.save_message(self.room_id, "user", message)

        response = self.chat.send_message(message)

        
        # part = response.candidates[0].content

        
        answer = response

        
        self.db.save_message(self.room_id, "assistant", answer)

        return answer
