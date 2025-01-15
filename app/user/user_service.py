from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        """
        이메일, 비밀번호로 로그인 기능 수행.

        Args:
            user_login (UserLogin): 사용자의 로그인 정보(이메일, 비밀번호).

        Returns:
            User: 로그인에 성공한 사용자 객체.

        Raises:
            ValueError("User not Found."): 시스템에서 이메일을 찾을 수 없는 경우.
            ValueError("Invalid ID/PW"): 저장된 비밀번호와 제공된 비밀번호가 일치하지 않는 경우.
        """
        # 이메일로 사용자를 검색
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")  # 등록되지 않은 이메일
        
        # 비밀번호 확인
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")  # 비밀번호 불일치

        return user


    def register_user(self, new_user: User) -> User:
        """
        새로운 사용자를 시스템에 등록.

        Args:
            new_user (User): 등록할 사용자의 정보 (이메일, 비밀번호, 사용자명).

        Returns:
            User: 등록에 성공한 사용자 객체.

        Raises:
            ValueError: 등록에 사용할 이메일을 가진 사용자가 이미 존재하는 경우.
        """
        # 사용자가 이미 존재하는지 확인
        existing_user = self.repo.get_user_by_email(new_user.email)
        if existing_user:
            raise ValueError("User already Exists.")  # 이미 등록된 이메일

        # 새로운 사용자를 저장
        saved_user = self.repo.save_user(new_user)
        return saved_user


    def delete_user(self, email: str) -> User:
        """
        이메일을 기준으로 시스템에서 사용자를 삭제.

        Args:
            email (str): 삭제할 사용자의 이메일 주소.

        Returns:
            User: 삭제된 사용자 객체.

        Raises:
            ValueError: 제공된 이메일로 사용자를 찾을 수 없는 경우.
        """
        # 이메일로 사용자 검색
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("User not Found.")  # 사용자를 찾을 수 없음

        # 사용자 삭제 및 삭제된 사용자 객체 반환
        deleted_user = self.repo.delete_user(user)
        return deleted_user


    def update_user_pwd(self, user_update: UserUpdate) -> User:
        """
        이메일을 기준으로 비밀번호 업데이트.

        Args:
            user_update (UserUpdate): 이메일과 새로운 비밀번호 정보를 포함한 객체.

        Returns:
            User: 업데이트된 비밀번호를 가진 사용자 객체.

        Raises:
            ValueError: 제공된 이메일로 사용자를 찾을 수 없는 경우.
        """
        # 이메일로 사용자 검색
        user = self.repo.get_user_by_email(user_update.email)
        if not user:
            raise ValueError("User not Found.")  # 사용자를 찾을 수 없음

        # 사용자의 비밀번호 업데이트
        user.password = user_update.new_password
        updated_user = self.repo.save_user(user)  # 업데이트된 사용자 저장
        return updated_user
