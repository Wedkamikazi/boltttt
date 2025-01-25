import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from pathlib import Path
from auth.login_window import LoginWindow
from auth.user_management import UserRole, User, UserManager
from ui.todo_tab import TodoTab
from ui.folder_tab import FolderTab
from ui.bank_accounts_tab import BankAccountsTab
from ui.clearing_tab import ClearingTab
from ui.lg_operations import LGTab
from core.validation_system import ValidationSystem
from core.status_tracker import StatusTracker
from core.file_operations import FileOperations
import os
import subprocess

class PaymentSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Payment Processing System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set base paths
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        
        # Ensure data directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "treasury").mkdir(exist_ok=True)
        (self.data_dir / "bs").mkdir(exist_ok=True)
        (self.data_dir / "cnp").mkdir(exist_ok=True)
        
        # Initialize user manager and validation system
        self.user_manager = UserManager()
        self.validation_system = ValidationSystem()
        self.file_operations = FileOperations()
        
        # Initialize notification state
        self.notification_count = 0
        self.notification_labels = []
        
        # Show login window first
        self.show_login()
        
    def show_login(self):
        """Show login window and hide main content"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Reset window title
        self.root.title("Payment Processing System - Login")
        
        # Show login window
        from auth.login_window import LoginWindow
        self.login_window = LoginWindow(self)
        
    def on_login_success(self, user: User):
        """Called when login is successful"""
        self.current_user = user
        
        # Clear login window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Variables
        self.company_var = tk.StringVar()
        self.beneficiary_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.exception_var = tk.BooleanVar()
        self.approver_var = tk.StringVar()
        self.signature_var = tk.StringVar()
        self.cnp_approver_var = tk.StringVar()
        self.search_mode_var = tk.BooleanVar()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create main payment frame
        self.payment_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.payment_frame, text="Payments")
        
        # Create LGs frame
        self.lg_tab = LGTab(self.notebook, self)
        self.notebook.add(self.lg_tab.lg_frame, text="LGs")
        
        # Create Todo tab
        todo_tab = TodoTab(self.notebook, self.current_user)
        self.notebook.add(todo_tab.main_frame, text="To Do List")
        
        # Create Folder Management tab
        folder_tab = FolderTab(self.notebook, self.current_user)
        self.notebook.add(folder_tab.main_frame, text="Folder Access")
        
        # Create Bank Accounts tab
        bank_frame = ttk.Frame(self.notebook)
        self.bank_tab = BankAccountsTab(bank_frame, self)
        self.notebook.add(bank_frame, text="Bank Accounts")
        
        # Create Clearing tab
        clearing_frame = ttk.Frame(self.notebook)
        self.clearing_tab = ClearingTab(clearing_frame, self)
        self.notebook.add(clearing_frame, text="Clearing")
        
        self.setup_styles()
        self.create_main_layout()
        self.create_menu()
        
        # Schedule periodic updates for LGs
        self.root.after(1000, self.check_lg_updates)

    def update_all_notifications(self, count):
        """Update notification count across all tabs"""
        self.notification_count = count
        for label in self.notification_labels:
            if label and label.winfo_exists():
                label.config(text=f" {count}" if count > 0 else " 0")

    def register_notification_label(self, label):
        """Register a notification label for updates"""
        self.notification_labels.append(label)

    def setup_styles(self):
        """Setup custom styles for the application"""
        style = ttk.Style()
        
        # General styles
        style.configure("Section.TLabelframe", padding=10)
        style.configure("Action.TButton", padding=5)
        style.configure("Notification.TLabel", font=("TkDefaultFont", 12))
        
        # Treeview styles
        style.configure("Results.Treeview", rowheight=25)
        style.configure("Results.Treeview.Heading", font=("TkDefaultFont", 10, "bold"))
        
        style.configure("Summary.Treeview", rowheight=25)
        style.configure("Summary.Treeview.Heading", font=("TkDefaultFont", 10, "bold"))
        
        # Configure tags for LG status
        self.lg_tab.results_tree.tag_configure('urgent', foreground='red', font=("TkDefaultFont", 9, "bold"))
        self.lg_tab.results_tree.tag_configure('warning', foreground='orange', font=("TkDefaultFont", 9))
        self.lg_tab.results_tree.tag_configure('expired', foreground='gray', font=("TkDefaultFont", 9))
    
    def check_lg_updates(self):
        """Periodic check for LG updates"""
        self.lg_tab.check_for_updates()
        self.root.after(3600000, self.check_lg_updates)  # Check every hour

    def create_main_layout(self):
        """Create the main layout of the application"""
        # Create main container with proper weights
        main_container = ttk.Frame(self.payment_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights
        self.payment_frame.grid_rowconfigure(0, weight=1)
        self.payment_frame.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=2)  # Left panel
        main_container.grid_columnconfigure(1, weight=3)  # Right panel
        main_container.grid_rowconfigure(2, weight=1)     # Content area
        
        # Create title section
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Payment Processing System", 
                              font=("TkDefaultFont", 14, "bold"), foreground="#0066cc")
        title_label.pack(side=tk.LEFT)
        
        # Add notification gadget to title section
        notification_label = ttk.Label(title_frame, text=" 0", style="Notification.TLabel")
        notification_label.pack(side=tk.RIGHT, padx=5)
        self.register_notification_label(notification_label)
        
        dept_label = ttk.Label(main_container, text="Treasury Department", font=("TkDefaultFont", 11))
        dept_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Create panels
        left_panel = ttk.Frame(main_container)
        left_panel.grid(row=2, column=0, sticky="nsew", padx=(0, 5))
        
        right_panel = ttk.Frame(main_container)
        right_panel.grid(row=2, column=1, sticky="nsew", padx=(5, 0))
        
        # Create sections
        self.create_payment_section(left_panel)
        self.create_results_section(right_panel)
        self.create_file_section(right_panel)

    def create_payment_section(self, parent):
        """Create payment details section"""
        payment_frame = ttk.LabelFrame(parent, text="Payment Details", style="Section.TLabelframe")
        payment_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        payment_frame.grid_columnconfigure(1, weight=1)
        
        # Basic payment fields
        row = 0
        ttk.Label(payment_frame, text="Company:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(payment_frame, textvariable=self.company_var, values=["SALAM", "MVNO"], state="readonly"
                     ).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        row += 1
        ttk.Label(payment_frame, text="Beneficiary:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(payment_frame, textvariable=self.beneficiary_var
                 ).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        row += 1
        ttk.Label(payment_frame, text="Reference:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ref_frame = ttk.Frame(payment_frame)
        ref_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ref_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Entry(ref_frame, textvariable=self.reference_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(ref_frame, text="Check Status", command=self.check_status
                  ).grid(row=0, column=1, sticky="e", padx=(5, 0))
        
        row += 1
        ttk.Label(payment_frame, text="Amount:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(payment_frame, textvariable=self.amount_var
                 ).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        row += 1
        ttk.Label(payment_frame, text="Date:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(payment_frame, textvariable=self.date_var
                 ).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        # Action buttons frame
        row += 1
        button_frame = ttk.Frame(payment_frame)
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        
        # Create buttons with fixed width and center alignment
        validate_btn = ttk.Button(button_frame, text=" Validate", command=self.validate_payment, 
                                style="Action.TButton", width=12)
        process_btn = ttk.Button(button_frame, text=" Process", command=self.process_payment, 
                               style="Action.TButton", width=12)
        clear_btn = ttk.Button(button_frame, text=" Clear", command=self.clear_form, width=12)
        
        # Center the buttons using pack
        for btn in [validate_btn, process_btn, clear_btn]:
            btn.pack(side="left", expand=True, padx=5)
        
        # Search mode checkbox with extra padding
        row += 1
        search_frame = ttk.LabelFrame(payment_frame, text="Search Mode", padding=5)
        search_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        search_mode = ttk.Checkbutton(search_frame, text="Read-only search across all files", variable=self.search_mode_var)
        search_mode.pack(anchor=tk.W)

        # Exception Processing frame
        exception_frame = ttk.LabelFrame(payment_frame, text="Exception Processing", padding=5)
        exception_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        process_exception = ttk.Checkbutton(exception_frame, text="Process as Exception (for old payments)", 
                                          variable=self.exception_var, 
                                          command=self.toggle_exception_mode)
        process_exception.pack(anchor=tk.W)
        
        # Only create the Reason field
        ttk.Label(exception_frame, text="Reason for Exception:").pack(anchor=tk.W, pady=(5,0))
        self.exception_reason_entry = ttk.Entry(exception_frame)
        self.exception_reason_entry.pack(fill=tk.X, pady=2, padx=5)
        # Initially hide the reason field
        self.exception_reason_entry.pack_forget()

    def toggle_exception_mode(self):
        """Toggle exception mode fields visibility"""
        if self.exception_var.get():
            self.exception_reason_entry.pack(fill=tk.X, pady=2, padx=5)  # Show reason field
            self.show_in_results("Exception Mode Activated\nPlease fill in the reason for exception.", "warning")
        else:
            self.exception_reason_entry.pack_forget()  # Hide reason field
            self.show_in_results("Exception Mode Deactivated", "info")

    def create_results_section(self, parent):
        """Create results display section"""
        results_frame = ttk.LabelFrame(parent, text="Results", style="Section.TLabelframe")
        results_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)  # Make text widget expand
        
        # Results text widget with scrollbar
        self.results_text = tk.Text(results_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)
        
        self.results_text.config(state='disabled')

    def create_file_section(self, parent):
        """Create file access section with icons"""
        file_frame = ttk.LabelFrame(parent, text=" File Access", style="Section.TLabelframe")
        file_frame.grid(row=1, column=0, sticky="ew")  # Changed to ew to prevent vertical expansion
        file_frame.grid_columnconfigure(0, weight=1)
        
        # Button container
        button_container = ttk.Frame(file_frame)
        button_container.grid(row=0, column=0, pady=5)  # Reduced padding
        
        # File buttons with icons in a grid layout
        buttons = [
            (" BS-Salam", "BS-Salam"),
            (" BS-MVNO", "BS-MVNO"),
            (" CNP-Salam", "CNP-Salam"),
            (" CNP-MVNO", "CNP-MVNO"),
            (" Treasury", "Treasury")
        ]
        
        for i, (text, command_text) in enumerate(buttons):
            ttk.Button(button_container, text=text,
                      command=lambda x=command_text: self.open_file(x)
                      ).grid(row=0, column=i, padx=3)  # Reduced padding
        
        # Update status button with icon
        ttk.Button(file_frame, text=" Update All Statuses", style="Action.TButton",
                  command=self.update_all_statuses).grid(row=1, column=0, pady=5)  # Reduced padding

    def show_in_results(self, text, message_type="info"):
        """Display text in results panel"""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)  # Clear previous content
        
        # Add icon based on message type
        icon = {
            "success": " ",
            "error": " ",
            "warning": " ",
            "info": " "
        }.get(message_type, "")
        
        self.results_text.insert(tk.END, f"{icon}{text}")
        self.results_text.see(tk.END)
        self.results_text.config(state='disabled')

    def open_file(self, file_type):
        """Open file in system default application"""
        try:
            # Convert file type to match the keys in file_ops
            if file_type == "BS-Salam":
                file_type = "BS-SALAM"
            elif file_type == "CNP-Salam":
                file_type = "CNP-SALAM"

            # Get the correct file path
            if file_type == "Treasury":
                file_path = self.data_dir / "treasury" / "TREASURY_CURRENT.csv"
            else:
                folder = file_type.split('-')[0].lower()
                file_path = self.data_dir / folder / f"{file_type}_CURRENT.csv"
            
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file with headers if it doesn't exist
            if not file_path.exists():
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary'])
            
            # Open file with default application
            os.startfile(str(file_path))
            
        except Exception as e:
            self.show_in_results(f"Error opening file: {str(e)}", "error")

    def update_all_statuses(self):
        """Update status for all payments"""
        try:
            self.show_in_results("Updating all statuses...", "info")
            
            # Use StatusTracker to update all statuses
            status_tracker = StatusTracker(self.file_operations)
            results = status_tracker.update_all_statuses()
            
            # Show results
            if results['updated'] > 0:
                message = f"\nSuccessfully updated {results['updated']} payment(s)!"
                if results['details']:
                    message += "\n\nDetails:"
                    for detail in results['details']:
                        message += f"\n• {detail}"
                self.show_in_results(message, "success")
            elif results['errors'] > 0:
                message = f"\nEncountered {results['errors']} error(s) while updating."
                if results['details']:
                    message += "\n\nDetails:"
                    for detail in results['details']:
                        message += f"\n• {detail}"
                self.show_in_results(message, "error")
            else:
                self.show_in_results("\nNo payments needed updating", "info")
                
        except Exception as e:
            self.show_in_results(f"Error updating statuses: {str(e)}", "error")

    def check_status(self):
        """Check payment status across all files"""
        reference = self.reference_var.get().strip()
        if not reference:
            self.show_in_results(" Please enter a reference number", "error")
            return
            
        try:
            # Use StatusTracker to check status
            status_tracker = StatusTracker(self.file_operations)
            status = status_tracker.get_status(reference)
            
            if status:
                message = f"\nPayment Status for {reference}:\n"
                message += f"\nCurrent Status: {status['status']}"
                message += f"\nLast Updated: {status['timestamp']}"
                if status.get('user'):
                    message += f"\nUpdated By: {status['user']}"
                if status.get('reason'):
                    message += f"\nReason: {status['reason']}"
                self.show_in_results(message, "info")
            else:
                self.show_in_results(f"\nNo status found for reference: {reference}", "warning")
                
        except Exception as e:
            self.show_in_results(f"Error checking status: {str(e)}", "error")

    def validate_payment(self):
        """Validate payment details"""
        try:
            # Get form data
            payment_data = self.get_payment_data()
            
            # If in search mode, just search without validation
            if self.search_mode_var.get():
                results = self.search_payment(payment_data)
                self.show_in_results("\n Search Results:")
                for result in results:
                    self.show_in_results(f"\n• {result}")
                return False
            
            # Check if it's an old payment
            if self._is_old_payment(payment_data['date']) and not self.exception_var.get():
                self.show_in_results("\n This is an old payment. Please ensure you check 'Process as Exception' box.", "warning")
                return False
            
            # Use ValidationSystem for comprehensive validation
            validation_result = self.validation_system.validate_input(payment_data)
            
            if not validation_result['valid']:
                error_msg = "\n".join(validation_result['errors'])
                self.show_in_results(f"\nValidation failed:\n{error_msg}", "error")
                return False
            
            # Check if CNP approval is required
            if validation_result.get('cnp_required', False):
                if not self.exception_var.get():
                    self.show_in_results("\nThis payment requires CNP approval. Please check 'Process as Exception' box.", "warning")
                    return False
                
            # Check exception mode requirements if enabled
            if self.exception_var.get():
                explanation = self.exception_reason_entry.get()
                if not explanation:
                    error_msg = (
                        "When using Exception Mode:\n"
                        "- Exception reason is required"
                    )
                    self.show_in_results(f"\nValidation failed:\n{error_msg}", "error")
                    return False
            
            self.show_in_results("\nValidation successful!", "success")
            return True
            
        except Exception as e:
            self.show_in_results(f"\nValidation failed: {str(e)}", "error")
            return False

    def validate_payment_data(self, payment_data):
        """
        Validate payment data according to business rules
        Returns dict with 'valid' boolean and 'errors' list
        """
        try:
            errors = []
            
            # Check data types
            if not isinstance(payment_data, dict):
                errors.append("Payment data must be a dictionary")
                return {'valid': False, 'errors': errors}
                
            required_fields = ['company', 'beneficiary', 'reference', 'amount', 'date']
            for field in required_fields:
                if field not in payment_data:
                    errors.append(f"Missing required field: {field}")
                    continue
                    
                if not isinstance(payment_data[field], str):
                    errors.append(f"Field {field} must be a string")
                    return {'valid': False, 'errors': errors}  # Return immediately for type errors
            
            # Validate company
            if payment_data.get('company') not in ['SALAM', 'MVNO']:
                errors.append("Company must be either SALAM or MVNO")
                
            # Beneficiary validation
            beneficiary = payment_data.get('beneficiary', '')
            if len(beneficiary.strip()) < 2:
                errors.append("Beneficiary name too short")
            if len(beneficiary) > 100:
                errors.append("Beneficiary name too long")
            if beneficiary.strip() != beneficiary:
                errors.append("Beneficiary cannot have leading/trailing whitespace")
            if beneficiary[0].isdigit():
                errors.append("Beneficiary cannot start with a number")
            if any(ord(c) > 127 for c in beneficiary):
                errors.append("Beneficiary contains non-ASCII characters")
            if any(c in '@#$%^&*()+=<>[]{}|\\;\n"!/' for c in beneficiary):
                errors.append("Beneficiary contains invalid characters")
            if any(c.isdigit() for c in beneficiary):
                errors.append("Beneficiary cannot contain numbers")
            if '..' in beneficiary:
                errors.append("Beneficiary cannot contain consecutive dots")
            if '--' in beneficiary:
                errors.append("Beneficiary cannot contain consecutive hyphens")
            if "''" in beneficiary:
                errors.append('Beneficiary cannot contain consecutive single quotes')
            if beneficiary[-1] == '.':
                errors.append("Beneficiary cannot end with a dot")
            
            # SQL injection prevention
            sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'WHERE', 'FROM', 'TABLE']
            if any(keyword in beneficiary.upper() for keyword in sql_keywords):
                errors.append('Beneficiary contains SQL keywords')
            
            # Validate reference
            ref = payment_data.get('reference', '')
            if not ref.startswith('TST-'):
                errors.append("Reference must start with TST-")
            if len(ref) != 13:
                errors.append("Reference must be 13 characters long")
            if ref.count('-') != 2:
                errors.append("Reference must have exactly two hyphens")
            try:
                _, year, seq = ref.split('-')
                if not year.isdigit() or not seq.isdigit():
                    errors.append("Reference year and sequence must be numeric")
                year_int = int(year)
                if year_int < 2020 or year_int > 2030:
                    errors.append("Reference year must be between 2020 and 2030")
                seq_int = int(seq)
                if seq_int < 1 or seq_int > 9999:
                    errors.append("Reference sequence must be between 0001 and 9999")
                if len(seq) != 4:
                    errors.append("Reference sequence must be exactly 4 digits")
            except (ValueError, IndexError):
                errors.append("Invalid reference format")
            
            # Validate amount
            amount = payment_data.get('amount', '')
            try:
                if amount.startswith('0') and not amount.startswith('0.'):
                    errors.append("Amount cannot have leading zeros")
                if ',' in amount:
                    errors.append("Amount cannot contain commas")
                amount_float = float(amount)
                if amount_float <= 0:
                    errors.append("Amount must be positive")
                if amount_float >= 15000:
                    errors.append("Amount exceeds maximum limit of 15000")
                if '.' not in amount or len(amount.split('.')[1]) != 2:
                    errors.append("Amount must have exactly 2 decimal places")
            except ValueError:
                errors.append("Invalid amount format")
            
            # Validate date
            date = payment_data.get('date', '')
            try:
                if len(date.split('-')) != 3:
                    errors.append("Invalid date format")
                else:
                    year, month, day = date.split('-')
                    if len(month) != 2 or len(day) != 2:
                        errors.append("Date month and day must have 2 digits")
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    if date_obj.date() > datetime.strptime('2025-01-16', '%Y-%m-%d').date():
                        errors.append("Future dates not allowed")
                    if date_obj.year < 2020:
                        errors.append("Date year must be 2020 or later")
            except ValueError as e:
                errors.append(f"Invalid date format: {str(e)}")
            
            # Check if CNP approval is required for past month payments
            if len(errors) == 0:  # Only check if no other errors
                current_month = datetime.strptime('2025-01-16', '%Y-%m-%d').replace(day=1)
                payment_month = date_obj.replace(day=1)
                cnp_required = payment_month < current_month
            
                return {
                    'valid': True,
                    'errors': [],
                    'cnp_required': cnp_required
                }
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
        
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}']
            }

    def process_payment(self):
        """Process the payment"""
        try:
            # Get form data
            payment_data = self.get_payment_data()
            
            # If in search mode, just search without processing
            if self.search_mode_var.get():
                results = self.search_payment(payment_data)
                self.show_in_results("\n Search Results:")
                for result in results:
                    self.show_in_results(f"\n• {result}")
                return
            
            if not self.validate_payment():
                return
            
            # Show confirmation dialog
            confirm_msg = f"""Please confirm payment details:

