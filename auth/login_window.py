import tkinter as tk
from tkinter import ttk, messagebox
from .user_management import UserManager, UserRole
import json
from pathlib import Path

class LoginWindow:
    def __init__(self, parent):
        self.parent = parent
        self.user_manager = UserManager()
        
        # Create login frame
        self.frame = ttk.Frame(parent.root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Set data paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.credentials_file = self.data_dir / "credentials.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar()
        
        self.create_widgets()
        self.load_saved_credentials()
        
    def create_widgets(self):
        """Create login form widgets"""
        # Title
        title_label = ttk.Label(self.frame, text="Payment Processing System", 
                              font=("TkDefaultFont", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Username
        username_frame = ttk.Frame(self.frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Username:").pack(side=tk.LEFT)
        username_entry = ttk.Entry(username_frame, textvariable=self.username_var)
        username_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        # Password
        password_frame = ttk.Frame(self.frame)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="Password:").pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                      show="*")
        self.password_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Remember me
        ttk.Checkbutton(self.frame, text="Remember Me", 
                       variable=self.remember_var).pack(pady=10)
        
        # Login button
        login_btn = ttk.Button(self.frame, text="Login", 
                             command=self.login)
        login_btn.pack(pady=10)
        
        # Status message
        self.status_label = ttk.Label(self.frame, text="")
        self.status_label.pack(pady=10)
        
        # Set initial focus
        username_entry.focus()
        
    def login(self):
        """Handle login attempt"""
        username = self.username_var.get()
        password = self.password_var.get()
        remember = self.remember_var.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter both username and password", 
                                   foreground="red")
            return
            
        user = self.user_manager.authenticate(username, password, remember)
        if user:
            if remember:
                self.save_credentials(username, user.remember_token)
            self.parent.on_login_success(user)
        else:
            self.status_label.config(text="Invalid username or password", 
                                   foreground="red")
            
    def save_credentials(self, username, token):
        """Save credentials to file"""
        try:
            creds = {
                "username": username,
                "token": token
            }
            with open(self.credentials_file, "w", encoding='utf-8') as f:
                json.dump(creds, f, indent=4)
        except Exception as e:
            print(f"Error saving credentials: {e}")
            
    def load_saved_credentials(self):
        """Load saved credentials if they exist"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, "r", encoding='utf-8') as f:
                    creds = json.load(f)
                    if "username" in creds and "token" in creds:
                        # Set the username in the form
                        self.username_var.set(creds["username"])
                        # Check the remember me box
                        self.remember_var.set(True)
                        # Try to auto-login
                        user = self.user_manager.validate_session(creds["username"], creds["token"])
                        if user:
                            self.parent.on_login_success(user)
        except Exception as e:
            print(f"Error loading credentials: {e}")
