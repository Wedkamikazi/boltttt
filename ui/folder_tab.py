import tkinter as tk
from tkinter import ttk, messagebox
from utils.folder_system import FolderManager, Company
import calendar
from datetime import datetime

class FolderTab:
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.folder_manager = FolderManager()
        
        # Create main frame
        self.main_frame = ttk.Frame(parent, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top frame for selections
        select_frame = ttk.LabelFrame(self.main_frame, text="Folder Selection", padding=5)
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Company selection
        company_frame = ttk.Frame(select_frame)
        company_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(company_frame, text="Company:").pack(side=tk.LEFT)
        self.company_var = tk.StringVar(value=Company.SALAM.value)  # Set default company
        self.company_combo = ttk.Combobox(company_frame, textvariable=self.company_var, 
                                        values=[c.value for c in Company], state="readonly")
        self.company_combo.pack(side=tk.LEFT, padx=5)
        self.company_combo.bind('<<ComboboxSelected>>', self.on_company_select)
        
        # Year selection
        year_frame = ttk.Frame(select_frame)
        year_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(year_frame, text="Year:").pack(side=tk.LEFT)
        available_years = self.folder_manager.get_available_years()
        self.year_var = tk.StringVar(value=str(available_years[-1]))  # Set to latest year
        self.year_combo = ttk.Combobox(year_frame, textvariable=self.year_var,
                                     values=available_years, state="readonly")
        self.year_combo.pack(side=tk.LEFT, padx=5)
        
        # Month selection
        month_frame = ttk.Frame(select_frame)
        month_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(month_frame, text="Month:").pack(side=tk.LEFT)
        months = self.folder_manager.get_months()
        current_month = datetime.now().strftime("%B")  # Get current month name
        self.month_var = tk.StringVar(value=current_month)  # Set to current month
        self.month_combo = ttk.Combobox(month_frame, textvariable=self.month_var,
                                      values=months, state="readonly")
        self.month_combo.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(select_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create Missing Folder", command=self.create_folder).pack(side=tk.LEFT, padx=5)
        
        # Notification area
        notification_frame = ttk.LabelFrame(self.main_frame, text="Notifications", padding=5)
        notification_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notification_text = tk.Text(notification_frame, height=10, wrap=tk.WORD)
        self.notification_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial check for missing folders
        self.check_missing_folders()
        
    def on_company_select(self, event=None):
        """Handle company selection"""
        self.check_missing_folders()
        
    def open_folder(self):
        """Open selected folder"""
        if not all([self.company_var.get(), self.year_var.get(), self.month_var.get()]):
            messagebox.showwarning("Warning", "Please select company, year, and month")
            return
            
        company = Company(self.company_var.get())
        year = int(self.year_var.get())
        month = self.month_var.get()
        
        if not self.folder_manager.open_folder(company, year, month):
            messagebox.showerror("Error", f"Could not open folder for {month} {year}")
            
    def create_folder(self):
        """Create selected folder"""
        if not all([self.company_var.get(), self.year_var.get(), self.month_var.get()]):
            messagebox.showwarning("Warning", "Please select company, year, and month")
            return
            
        company = Company(self.company_var.get())
        year = int(self.year_var.get())
        month = self.month_var.get()
        
        if self.folder_manager.create_folder(company, year, month):
            messagebox.showinfo("Success", f"Created folder for {company.value}/{month} {year}")
            # Update notifications immediately after creating folder
            self.check_missing_folders()
        else:
            messagebox.showerror("Error", f"Could not create folder for {company.value}/{month} {year}")
            
    def check_missing_folders(self):
        """Check and display missing folders"""
        self.notification_text.delete(1.0, tk.END)
        
        # Get selected company if any
        selected_company = Company(self.company_var.get()) if self.company_var.get() else None
        missing = self.folder_manager.get_missing_folders(selected_company)
        
        if not missing:
            self.notification_text.insert(tk.END, "✅ All required folders are present.\n", "success")
            return
            
        # Add single warning header
        self.notification_text.insert(tk.END, 
            "\n⚠️ Missing Folders:\n", "warning")
            
        # Reorganize by year first
        by_year = {}
        for company, folders in missing.items():
            # Skip if we're filtering for a specific company and this isn't it
            if selected_company and company != selected_company.value:
                continue
                
            for folder in folders:
                month, year = folder.split()
                if year not in by_year:
                    by_year[year] = {}
                if company not in by_year[year]:
                    by_year[year][company] = []
                by_year[year][company].append(month)
        
        # Display organized by year
        for year in sorted(by_year.keys()):
            self.notification_text.insert(tk.END, f"\n{year}:\n", "year")
            
            for company in sorted(by_year[year].keys()):
                months = sorted(by_year[year][company], 
                             key=lambda m: list(calendar.month_name).index(m))
                # If a company is selected, don't show the company name in each line
                if selected_company:
                    self.notification_text.insert(tk.END, "  ", "indent")
                else:
                    self.notification_text.insert(tk.END, f"  {company}: ", "company")
                self.notification_text.insert(tk.END, 
                    ", ".join(months) + "\n", "months")
        
        # Configure tags for styling
        self.notification_text.tag_configure("success", foreground="green")
        self.notification_text.tag_configure("warning", foreground="red")
        self.notification_text.tag_configure("company", foreground="blue", font=("TkDefaultFont", 10, "bold"))
        self.notification_text.tag_configure("year", foreground="dark blue", font=("TkDefaultFont", 10, "bold"))
        self.notification_text.tag_configure("months", foreground="black")
        self.notification_text.tag_configure("indent", foreground="black")
