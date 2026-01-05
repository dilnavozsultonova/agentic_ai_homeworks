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
                "You are an assistant connected to a PRIVATE company database. "
                "You MUST use ONLY the provided tools if you are asked about employees "
                "Do NOT use any built-in SQL or database tools. "
                "All employee and salary data MUST come from the provided tools."
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
        # print("RAW PARTS:", response.candidates[0].content.parts)

        # function_call = None

        # for part in response.candidates[0].content.parts:
        #     if part.function_call:
        #         function_call = part.function_call
        #         break

        # if function_call:
        #     tool_name = function_call.name
        #     tool_args = function_call.args or {}

        #     result = self.tool_handlers[tool_name](tool_args)

        #     response = self.chat.send_message(
        #         types.FunctionResponse(
        #             name=tool_name,
        #             response=result
        #         )
        #     

        answer = response.text
        self.db.save_message(self.room_id, "assistant", answer)

        return answer 