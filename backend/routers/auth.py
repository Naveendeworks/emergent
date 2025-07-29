from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.auth import LoginRequest, LoginResponse, TokenData
from services.auth_service import AuthService
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

def get_auth_service() -> AuthService:
    return AuthService()

@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with admin credentials"""
    try:
        # Authenticate user
        if not auth_service.authenticate_user(login_request.username, login_request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=480)  # 8 hours
        access_token = auth_service.create_access_token(
            data={"sub": login_request.username}, 
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            username=login_request.username
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify JWT token"""
    try:
        username = auth_service.verify_token(credentials.credentials)
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"username": username, "valid": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_token endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Token verification failed")

# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> str:
    """Get current authenticated user"""
    username = auth_service.verify_token(credentials.credentials)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username