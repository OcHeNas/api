from fastapi import Depends, Request, HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UserDAO
from app.users.models import Users
# Получение токена
def get_token(request: Request):
       token = request.cookies.get("my_access_token")
       if not token:
          raise TokenAbsentException
       return token
# Получение пользователя
async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UserDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user
# Проверка прав пользователя
async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    if current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user