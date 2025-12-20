import sys
from getpass import getpass
import hashlib
from google.genai import Client
from sqlalchemy import create_engine, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(".env")


engine = create_engine(
    "mssql+pyodbc://@WIN-746EJ365LOT/DBName"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    chatrooms = relationship("ChatRoom", back_populates="user")


class ChatRoom(Base):
    __tablename__ = "chatrooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    user = relationship("User", back_populates="chatrooms")
    messages = relationship("Message", back_populates="room")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("chatrooms.id"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    room = relationship("ChatRoom", back_populates="messages")


Base.metadata.create_all(engine)


class DB:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        session = self.Session()
        try:
            if session.query(User).filter_by(username=username).first():
                print("Username already exists.")
                return False

            user = User(
                username=username,
                password_hash=self._hash_password(password),
            )
            session.add(user)
            session.commit()
            print("User registered successfully")
            return True
        finally:
            session.close()

    def login(self, username, password):
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                print("User not found")
                return None
            if user.password_hash != self._hash_password(password):
                print("Password is incorrect")
                return None

            return user.id
        finally:
            session.close()

    def load_history(self, room_id, limit=5):
        session = self.Session()
        try:
            messages = (
                session.query(Message)
                .filter_by(room_id=room_id)
                .order_by(Message.created_at)
                .limit(limit)
                .all()
            )

            return [
                {"role": m.role, "content": m.content}
                for m in messages
            ]
        finally:
            session.close()

    def save_message(self, room_id, role, content):
        session = self.Session()
        try:
            msg = Message(
                room_id=room_id,
                role=role,
                content=content
            )
            session.add(msg)
            session.commit()
        finally:
            session.close()

    def create_chatroom(self, user_id, title):
        session = self.Session()
        try:
            room = ChatRoom(user_id=user_id, title=title)
            session.add(room)
            session.commit()
            return room.id
        finally:
            session.close()

    def get_user_chatrooms(self, user_id):
        session = self.Session()
        try:
            return session.query(ChatRoom).filter_by(user_id=user_id).all()
        finally:
            session.close()

    def get_chatroom(self, room_id):
        session = self.Session()
        try:
            return session.query(ChatRoom).filter_by(id=room_id).first()
        finally:
            session.close()


class Agent:
    def __init__(self, room_id):
        self.room_id = room_id
        self.client = Client()
        self.db = DB()
        history = self.db.load_history(room_id)
        self.chat = self.client.chats.create(
            model="gemini-3-flash-preview",
            history=history
        )

    def ask(self, message):
        self.db.save_message(self.room_id, "user", message)

        response = self.chat.send_message(message)
        answer = response.text

        self.db.save_message(self.room_id, "assistant", answer)
        return answer

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
        self.agent = Agent(room_id)

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
        self.agent = Agent(room_id)
        print(f"Switched to chatroom: {room.title}")

    def create_chatroom(self):
        title = input("Chatroom title: ")
        room_id = self.db.create_chatroom(self.current_user, title)
        self.current_room = room_id
        self.agent = Agent(room_id)
        print(f"Chatroom '{title}' created and selected.")

    def run(self):
        self.show_menu()
        while True:
            try:
                command_id = int(input("Command ID: "))
                self.commands[command_id]()
            except Exception:
                print("Invalid command.")

app = Application()
app.run()
