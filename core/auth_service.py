"""
Sarasai - Authentication Service
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
import json
import os
from pathlib import Path

class AuthService:
    """Simple file-based authentication service"""
    
    def __init__(self):
        self.secret_key = "sarasai_secret_key_2026"  # In production, use environment variable
        self.algorithm = "HS256"
        self.token_expiry = timedelta(days=7)  # Token expires in 7 days
        
        # Create users file if it doesn't exist
        self.users_file = Path("data/users.json")
        self.users_file.parent.mkdir(exist_ok=True)
        
        if not self.users_file.exists():
            self._create_initial_users()
    
    def _create_initial_users(self):
        """Create initial demo users"""
        initial_users = {
            "demo@sarasai.com": {
                "email": "demo@sarasai.com",
                "name": "Demo User",
                "password_hash": self._hash_password("demo123"),
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "subscription": "basic"
            },
            "admin@sarasai.com": {
                "email": "admin@sarasai.com", 
                "name": "Admin User",
                "password_hash": self._hash_password("admin123"),
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "subscription": "premium"
            }
        }
        
        with open(self.users_file, 'w') as f:
            json.dump(initial_users, f, indent=2)
    
    def _load_users(self) -> Dict:
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
    
    def register(self, email: str, name: str, password: str) -> Dict:
        """Register a new user"""
        users = self._load_users()
        
        if email in users:
            return {"success": False, "message": "User already exists"}
        
        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}
        
        users[email] = {
            "email": email,
            "name": name,
            "password_hash": self._hash_password(password),
            "created_at": datetime.now().isoformat(),
            "is_active": True,
            "subscription": "basic"
        }
        
        self._save_users(users)
        
        # Generate token
        token = self._generate_token(email)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "token": token,
            "user": {
                "email": email,
                "name": name,
                "subscription": "basic"
            }
        }
    
    def login(self, email: str, password: str) -> Dict:
        """Login user"""
        users = self._load_users()
        
        if email not in users:
            return {"success": False, "message": "Invalid email or password"}
        
        user = users[email]
        
        if not user.get("is_active", True):
            return {"success": False, "message": "Account is deactivated"}
        
        if not self._verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid email or password"}
        
        # Generate token
        token = self._generate_token(email)
        
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "email": user["email"],
                "name": user["name"],
                "subscription": user.get("subscription", "basic")
            }
        }
    
    def _generate_token(self, email: str) -> str:
        """Generate JWT token"""
        payload = {
            "email": email,
            "exp": datetime.utcnow() + self.token_expiry,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email = payload.get("email")
            
            users = self._load_users()
            if email in users and users[email].get("is_active", True):
                user = users[email]
                return {
                    "email": user["email"],
                    "name": user["name"],
                    "subscription": user.get("subscription", "basic")
                }
            
            return None
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an existing token"""
        user_info = self.verify_token(token)
        if user_info:
            return self._generate_token(user_info["email"])
        return None
    
    def get_user_portfolio(self, email: str) -> Optional[Dict]:
        """Get user's saved portfolio"""
        portfolio_file = Path(f"data/portfolios/{email.replace('@', '_at_').replace('.', '_')}.json")
        
        if portfolio_file.exists():
            try:
                with open(portfolio_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def save_user_portfolio(self, email: str, portfolio_data: Dict) -> bool:
        """Save user's portfolio"""
        try:
            portfolio_dir = Path("data/portfolios")
            portfolio_dir.mkdir(exist_ok=True)
            
            portfolio_file = portfolio_dir / f"{email.replace('@', '_at_').replace('.', '_')}.json"
            
            portfolio_data["updated_at"] = datetime.now().isoformat()
            
            with open(portfolio_file, 'w') as f:
                json.dump(portfolio_data, f, indent=2)
            
            return True
        except:
            return False

# Singleton instance
auth_service = AuthService()