Company: {payment_data['company']}
Beneficiary: {payment_data['beneficiary']}
Reference: {payment_data['reference']}
Amount: {payment_data['amount']}
Date: {payment_data['date']}

Do you want to proceed with this payment?"""

            if self.exception_var.get():
                confirm_msg += f"\n\n WARNING: EXCEPTION MODE ACTIVE\n"
                confirm_msg += f"Reason: {self.exception_reason_entry.get()}\n"

            if not messagebox.askyesno("Confirm Payment", confirm_msg):
                self.show_in_results("Payment cancelled by user", "info")
                return
            
            # Save payment
            self.save_to_treasury(payment_data)
            self.show_in_results(" Payment processed successfully!", "success")
            self.clear_form()
            
        except Exception as e:
            self.show_in_results(f" Error processing payment: {str(e)}", "error")

    def get_payment_data(self):
        """Get current payment data from form"""
        return {
            'company': self.company_var.get(),
            'beneficiary': self.beneficiary_var.get(),
            'reference': self.reference_var.get().strip(),
            'amount': self.amount_var.get().strip(),
            'date': self.date_var.get(),
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def clear_form(self):
        """Clear all form fields"""
        self.company_var.set('')
        self.beneficiary_var.set('')
        self.reference_var.set('')
        self.amount_var.set('')
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.exception_var.set(False)
        self.exception_reason_entry.delete(0, tk.END)
        self.search_mode_var.set(False)
        self.show_in_results("Form cleared", "info")

    def _is_old_payment(self, date_str):
        """Check if payment is from a previous month"""
        try:
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            return (payment_date.year < current_date.year or 
                   (payment_date.year == current_date.year and payment_date.month < current_date.month))
        except:
            return False

    def save_to_treasury(self, payment_data):
        """Save payment data to treasury file"""
        try:
            treasury_file = self.data_dir / 'treasury' / 'TREASURY_CURRENT.csv'
            treasury_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and get headers
            headers = []
            if treasury_file.exists():
                with open(treasury_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
            else:
                headers = [
                    'Company', 'Beneficiary', 'Reference', 'Amount',
                    'Date', 'Exception', 'Approver', 'Signature',
                    'CNP Approver', 'Status'
                ]
            
            # Write data
            mode = 'a' if treasury_file.exists() else 'w'
            with open(treasury_file, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                if mode == 'w':
                    writer.writeheader()
                writer.writerow(payment_data)
                
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to treasury: {str(e)}")
            return False
            
    def search_payment(self, payment_data):
        """Search for payment across all files without modifying anything"""
        results = []
        reference = payment_data['reference']
        amount = payment_data.get('amount', '0')
        
        try:
            # Check Treasury
            treasury_file = self.data_dir / 'treasury' / 'TREASURY_CURRENT.csv'
            if treasury_file.exists():
                with open(treasury_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if (row['reference'].strip() == reference or 
                            (amount and abs(float(row.get('amount', '0').strip()) - float(amount)) < 0.01)):
                            results.append(f"Found in Treasury (Status: {row.get('status', 'N/A')})")
            
            # Check BS files
            for company in ['SALAM', 'MVNO']:
                bs_file = self.data_dir / 'bs' / f'BS-{company}.csv'
                if bs_file.exists():
                    with open(bs_file, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if (row['reference'].strip() == reference or 
                                (amount and abs(float(row.get('amount', '0').strip()) - float(amount)) < 0.01)):
                                results.append(f"Found in BS-{company}")
                                
            # Check CNP files
            for company in ['SALAM', 'MVNO']:
                cnp_file = self.data_dir / 'cnp' / f'CNP-{company}.csv'
                if cnp_file.exists():
                    with open(cnp_file, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if (row['reference'].strip() == reference or 
                                (amount and abs(float(row.get('amount', '0').strip()) - float(amount)) < 0.01)):
                                results.append(f"Found in CNP-{company}")
            
            return results if results else ["Payment not found in any file"]
        except Exception as e:
            return [f"Error searching: {str(e)}"]

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Add admin menu items if user is admin
        if self.current_user.role == UserRole.ADMIN:
            file_menu.add_command(label="Admin Panel", command=self.show_admin_panel)
            file_menu.add_separator()
            
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Show user info
        menubar.add_command(label=f"Logged in as: {self.current_user.username} ({self.current_user.role.value})",
                          state="disabled")

    def show_admin_panel(self):
        """Show the admin panel"""
        from auth.admin_panel import AdminPanel
        AdminPanel(self)

    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clear user session
            if hasattr(self, 'current_user'):
                self.user_manager.logout(self.current_user.username)
            
            # Clear saved credentials if they exist
            try:
                if (self.data_dir / "credentials.json").exists():
                    (self.data_dir / "credentials.json").unlink()
            except:
                pass
            
            # Show login window
            self.show_login()

class ValidationSystem:
    def validate_input(self, payment_data):
        """
        Basic validation of payment data
        Returns dict with 'valid' boolean and 'errors' list
        """
        errors = []
        date_obj = None
        
        try:
            # Check data types and required fields
            if not isinstance(payment_data, dict):
                return {'valid': False, 'errors': ['Payment data must be a dictionary']}
                
            required_fields = ['company', 'beneficiary', 'reference', 'amount', 'date']
            missing_fields = [field for field in required_fields if field not in payment_data]
            if missing_fields:
                return {'valid': False, 'errors': [f'Missing required fields: {", ".join(missing_fields)}']}
                
            # Basic field validations
            if payment_data['company'] not in ['SALAM', 'MVNO']:
                errors.append('Company must be either SALAM or MVNO')
                
            # Amount validation - only check if it's a valid number
            amount = payment_data['amount']
            try:
                amount_float = float(amount)
                if amount_float <= 0:
                    errors.append('Amount must be positive')
            except ValueError:
                errors.append('Invalid amount format')
                
            # Date validation - only check if it's a valid date
            date = payment_data['date']
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                errors.append('Invalid date format (must be YYYY-MM-DD)')
                
            # Return result with CNP check if no errors
            if len(errors) == 0 and date_obj is not None:
                current_month = datetime.strptime('2025-01-16', '%Y-%m-%d').replace(day=1)
                payment_month = date_obj.replace(day=1)
                cnp_required = payment_month < current_month
            
                return {
                    'valid': True,
                    'errors': [],
                    'cnp_required': cnp_required
                }
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}']
            }

def main():
    from ui.splash_screen import SplashScreen
    
    # Show splash screen
    splash = SplashScreen()
    splash.mainloop()
    
    # Start main application
    root = tk.Tk()
    app = PaymentSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
