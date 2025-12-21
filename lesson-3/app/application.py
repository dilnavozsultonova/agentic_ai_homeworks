import sys
from getpass import getpass
from db.repository import DB
from agent.agent import Agent


class Application:
    def __init__(self):
        self.db = DB()
        self.commands = {
            0: self.show_menu,
            1: self.register,
            2: self.login,
            3: self.select_chatroom_menu,  
            4: sys.exit,
        }
        self.agent = None
        self.current_user = None
        self.current_room = None
        self.menu = """Menu:
        0.Show Menu
        1.Register
        2.Login
        3.Select chatroom
        4.Exit
"""

    def show_menu(self):
        print(self.menu)

    def register(self, username=None):
        if not username:
            username = input("Username: ")

        password1 = getpass("Password: ")
        password2 = getpass("Password (again): ")

        if password1 != password2:
            print("Passwords do not match.")
            return

        self.db.register(username=username, password=password1)

    def login(self):
        username = input("Username: ")
        password = getpass("Password: ")

        user_id = self.db.login(username=username, password=password)
        if not user_id:
            return

        self.current_user = user_id
        room_id = self.db.create_chatroom(user_id, "Default Chat")
        self.current_room = room_id
        self.agent = Agent(room_id,self.db)

        print("Logged in. Type messages (type 'exit' to stop).")
        self.chat_loop()

    def chat_loop(self):
        if not self.agent:
            print("No chatroom selected.")
            return

        while True:
            msg = input("You: ")
            if msg.lower() == "exit":
                break

            reply = self.agent.ask(msg)
            print("AI:", reply)

    def select_chatroom_menu(self):
        if not self.current_user:
            print("Please login first.")
            return

        rooms = self.db.get_user_chatrooms(self.current_user)
        if not rooms:
            print("No chatrooms found. Creating a new one.")
            self.create_chatroom()
            return

        print("Your chatrooms:")
        for r in rooms:
            print(f"{r.id}: {r.title}")

        room_id = input("Enter chatroom ID (or press Enter to create new): ")
        if room_id.strip() == "":
            self.create_chatroom()
        else:
            self.select_chatroom(int(room_id))

    def select_chatroom(self, room_id):
        room = self.db.get_chatroom(room_id)
        if not room:
            print("Chatroom not found.")
            return

        if room.user_id != self.current_user:
            print("Access denied.")
            return

        self.current_room = room_id
        self.agent = Agent(room_id,self.db)
        print(f"Switched to chatroom: {room.title}")

    def create_chatroom(self):
        title = input("Chatroom title: ")
        room_id = self.db.create_chatroom(self.current_user, title)
        self.current_room = room_id
        self.agent = Agent(room_id,self.db)
        print(f"Chatroom '{title}' created and selected.")

    def run(self):
        self.show_menu()
        while True:
            try:
                command_id = int(input("Command ID: "))
                self.commands[command_id]()
            except Exception as e:
                print("ERROR:", e)
