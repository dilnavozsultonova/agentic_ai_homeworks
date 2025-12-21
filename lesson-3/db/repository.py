import hashlib
from .engine import SessionLocal
from .models import User, ChatRoom, Message


class DB:
    def __init__(self):
        self.session = SessionLocal

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        session = self.session()
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
        session = self.session()
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
        session = self.session()
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
        session = self.session()
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
        session = self.session()
        try:
            room = ChatRoom(user_id=user_id, title=title)
            session.add(room)
            session.commit()
            return room.id
        finally:
            session.close()

    def get_user_chatrooms(self, user_id):
        session = self.session()
        try:
            return session.query(ChatRoom).filter_by(user_id=user_id).all()
        finally:
            session.close()

    def get_chatroom(self, room_id):
        session = self.session()
        try:
            return session.query(ChatRoom).filter_by(id=room_id).first()
        finally:
            session.close()