import tkinter as tk
from tkinter import ttk, messagebox
from .user_management import UserManager, UserRole, User

class AdminPanel:
    def __init__(self, parent):
        self.parent = parent
        self.user_manager = parent.user_manager
        
        # Create admin window
        self.window = tk.Toplevel(parent.root)
        self.window.title("Admin Panel - User Management")
        self.window.geometry("800x600")  
        self.window.minsize(800, 600)    
        
        # Make it modal
        self.window.transient(parent.root)
        self.window.grab_set()
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.role_var = tk.StringVar(value=UserRole.USER.value)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_users())
        
        self.create_widgets()
        self.load_users()
        
        # Center the window
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """Create admin panel widgets"""
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Left panel - User List
        left_panel = ttk.LabelFrame(self.window, text="User List", padding="10")
        left_panel.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Configure left panel grid
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Search box
        search_frame = ttk.Frame(left_panel)
        search_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        ttk.Entry(search_frame, textvariable=self.search_var).grid(row=0, column=1, sticky='ew')
        
        # User list with scrollbar
        list_frame = ttk.Frame(left_panel)
        list_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.user_tree = ttk.Treeview(list_frame, columns=('Username', 'Role', 'Last Login'),
                                     show='headings', selectmode='browse')
        self.user_tree.grid(row=0, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.user_tree.heading('Username', text='Username')
        self.user_tree.heading('Role', text='Role')
        self.user_tree.heading('Last Login', text='Last Login')
        
        # Right panel - User Management
        right_panel = ttk.LabelFrame(self.window, text="User Management", padding="10")
        right_panel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Configure right panel grid
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Form fields
        ttk.Label(right_panel, text="Username:").grid(row=0, column=0, sticky='w', pady=(0, 2))
        ttk.Entry(right_panel, textvariable=self.username_var).grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(right_panel, text="Password:").grid(row=2, column=0, sticky='w', pady=(0, 2))
        ttk.Entry(right_panel, textvariable=self.password_var, show="*").grid(row=3, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(right_panel, text="Role:").grid(row=4, column=0, sticky='w', pady=(0, 2))
        role_combo = ttk.Combobox(right_panel, textvariable=self.role_var,
                                 values=[role.value for role in UserRole],
                                 state='readonly')
        role_combo.grid(row=5, column=0, sticky='ew', pady=(0, 20))
        
        # Action buttons
        ttk.Button(right_panel, text="Add New User",
                  command=self.add_user).grid(row=6, column=0, sticky='ew', pady=2)
        ttk.Button(right_panel, text="Update Selected User",
                  command=self.update_user).grid(row=7, column=0, sticky='ew', pady=2)
        ttk.Button(right_panel, text="Reset Password",
                  command=self.reset_password).grid(row=8, column=0, sticky='ew', pady=2)
        ttk.Button(right_panel, text="Delete User",
                  command=self.delete_user).grid(row=9, column=0, sticky='ew', pady=2)
        
        # Spacer
        ttk.Frame(right_panel).grid(row=10, column=0, sticky='ew', pady=10)
        
        # Close button
        ttk.Button(right_panel, text="Close",
                  command=self.window.destroy).grid(row=11, column=0, sticky='ew', pady=(0, 5))
        
        # Bind selection event
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
    def load_users(self):
        """Load users into the treeview"""
        # Clear existing items
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
            
        # Load users
        users = self.user_manager.get_all_users()
        for username, user_data in users.items():
            self.user_tree.insert('', 'end', values=(
                username,
                user_data['role'],
                user_data.get('last_login', 'Never')
            ))
            
    def filter_users(self):
        """Filter users based on search text"""
        search_text = self.search_var.get().lower()
        self.load_users()  # Reload all users
        
        if search_text:
            for item in self.user_tree.get_children():
                username = self.user_tree.item(item)['values'][0].lower()
                if search_text not in username:
                    self.user_tree.delete(item)
                    
    def on_user_select(self, event):
        """Handle user selection"""
        selection = self.user_tree.selection()
        if not selection:
            return
            
        # Get selected user
        item = selection[0]
        username = self.user_tree.item(item)['values'][0]
        role = self.user_tree.item(item)['values'][1]
        
        # Update form
        self.username_var.set(username)
        self.role_var.set(role)
        self.password_var.set('')  # Clear password field
        
    def add_user(self):
        """Add a new user"""
        username = self.username_var.get()
        password = self.password_var.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
            
        try:
            self.user_manager.create_user(username, password, UserRole(role))
            messagebox.showinfo("Success", f"User {username} created successfully")
            self.load_users()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def update_user(self):
        """Update selected user"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a user to update")
            return
            
        username = self.username_var.get()
        role = self.role_var.get()
        
        try:
            self.user_manager.update_user(username, role=UserRole(role))
            messagebox.showinfo("Success", f"User {username} updated successfully")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def delete_user(self):
        """Delete selected user"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a user to delete")
            return
            
        username = self.username_var.get()
        if username == self.parent.current_user.username:
            messagebox.showerror("Error", "Cannot delete your own account")
            return
            
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete user {username}?"):
            try:
                self.user_manager.delete_user(username)
                messagebox.showinfo("Success", f"User {username} deleted successfully")
                self.load_users()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def reset_password(self):
        """Reset password for selected user"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a user")
            return
            
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not password:
            messagebox.showerror("Error", "Please enter new password")
            return
            
        try:
            self.user_manager.update_user(username, password=password)
            messagebox.showinfo("Success", f"Password reset for {username}")
            self.password_var.set('')  # Clear password field
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def clear_form(self):
        """Clear the form fields"""
        self.username_var.set('')
        self.password_var.set('')
        self.role_var.set(UserRole.USER.value)
