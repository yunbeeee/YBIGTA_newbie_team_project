from fastapi import APIRouter, HTTPException, Depends, status
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.user.user_service import UserService
from app.dependencies import get_user_service
from app.responses.base_response import BaseResponse

user = APIRouter(prefix="/api/user")

@user.post("/login", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def login_user(user_login: UserLogin, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    try:
        user = service.login(user_login)
        return BaseResponse(status="success", data=user, message="Login Success.") 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(user: User, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    새로운 사용자 등록.

    Args:
        user (User): 등록할 사용자의 정보 (이메일, 비밀번호, 사용자명).
        service (UserService): UserService를 전달받음.

    Returns:
        BaseResponse[User]: 등록된 사용자 정보와 메시지를 반환.

    Raises:
        HTTPException: 이메일을 사용하는 사용자가 존재하는 경우 400 상태 코드와 함께 오류 메시지를 반환.
    """
    try:
        new_user = service.register_user(user)
        return BaseResponse(status="success", data=new_user, message="User registeration success.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(user_delete_request: UserDeleteRequest, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    이메일을 기반으로 사용자를 삭제.

    Args:
        user_delete_request (UserDeleteRequest): 삭제할 사용자의 이메일 정보.
        service (UserService): UserService를 전달받음.

    Returns:
        BaseResponse[User]: 삭제된 사용자 정보와 메시지를 반환.

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 상태 코드와 함께 오류 메시지를 반환.
    """
    try:
        deleted_user = service.delete_user(user_delete_request.email)
        return BaseResponse(status="success", data=deleted_user, message="User Deletion Success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    
@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(user_update: UserUpdate, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    사용자 비밀번호 업데이트.

    Args:
        user_update (UserUpdate): 업데이트할 이메일과 새로운 비밀번호 정보.
        service (UserService): UserService를 전달받음.

    Returns:
        BaseResponse[User]: 업데이트된 사용자 정보와 메시지를 반환.

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 상태 코드와 함께 오류 메시지를 반환.
    """
    try:
        updated_user = service.update_user_pwd(user_update)
        return BaseResponse(status="success", data=updated_user, message="User password update success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
