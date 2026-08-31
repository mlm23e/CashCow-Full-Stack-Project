from collections.abc import AsyncGenerator

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import User, UserRole

from app.security import decode_access_token

# this is a fastAPI dependency that provides an async database session to any route that needs it
async def get_db()-> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

"""
What is yield and why are we using it? Yield basically can be considered like a try-with-resources statement from Java

When a method requires this, it will call get_db which will return the session, then the operations get executed and then after the other function is 
finished, it returns here and completes this method, which just means it closes the session
"""

# We need to create a dependency that will extract the current user from the JWT access token 
# provided in the authorization header of the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Create a dependency that will extract the current user from the JWT access token
async def get_current_user(
        token : str = Depends(oauth2_scheme),
        db : AsyncSession = Depends(get_db)
)-> User:
    # we will be using the decode_access_token function to decode the token and 
    # extract the username from the payload
    # we also want to catch any exceptions that might occur during the decode process, 
    # such as an invalid token or missing username
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        payload = decode_access_token(token)
        username = payload.get("sub") 
        # note that sub is the standard claim name for the subject of the token, which, in our case, is the username
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    # finally, we can query the database for the user with the extracted username
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

# we need a dependency that will check if the current user has the required role(s) 
# necessary to access a particular route

# * operator allows us to pass in multiple roles

# could modify this function to put everything from role_checker inside require_role so long as you add 
# "async def" to the method signature along with the current_user parameter
def require_role(*allowed_role : UserRole):
    async def role_checker(current_user : User = Depends(get_current_user))-> User:
        if current_user.role not in allowed_role:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail=(f"Role {current_user.role.value} is not permitted to perform this action")
            )
        return current_user
    return role_checker
