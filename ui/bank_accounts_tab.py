import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
import subprocess
from auth.user_management import UserRole

class BankAccountsTab:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.bank_frame = ttk.Frame(parent)
        self.bank_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Data paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data" / "bank_accounts"
        self.documents_dir = self.base_dir / "data" / "bank_documents"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        
        # Create right-click menu
        self.context_menu = tk.Menu(self.bank_frame, tearoff=0)
        
        # Initialize UI components
        self.setup_ui()
        self.load_bank_data()
        
    def setup_ui(self):
        """Setup the user interface components"""
        # Top control frame
        control_frame = ttk.Frame(self.bank_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Company selection
        ttk.Label(control_frame, text="Company:").pack(side=tk.LEFT, padx=5)
        self.company_var = tk.StringVar(value="Salam")
        company_combo = ttk.Combobox(control_frame, textvariable=self.company_var,
                                   values=["Salam", "MVNO"], state="readonly")
        company_combo.pack(side=tk.LEFT, padx=5)
        company_combo.bind('<<ComboboxSelected>>', self.on_company_change)
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh", 
                  command=self.refresh_data).pack(side=tk.RIGHT, padx=5)
        
        # Create table
        self.setup_table()
        
        # Notification area
        self.notification_var = tk.StringVar()
        self.notification_label = ttk.Label(self.bank_frame, 
                                          textvariable=self.notification_var,
                                          wraplength=600)
        self.notification_label.pack(fill=tk.X, padx=5, pady=5)
        
    def setup_table(self):
        """Setup the bank accounts table"""
        # Create table frame with scrollbar
        table_frame = ttk.Frame(self.bank_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("Account Name", "Bank Name", "Account Number", 
                  "IBAN", "Currency", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, 
                                show="headings",
                                selectmode="browse")
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, 
                            command=lambda c=col: self.sort_table(c))
            self.tree.column(col, width=100)  # Adjust width as needed
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_account_click)
        self.tree.bind('<Button-3>', self.show_context_menu)  # Right-click
        self.tree.bind('<Control-c>', lambda e: self.copy_selected_details())  # Ctrl+C shortcut
        
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Clear existing menu items
        self.context_menu.delete(0, tk.END)
        
        # Get item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            # Add Copy option (available to all users)
            self.context_menu.add_command(label="Copy Details", 
                                        command=self.copy_selected_details)
            
            # Add Edit option (admin only)
            if hasattr(self.main_app, 'current_user') and \
               self.main_app.current_user.role == UserRole.ADMIN:
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Edit Details", 
                                            command=self.edit_selected_details)
            
            # Show context menu
            self.context_menu.tk_popup(event.x_root, event.y_root)
            
    def copy_selected_details(self):
        """Copy selected account details in a formatted way"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.tree.item(item)['values']
        if not values:
            return
            
        # Format the details
        details = (
            f"Account Name: {values[0]}\n"
            f"Bank Name: {values[1]}\n"
            f"Account Number: {values[2]}\n"
            f"IBAN: {values[3]}\n"
            f"Currency: {values[4]}\n"
            f"Status: {values[5]}"
        )
        
        # Copy to clipboard
        self.parent.clipboard_clear()
        self.parent.clipboard_append(details)
        self.notification_var.set("Account details copied successfully")
        
    def edit_selected_details(self):
        """Open edit dialog for selected account (admin only)"""
        if not hasattr(self.main_app, 'current_user') or \
           self.main_app.current_user.role != UserRole.ADMIN:
            self.notification_var.set("Only administrators can edit account details")
            return
            
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.tree.item(item)['values']
        if not values:
            return
            
        self.show_edit_dialog(dict(zip(
            ['account_name', 'bank_name', 'account_number', 'iban', 'currency', 'status'],
            values
        )))
        
    def show_edit_dialog(self, account_data):
        """Show dialog for editing account details"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Account Details")
        dialog.geometry("400x450")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create frame for form
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create entry fields
        entries = {}
        row = 0
        for field in ['account_name', 'bank_name', 'account_number', 'iban', 'currency', 'status']:
            # Label
            ttk.Label(form_frame, text=field.replace('_', ' ').title()).grid(
                row=row, column=0, sticky='w', pady=5)
            
            # Entry
            var = tk.StringVar(value=account_data.get(field, ''))
            entry = ttk.Entry(form_frame, textvariable=var)
            entry.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
            entries[field] = var
            row += 1
            
        # Add buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save",
                  command=lambda: self.save_account_changes(entries, dialog)
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def save_account_changes(self, entries, dialog):
        """Save changes to account details"""
        # Validate entries
        for field, var in entries.items():
            if not var.get().strip():
                self.notification_var.set(f"{field.replace('_', ' ').title()} cannot be empty")
                return
                
        # Get selected item
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        
        # Update treeview
        self.tree.item(item, values=[var.get() for var in entries.values()])
        
        # Update data file
        try:
            self.save_data_to_file()
            self.notification_var.set("Account details updated successfully")
            dialog.destroy()
        except Exception as e:
            self.notification_var.set(f"Error saving changes: {str(e)}")
            
    def save_data_to_file(self):
        """Save current data to JSON file"""
        data = {'accounts': []}
        
        # Collect all items from treeview
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            data['accounts'].append({
                'account_name': values[0],
                'bank_name': values[1],
                'account_number': values[2],
                'iban': values[3],
                'currency': values[4],
                'status': values[5]
            })
            
        # Save to file
        company = self.company_var.get().lower()
        data_file = self.data_dir / f"{company}_accounts.json"
        with data_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
    def load_bank_data(self):
        """Load bank account data from file"""
        company = self.company_var.get().lower()
        data_file = self.data_dir / f"{company}_accounts.json"
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Load data if file exists
        try:
            if data_file.exists():
                with data_file.open('r', encoding='utf-8') as f:
                    accounts = json.load(f)
                    for account in accounts['accounts']:
                        self.tree.insert('', tk.END, values=(
                            account.get('account_name', ''),
                            account.get('bank_name', ''),
                            account.get('account_number', ''),
                            account.get('iban', ''),
                            account.get('currency', ''),
                            account.get('status', '')
                        ))
        except Exception as e:
            self.notification_var.set(f"Error loading bank data: {str(e)}")
            
    def on_company_change(self, event=None):
        """Handle company selection change"""
        self.load_bank_data()
        
    def refresh_data(self):
        """Refresh the bank account data"""
        self.load_bank_data()
        self.notification_var.set("Data refreshed successfully")
        
    def sort_table(self, col):
        """Sort table by column"""
        # Get all items
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Sort items
        items.sort()
        
        # Rearrange items in sorted positions
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
            
    def on_account_click(self, event):
        """Handle account selection"""
        # Get selected item
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        account_name = self.tree.item(item)['values'][0]
        
        # Create document options window
        self.show_document_options(account_name)
        
    def show_document_options(self, account_name):
        """Show document options dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Documents - {account_name}")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create frame for buttons
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Document buttons
        doc_types = [
            ("IBAN Letter", "iban_letter"),
            ("Authorization Letter", "auth_letter"),
            ("Other Documents", "other_docs")
        ]
        
        for doc_name, doc_type in doc_types:
            btn = ttk.Button(frame, text=doc_name,
                           command=lambda a=account_name, t=doc_type: 
                           self.open_document(a, t, dialog))
            btn.pack(fill=tk.X, pady=5)
            
        # Close button
        ttk.Button(frame, text="Close",
                  command=dialog.destroy).pack(fill=tk.X, pady=20)
        
    def open_document(self, account_name, doc_type, dialog):
        """Open the selected document"""
        try:
            company = self.company_var.get().lower()
            doc_dir = self.documents_dir / company / account_name / doc_type
            
            if not doc_dir.exists():
                doc_dir.mkdir(parents=True, exist_ok=True)
                self.notification_var.set(f"Created new document directory: {doc_type}")
                dialog.destroy()
                return
                
            # Open document directory
            if doc_dir.exists():
                subprocess.Popen(['explorer', str(doc_dir)])
                self.notification_var.set(f"Opening {doc_type} documents for {account_name}")
            else:
                self.notification_var.set(f"No {doc_type} documents found for {account_name}")
                
            dialog.destroy()
            
        except Exception as e:
            self.notification_var.set(f"Error opening document: {str(e)}")
            dialog.destroy()
