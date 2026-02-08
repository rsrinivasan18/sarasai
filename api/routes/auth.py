"""
Sarasai - Authentication Routes
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    email: str
    name: str
    subscription: str

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user from JWT token"""
    token = credentials.credentials
    user = auth_service.verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest):
    """Register a new user"""
    result = auth_service.register(request.email, request.name, request.password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return TokenResponse(
        access_token=result["token"],
        token_type="bearer",
        user=result["user"]
    )

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """Login user"""
    result = auth_service.login(request.email, request.password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    return TokenResponse(
        access_token=result["token"],
        token_type="bearer",
        user=result["user"]
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@router.post("/refresh")
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token"""
    token = credentials.credentials
    new_token = auth_service.refresh_token(token)
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {"access_token": new_token, "token_type": "bearer"}

@router.get("/portfolio")
def get_user_portfolio(current_user: dict = Depends(get_current_user)):
    """Get user's saved portfolio"""
    portfolio = auth_service.get_user_portfolio(current_user["email"])
    
    if not portfolio:
        return {"holdings": [], "message": "No saved portfolio"}
    
    return portfolio

@router.post("/portfolio")
def save_user_portfolio(portfolio_data: dict, current_user: dict = Depends(get_current_user)):
    """Save user's portfolio"""
    success = auth_service.save_user_portfolio(current_user["email"], portfolio_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save portfolio"
        )
    
    return {"message": "Portfolio saved successfully"}