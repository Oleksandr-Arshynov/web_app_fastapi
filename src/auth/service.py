import datetime
import jose.jwt
import fastapi
import fastapi.security
import passlib.context
import database
import src.posts.models

class Auth:
    HASH_CONTEXT = passlib.context.CryptContext(schemes=["bcrypt"])
    ALGORITM = "HS256"
    SECRET = "My secret key"
    oauth2_scheme = fastapi.security.OAuth2PasswordBearer("/auth/login")
    
    
    def verify_password(self, plain_password, hashed_password) -> bool:
        """Verify a plain password against a hashed password.

        Args:
        - plain_password (str): The plain text password.
        - hashed_password (str): The hashed password to compare against.
        Returns:
        - bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.HASH_CONTEXT.verify(plain_password, hashed_password)
    
    def get_password_hash(self, plain_password):
        """Generate a hashed password from a plain text password.

        Args:
        - plain_password (str): The plain text password to hash.

        Returns:
        - str: The hashed password.
        """
        return self.HASH_CONTEXT.hash(plain_password)
        
    
    async def create_access_token(self, payload: dict) -> str:
        """
        Create an access token with the specified payload.

        Args:
        - payload (dict): The payload to encode into the token.

        Returns:
        - str: The generated access token.
        """
        to_encode = payload.copy()
        to_encode.update({"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)})
        encoded_jwt = jose.jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITM)
        return encoded_jwt
    
    async def create_refresh_token(self, payload: dict) -> str:
        """
        Create a refresh token with the specified payload.

        Args:
        - payload (dict): The payload to encode into the token.

        Returns:
        - str: The generated refresh token.
        """
        to_encode = payload.copy()
        to_encode.update({"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)})
        encoded_jwt = jose.jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITM)
        return encoded_jwt
    
    async def get_current_user(self, token: str = fastapi.Depends(oauth2_scheme), db = fastapi.Depends(database.get_db)):
        """
        Get the current user based on the provided token.

        Args:
        - token (str): The JWT token containing user information.
        - db: Database dependency.

        Returns:
        - src.posts.models.User: The authenticated user.

        Raises:
        - HTTPException: If the token is invalid or the user cannot be found.
        """
        credentials_exception = fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jose.jwt.decode(token, self.SECRET, algorithms=[self.ALGORITM])
        except jose.ExpiredSignatureError:
            raise credentials_exception
        except jose.JWTError:
            raise credentials_exception
        
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        user = db.query(src.posts.models.User).filter(src.posts.models.User.username==email).first()
        if user is None:
            raise credentials_exception
        return user
    
    async def decode_refresh_token(self, token: str) -> str:
        """
        Decode a refresh token to extract the user's email.

        Args:
        - token (str): The JWT refresh token to decode.

        Returns:
        - str: The user's email extracted from the token.

        Raises:
        - HTTPException: If the token is expired or invalid.
        """
        try:
            payload = jose.jwt.decode(token, Auth.SECRET, algorithms=[Auth.ALGORITM])
            return payload.get("sub")
        except jose.ExpiredSignatureError:
            raise fastapi.HTTPException(status_code=401, detail="Token has expired")
        except (jose.JWTError, ValueError):
            raise fastapi.HTTPException(status_code=401, detail="Could not validate credentials")
    
    
    async def update_token(user: src.posts.models.User, token: str | None, db = fastapi.Depends(database.get_db)):
        """
        Update the refresh token for the specified user.

        Args:
        - user (src.posts.models.User): The user whose refresh token needs to be updated.
        - token (str | None): The new refresh token.
        - db: Database dependency.
        """
        user.refresh_token = token
        await db.commit()
    
        
        