from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        ## TODO
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            # not None으로 받으면 데이터베이스에 해당 user가 없다.
            raise ValueError("User not Found.")
        if user.password != user_login.password:
            # 데이터베이스에 있는 비번과 우리가 입력한 비번이 다르면
            raise ValueError("Invalid ID/PW")
        return user
        
    def register_user(self, new_user: User) -> User:
        ## TODO
        if self.repo.get_user_by_email(new_user.email):
            # None을 반환하지 않으면 이미 데이터베이스에 해당 email이 있다.
            raise ValueError("User already Exists.")
        # Error로 안빠지면 해당 유저 저장
        new_user = self.repo.save_user(new_user)
        return new_user

    def delete_user(self, email: str) -> User:
        ## TODO        
        deleted_user = self.repo.get_user_by_email(email)
        if not deleted_user:
            # 받은값이 not None이면 데베에 해당 user가 없다.
            raise ValueError("User not Found.")
        # 있으면 해당 유저 반환해서 삭제
        deleted_user = self.repo.delete_user(deleted_user)
        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        ## TODO
        updated_user = self.repo.get_user_by_email(user_update.email)
        if not updated_user:
            raise ValueError("User not Found.")
        updated_user.password = user_update.new_password
        updated_user = self.repo.save_user(updated_user)
        return updated_user
        