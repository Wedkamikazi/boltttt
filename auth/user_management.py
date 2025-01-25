import json
import hashlib
import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Set
from pathlib import Path

class UserRole(Enum):
    USER = "User"
    MANAGER = "Manager"
    ADMIN = "Admin"

class User:
    def __init__(self, username: str, role: UserRole, password_hash: str, remember_token: str = None):
        self.username = username
        self.role = role
        self.password_hash = password_hash
        self.last_login = None
        self.remember_token = remember_token

class UserManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.users_file = self.data_dir / "users.json"
        self.active_sessions: Dict[str, User] = {}
        self.users = {}
        self._ensure_data_directory()
        self._load_users()
        
        # Role permissions
        self.role_permissions = {
            UserRole.ADMIN: {
                'permissions': {'create_user', 'delete_user', 'view_all', 'approve_payment'},
                'resources': {'user_data', 'payment_data', 'status_data'}
            },
            UserRole.MANAGER: {
                'permissions': {'view_all', 'approve_payment'},
                'resources': {'payment_data', 'status_data'}
            },
            UserRole.USER: {
                'permissions': {'view_assigned', 'create_payment'},
                'resources': {'payment_data'}
            }
        }
        
        # Create default admin if no users exist
        if not self.users:
            self._create_default_admin()

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.users_file.exists():
            with open(self.users_file, "w", encoding='utf-8') as f:
                json.dump({}, f, indent=4)

    def _load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, "r", encoding='utf-8') as f:
                self.users = json.load(f)
        except Exception:
            self.users = {}

    def _save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, "w", encoding='utf-8') as f:
            json.dump(self.users, f, indent=4)

    def _create_default_admin(self):
        """Create default admin account"""
        admin_data = {
            "username": "admin",
            "role": UserRole.ADMIN.value,
            "password_hash": self._hash_password("admin123"),
            "last_login": None,
            "remember_token": None
        }
        self.users["admin"] = admin_data
        self._save_users()

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        return self._hash_password(password) == stored_hash

    def _generate_token(self) -> str:
        """Generate a secure remember-me token"""
        return secrets.token_urlsafe(32)

    def authenticate(self, username: str, password: str, remember: bool = False) -> Optional[User]:
        """Authenticate a user with username and password"""
        try:
            if username in self.users:
                stored_hash = self.users[username]['password_hash']
                if self._verify_password(password, stored_hash):
                    # Update last login and remember token
                    self.users[username]['last_login'] = datetime.now().isoformat()
                    if remember:
                        self.users[username]['remember_token'] = self._generate_token()
                    else:
                        self.users[username]['remember_token'] = None
                    
                    # Save changes
                    self._save_users()
                    
                    # Return user object
                    return User(
                        username=username,
                        role=UserRole(self.users[username]['role']),
                        password_hash=self.users[username]['password_hash'],
                        remember_token=self.users[username]['remember_token']
                    )
        except Exception as e:
            print(f"Authentication error: {e}")
        return None

    def validate_session(self, username: str, token: str) -> Optional[User]:
        """Validate a user's session using their remember-me token"""
        try:
            if (username in self.users and 
                self.users[username]['remember_token'] is not None and 
                self.users[username]['remember_token'] == token):
                
                # Update last login time
                self.users[username]['last_login'] = datetime.now().isoformat()
                self._save_users()
                
                return User(
                    username=username,
                    role=UserRole(self.users[username]['role']),
                    password_hash=self.users[username]['password_hash'],
                    remember_token=token
                )
        except Exception as e:
            print(f"Session validation error: {e}")
        return None

    def logout(self, username: str):
        """Log out a user by removing their session token"""
        try:
            if username in self.users:
                self.users[username]['remember_token'] = None
                self.users[username]['last_login'] = None
                
                self._save_users()
                return True
        except:
            pass
        return False

    def get_all_users(self) -> dict:
        """Get all users"""
        try:
            with open(self.users_file, "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
            
    def create_user(self, username: str, password: str, role: UserRole):
        """Create a new user"""
        if username in self.users:
            raise ValueError(f"User {username} already exists")
            
        self.users[username] = {
            'password_hash': self._hash_password(password),
            'role': role.value,
            'last_login': None,
            'remember_token': None
        }
        
        self._save_users()
            
    def update_user(self, username: str, password: str = None, role: UserRole = None):
        """Update user details"""
        if username not in self.users:
            raise ValueError(f"User {username} does not exist")
            
        if password:
            self.users[username]['password_hash'] = self._hash_password(password)
            
        if role:
            self.users[username]['role'] = role.value
            
        self._save_users()
            
    def delete_user(self, username: str):
        """Delete a user"""
        if username not in self.users:
            raise ValueError(f"User {username} does not exist")
            
        del self.users[username]
        
        self._save_users()

    def change_password(self, username: str, new_password: str):
        """Change user's password"""
        if username in self.users:
            self.users[username]["password_hash"] = self._hash_password(new_password)
            self._save_users()

    def get_user_role(self, username: str) -> Optional[UserRole]:
        """Get user's role"""
        if username in self.users:
            return UserRole(self.users[username]["role"])
        return None
        
    def has_permission(self, username: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        try:
            if username not in self.users:
                return False
                
            role = UserRole(self.users[username]['role'])
            if role not in self.role_permissions:
                return False
                
            return permission in self.role_permissions[role]['permissions']
            
        except Exception as e:
            print(f"Permission check error: {e}")
            return False
            
    def can_access_resource(self, username: str, resource: str) -> bool:
        """Check if user can access a specific resource"""
        try:
            if username not in self.users:
                return False
                
            role = UserRole(self.users[username]['role'])
            if role not in self.role_permissions:
                return False
                
            return resource in self.role_permissions[role]['resources']
            
        except Exception as e:
            print(f"Resource access check error: {e}")
            return False
