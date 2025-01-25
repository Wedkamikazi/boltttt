import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

class LGTab:
    def __init__(self, parent, main_app):
        """Initialize LG tab"""
        self.parent = parent
        self.main_app = main_app  # Reference to main application
        self.lg_frame = ttk.Frame(parent)
        self.create_lg_tab()
        self.last_check_time = None
        
        # Set data file path
        self.base_dir = Path(__file__).parent.parent
        self.lg_file = self.base_dir / "data" / "LGs.xlsx"
        
        # Ensure data directory exists
        self.lg_file.parent.mkdir(parents=True, exist_ok=True)
        
    def create_lg_tab(self):
        """Create the LG tab interface"""
        # Top section with Update button
        top_frame = ttk.Frame(self.lg_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        update_btn = ttk.Button(top_frame, text="Update LGs", command=self.update_lgs, style="Action.TButton")
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Notification icon
        notification_label = ttk.Label(top_frame, text=" 0", style="Notification.TLabel")
        notification_label.pack(side=tk.RIGHT, padx=5)
        self.main_app.register_notification_label(notification_label)
        
        # Results section
        results_frame = ttk.LabelFrame(self.lg_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview for results
        self.results_tree = ttk.Treeview(results_frame, columns=(
            "Sequence No.", "Vendor Name", "LG Number", "Start Date",
            "End Date", "Type of LG", "Related To", "Days Remaining"
        ), show="headings", style="Results.Treeview")
        
        # Configure columns
        column_widths = {
            "Sequence No.": 100,
            "Vendor Name": 150,
            "LG Number": 100,
            "Start Date": 100,
            "End Date": 100,
            "Type of LG": 120,
            "Related To": 120,
            "Days Remaining": 100
        }
        
        for col, width in column_widths.items():
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=width, minwidth=width)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Summary section
        summary_frame = ttk.LabelFrame(self.lg_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create Treeview for summary
        self.summary_tree = ttk.Treeview(summary_frame, columns=(
            "Type of LG", "Count", "Total Amount (SAR)"
        ), show="headings", style="Summary.Treeview", height=5)
        
        # Configure summary columns
        summary_widths = {
            "Type of LG": 300,
            "Count": 100,
            "Total Amount (SAR)": 200
        }
        
        for col, width in summary_widths.items():
            self.summary_tree.heading(col, text=col)
            self.summary_tree.column(col, width=width, minwidth=width)
        
        self.summary_tree.pack(fill=tk.X, padx=5, pady=5)

    def update_lgs(self):
        """Update LGs information with proper error handling"""
        try:
            # Check if file exists
            if not self.lg_file.exists():
                messagebox.showerror("Error", "LGs file not found")
                return
                
            # Clear existing items
            self.results_tree.delete(*self.results_tree.get_children())
            self.summary_tree.delete(*self.summary_tree.get_children())
            
            # Read Excel file
            df = pd.read_excel(self.lg_file)
            
            if df.empty:
                messagebox.showinfo("Info", "No LG data found")
                return
                
            # Basic data validation
            required_columns = ["Sequence No.", "Vendor Name", "LG Number", 
                              "Start Date", "End Date", "Type of LG"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                messagebox.showerror("Error", f"Missing columns: {', '.join(missing_columns)}")
                return
                
            # Convert dates safely
            try:
                df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
                df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
            except Exception as e:
                messagebox.showerror("Error", f"Invalid date format: {str(e)}")
                return
                
            # Remove rows with invalid dates
            df = df.dropna(subset=['Start Date', 'End Date'])
            
            # Calculate days remaining
            today = datetime.now()
            df['Days Remaining'] = (df['End Date'] - today).dt.days
            
            # Update display
            self._update_display(df)
            
            # Update last check time
            self.last_check_time = datetime.now()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update LGs: {str(e)}")
            
    def _update_display(self, df):
        """Update display with dataframe data"""
        try:
            # Clear existing items
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
                
            # Update counter for LGs needing attention
            urgent_count = 0
            
            # Add data to treeview
            for _, row in df.iterrows():
                days_remaining = row['Days Remaining']
                
                # Count LGs that need attention (expired or close to expiry)
                if days_remaining <= 7:  # 7 days or less remaining, or already expired
                    urgent_count += 1
                
                # Format row values
                values = [
                    row['Sequence No.'],
                    row['Vendor Name'],
                    row['LG Number'],
                    row['Start Date'],
                    row['End Date'],
                    row['Type of LG'],
                    row['Related To'],
                    days_remaining
                ]
                
                # Set tag based on days remaining
                if days_remaining < 0:
                    tag = 'expired'
                elif days_remaining <= 3:
                    tag = 'urgent'
                elif days_remaining <= 7:
                    tag = 'warning'
                else:
                    tag = 'normal'
                    
                self.results_tree.insert('', 'end', values=values, tags=(tag,))
                
            # Update notification count
            if hasattr(self.main_app, 'update_all_notifications'):
                self.main_app.update_all_notifications(urgent_count)
                
            # Configure tag colors
            self.results_tree.tag_configure('expired', foreground='red')
            self.results_tree.tag_configure('urgent', foreground='orange')
            self.results_tree.tag_configure('warning', foreground='#FF8C00')  # Dark orange
            self.results_tree.tag_configure('normal', foreground='black')
            
            # Update summary tree
            summary = df.groupby('Type of LG').agg({
                'LG Number': 'count',
                'Amount': 'sum'
            }).reset_index()
            
            for _, row in summary.iterrows():
                self.summary_tree.insert('', 'end', values=(
                    row['Type of LG'],
                    row['LG Number'],
                    f"{row['Amount']:,.2f}"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update display: {str(e)}")
    
    def check_for_updates(self):
        """Check for updates if needed"""
        if not self.last_check_time or (datetime.now() - self.last_check_time).total_seconds() > 3600:
            self.update_lgs()
