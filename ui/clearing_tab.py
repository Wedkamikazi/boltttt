import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import re

class ClearingTab:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.clearing_frame = ttk.Frame(parent)
        self.clearing_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Data storage
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data" / "clearing"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # GL Account mapping
        self.gl_accounts = {
            'Salam': '10258',
            'MVNO': '10226'
        }
        
        # Initialize data
        self.df = pd.DataFrame(columns=[
            'Month', 'Transaction Number', 'Vendor Name', 
            'Amount', 'Notes', 'Comments'
        ])
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface components"""
        # Top control frame
        control_frame = ttk.Frame(self.clearing_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Company selection
        ttk.Label(control_frame, text="Select Company:").pack(side=tk.LEFT, padx=5)
        self.company_var = tk.StringVar(value="Salam")
        company_combo = ttk.Combobox(control_frame, textvariable=self.company_var,
                                   values=["Salam", "MVNO"], state="readonly")
        company_combo.pack(side=tk.LEFT, padx=5)
        company_combo.bind('<<ComboboxSelected>>', self.on_company_change)
        
        # Import Excel button
        ttk.Button(control_frame, text="Import Excel",
                  command=self.import_excel).pack(side=tk.RIGHT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.clearing_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search box
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Search column selection
        ttk.Label(search_frame, text="in:").pack(side=tk.LEFT, padx=5)
        self.search_column_var = tk.StringVar(value="All Columns")
        search_column_combo = ttk.Combobox(search_frame, 
                                         textvariable=self.search_column_var,
                                         values=["All Columns", "Month", 
                                                "Transaction Number", "Vendor Name"],
                                         state="readonly")
        search_column_combo.pack(side=tk.LEFT, padx=5)
        
        # Reconcile dropdown
        ttk.Label(search_frame, text="Reconcile By:").pack(side=tk.LEFT, padx=5)
        self.reconcile_var = tk.StringVar(value="Month")
        reconcile_combo = ttk.Combobox(search_frame, 
                                     textvariable=self.reconcile_var,
                                     values=["Month", "Transaction Number", 
                                            "Vendor Name"],
                                     state="readonly")
        reconcile_combo.pack(side=tk.LEFT, padx=5)
        reconcile_combo.bind('<<ComboboxSelected>>', self.on_reconcile_change)
        
        # Create table
        self.setup_table()
        
        # Summary frame
        summary_frame = ttk.LabelFrame(self.clearing_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Total amount
        self.total_amount_var = tk.StringVar(value="Total Amount: SAR 0.00")
        ttk.Label(summary_frame, 
                 textvariable=self.total_amount_var).pack(side=tk.LEFT, padx=20)
        
        # Transaction count
        self.transaction_count_var = tk.StringVar(value="Transactions: 0")
        ttk.Label(summary_frame, 
                 textvariable=self.transaction_count_var).pack(side=tk.LEFT, padx=20)
        
        # Vendor search button
        ttk.Button(summary_frame, text="Vendor Search",
                  command=self.show_vendor_search).pack(side=tk.RIGHT, padx=5)
        
    def setup_table(self):
        """Setup the clearing transactions table"""
        # Create table frame with scrollbar
        table_frame = ttk.Frame(self.clearing_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("Month", "Transaction Number", "Vendor Name", 
                  "Amount", "Notes", "Comments")
        self.tree = ttk.Treeview(table_frame, columns=columns,
                                show="headings", selectmode="browse")
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col,
                            command=lambda c=col: self.sort_table(c))
            self.tree.column(col, width=100)
        
        # Configure scrollbars
        self.tree.configure(yscrollcommand=y_scrollbar.set,
                          xscrollcommand=x_scrollbar.set)
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Pack tree
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure column formats
        self.column_formats = {
            'Month': str,
            'Transaction Number': str,
            'Vendor Name': str,
            'Amount': lambda x: f"{float(str(x).replace(',', '')):,.2f}",
            'Notes': str,
            'Comments': str
        }
        
    def import_excel(self):
        """Import data from Excel file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx;*.xls")]
            )
            
            if filename:
                # Read Excel file
                df = pd.read_excel(filename)
                
                # Process data
                self.df = self.process_excel_data(df)
                
                # Save processed data
                self.save_data()
                
                # Update table
                self.update_table()
                self.update_summary()
                
                messagebox.showinfo("Success", "Data imported successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import Excel file: {str(e)}")
            
    def save_data(self):
        """Save data to JSON file"""
        try:
            company = self.company_var.get().lower()
            file_path = self.data_dir / f"{company}_clearing.json"
            
            # Convert DataFrame to dict
            data = {
                'last_updated': datetime.now().isoformat(),
                'records': self.df.to_dict('records')
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            
    def load_data(self):
        """Load data from JSON file"""
        try:
            company = self.company_var.get().lower()
            file_path = self.data_dir / f"{company}_clearing.json"
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.df = pd.DataFrame(data.get('records', []))
            else:
                self.df = pd.DataFrame(columns=[
                    'Month', 'Transaction Number', 'Vendor Name', 
                    'Amount', 'Notes', 'Comments'
                ])
                
            self.update_table()
            self.update_summary()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.df = pd.DataFrame(columns=[
                'Month', 'Transaction Number', 'Vendor Name', 
                'Amount', 'Notes', 'Comments'
            ])
            
    def update_table(self):
        """Update the treeview with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if self.df is None or len(self.df) == 0:
            self.total_amount_var.set("Total Amount: SAR 0.00")
            self.transaction_count_var.set("Transactions: 0")
            return
            
        # Simple and fast search implementation
        filtered_df = self.df.copy()
        search_text = self.search_var.get().strip()
        if search_text:
            filtered_df = filtered_df[
                filtered_df.astype(str).apply(
                    lambda x: x.str.contains(search_text, case=False, na=False)
                ).any(axis=1)
            ]
            
        # Calculate total amount
        try:
            # Convert amount strings to numeric, handling commas
            amounts = filtered_df['Amount'].apply(lambda x: float(str(x).replace(',', '')))
            total_amount = amounts.sum()
            self.total_amount_var.set(f"Total Amount: SAR {total_amount:,.2f}")
        except Exception as e:
            print(f"Error calculating total: {e}")
            self.total_amount_var.set("Total Amount: SAR 0.00")
            
        # Bulk insert for better performance
        for _, row in filtered_df.iterrows():
            try:
                values = []
                for col in self.tree['columns']:
                    formatter = self.column_formats.get(col, str)
                    try:
                        value = formatter(row[col])
                    except:
                        value = str(row[col])
                    values.append(value)
                self.tree.insert('', 'end', values=values)
            except Exception as e:
                print(f"Error inserting row: {e}")
                continue
                
        # Update transaction count
        self.transaction_count_var.set(f"Transactions: {len(filtered_df)}")
        
    def update_summary(self):
        """Update the summary information"""
        try:
            # Calculate total amount
            total = self.df['Amount'].sum() if not self.df.empty else 0
            self.total_amount_var.set(f"Total Amount: SAR {total:,.2f}")
            
            # Update transaction count
            count = len(self.df) if not self.df.empty else 0
            self.transaction_count_var.set(f"Transactions: {count}")
        except Exception as e:
            print(f"Error updating summary: {str(e)}")
            
    def sort_table(self, col):
        """Sort treeview by column"""
        if self.df is None or len(self.df) == 0:
            return
            
        ascending = True
        if hasattr(self, '_last_sort') and self._last_sort == (col, True):
            ascending = False
            
        try:
            if col == 'Amount':
                # Convert amount strings to numeric for sorting
                self.df['Amount'] = self.df['Amount'].apply(
                    lambda x: float(str(x).replace(',', '')) if pd.notnull(x) else 0.0
                )
                self.df = self.df.sort_values(by=col, ascending=ascending)
                # Convert back to string format
                self.df['Amount'] = self.df['Amount'].apply(
                    lambda x: f"{float(x):,.2f}" if pd.notnull(x) else "0.00"
                )
            else:
                self.df = self.df.sort_values(by=col, ascending=ascending, na_position='last')
                
            self._last_sort = (col, ascending)
            self.update_table()
        except Exception as e:
            print(f"Sort error: {e}")
            
    def on_search(self, *args):
        """Handle search input - simple implementation without validation"""
        self.update_table()
        
    def load_company_data(self, company):
        """Load data for selected company"""
        try:
            file_path = self.data_dir / f"{company.lower()}_clearing.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.df = pd.DataFrame(data.get('data', []))
            else:
                self.df = pd.DataFrame()
            self.update_table()
        except Exception as e:
            print(f"Error loading company data: {e}")
            self.df = pd.DataFrame()
            self.update_table()
            
    def on_company_change(self, event=None):
        """Handle company selection change"""
        self.load_data()
        
    def on_reconcile_change(self, event=None):
        """Handle reconciliation option change"""
        try:
            self.update_table()  # Update the table display
            self.update_summary()  # Update the summary information
        except Exception as e:
            print(f"Error in reconciliation change: {str(e)}")
            
    def show_vendor_search(self):
        """Show vendor search dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Vendor Search")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create frames
        search_frame = ttk.Frame(dialog, padding="10")
        search_frame.pack(fill=tk.X)
        
        results_frame = ttk.Frame(dialog, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search box
        ttk.Label(search_frame, text="Vendor Name:").pack(side=tk.LEFT, padx=5)
        vendor_var = tk.StringVar()
        vendor_entry = ttk.Entry(search_frame, textvariable=vendor_var)
        vendor_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Results list
        results_tree = ttk.Treeview(results_frame, columns=("Vendor", "Transactions"),
                                  show="headings")
        results_tree.heading("Vendor", text="Vendor Name")
        results_tree.heading("Transactions", text="Transaction Count")
        results_tree.pack(fill=tk.BOTH, expand=True)
        
        def update_suggestions(*args):
            # Clear existing items
            for item in results_tree.get_children():
                results_tree.delete(item)
                
            search_text = vendor_var.get().strip().lower()
            if not search_text:
                return
                
            # Get matching vendors and their transaction counts
            vendors = self.df[self.df['Vendor Name'].str.lower().str.contains(
                search_text, na=False)]
            vendor_counts = vendors['Vendor Name'].value_counts()
            
            # Update results
            for vendor, count in vendor_counts.items():
                results_tree.insert('', 'end', values=(vendor, f"{count} transactions"))
                
        vendor_var.trace('w', update_suggestions)
        
        def on_vendor_select(event):
            selection = results_tree.selection()
            if not selection:
                return
                
            vendor = results_tree.item(selection[0])['values'][0]
            show_vendor_details(vendor, dialog)
            
        results_tree.bind('<Double-1>', on_vendor_select)
        
    def show_vendor_details(self, vendor_name, parent_dialog):
        """Show detailed transactions for selected vendor"""
        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"Transactions - {vendor_name}")
        dialog.geometry("800x600")
        dialog.transient(parent_dialog)
        
        # Get vendor transactions
        vendor_df = self.df[self.df['Vendor Name'] == vendor_name]
        
        # Create table
        columns = ("Month", "Transaction Number", "Amount", "Notes")
        tree = ttk.Treeview(dialog, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        # Add data
        for _, row in vendor_df.iterrows():
            values = [
                row['Month'],
                row['Transaction Number'],
                f"{row['Amount']:,.2f}",
                row['Notes']
            ]
            tree.insert('', 'end', values=values)
            
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary
        total = vendor_df['Amount'].sum()
        count = len(vendor_df)
        
        summary_frame = ttk.Frame(dialog, padding="10")
        summary_frame.pack(fill=tk.X)
        
        ttk.Label(summary_frame,
                 text=f"Total Amount: SAR {total:,.2f}").pack(side=tk.LEFT, padx=20)
        ttk.Label(summary_frame,
                 text=f"Total Transactions: {count}").pack(side=tk.LEFT, padx=20)
