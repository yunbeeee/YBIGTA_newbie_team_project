import json

from typing import Dict, Optional

from app.user.user_schema import User
from app.config import USER_DATA

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from database.mysql_connection import Base

class Userorm(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, unique=True, index=True)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    """
    def _load_users(self) -> Dict[str, Dict]:
        try:
            with open(USER_DATA, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError("File not found")
    """
            
    def get_user_by_email(self, email: str) -> Optional[Userorm]:
        user = self.db.query(Userorm).filter(Userorm.email == email).first()
        return user

    def save_user(self, user_data) -> Userorm:
        returned_user = self.get_user_by_email(user_data.email)

        if returned_user:
            returned_user.username = user_data.username
            returned_user.password = user_data.password
        else:
            new_user = Userorm(**user_data.model_dump())
            self.db.add(new_user)
            returned_user = new_user  

        self.db.commit()
        self.db.refresh(returned_user)
        return returned_user

    def delete_user(self, user_data) -> Userorm:
        returned_user = self.get_user_by_email(user_data.email)
        if returned_user:
            self.db.delete(returned_user)
            self.db.commit()
        return returned_user