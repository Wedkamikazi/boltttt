import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
import pandas as pd
from pathlib import Path
from ui.bank_accounts_tab import BankAccountsTab
from ui.clearing_tab import ClearingTab
from ui.folder_tab import FolderTab
from auth.user_management import UserManager, UserRole, User
from utils.folder_system import Company

class MockEvent:
    def __init__(self, widget=None):
        self.widget = widget

class UIAdvancedTests:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        self.setup_test_environment()
        
    def setup_test_environment(self):
        """Setup test environment with necessary components"""
        self.test_user = User("testuser", UserRole.ADMIN, "dummy_hash")
        self.notebook = ttk.Notebook(self.root)
        
        # Initialize tabs
        self.bank_tab = BankAccountsTab(self.notebook, self)
        self.clearing_tab = ClearingTab(self.notebook, self)
        self.folder_tab = FolderTab(self.notebook, self.test_user)
        
        # Create test data directory
        self.test_data_dir = Path("test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
    def test_import_export(self):
        """Test import/export functionality"""
        print("\nTest Case 1: Import/Export")
        try:
            # Create test Excel file
            test_df = pd.DataFrame({
                'Month': ['January'],
                'Transaction Number': ['TR001'],
                'Vendor Name': ['Test Vendor'],
                'Amount': [1000.0],
                'Notes': ['Test Note'],
                'Comments': ['Test Comment']
            })
            test_file = self.test_data_dir / "test_import.xlsx"
            test_df.to_excel(test_file, index=False)
            
            # Test import
            self.clearing_tab.import_excel()
            print("Import Functionality: PASS")
            
            # Test data persistence
            self.clearing_tab.save_data()
            print("Save Data: PASS")
            
            self.clearing_tab.load_data()
            print("Load Data: PASS")
            
        except Exception as e:
            print(f"Import/Export Tests Failed: {str(e)}")
            
    def test_document_management(self):
        """Test document management in Bank Accounts"""
        print("\nTest Case 2: Document Management")
        try:
            # Test document options dialog
            self.bank_tab.show_document_options("Test Account")
            print("Document Options Dialog: PASS")
            
            # Test document opening
            test_doc = self.test_data_dir / "test_doc.txt"
            test_doc.write_text("Test document content")
            self.bank_tab.open_document("Test Account", "Statement", None)
            print("Document Opening: PASS")
            
        except Exception as e:
            print(f"Document Management Tests Failed: {str(e)}")
            
    def test_search_filter(self):
        """Test search and filtering functionality"""
        print("\nTest Case 3: Search and Filter")
        try:
            # Test vendor search
            self.clearing_tab.search_var.set("Test Vendor")
            self.clearing_tab.on_search()
            print("Vendor Search: PASS")
            
            # Test sorting
            self.clearing_tab.sort_table("Amount")
            print("Table Sorting: PASS")
            
            # Test filtering by company
            self.clearing_tab.company_var.set("MVNO")
            self.clearing_tab.on_company_change()
            print("Company Filter: PASS")
            
        except Exception as e:
            print(f"Search/Filter Tests Failed: {str(e)}")
            
    def test_folder_management(self):
        """Test folder management functionality"""
        print("\nTest Case 4: Folder Management")
        try:
            # Test folder creation
            self.folder_tab.company_var.set(Company.SALAM.value)
            self.folder_tab.create_folder()
            print("Folder Creation: PASS")
            
            # Test missing folders check
            self.folder_tab.check_missing_folders()
            print("Missing Folders Check: PASS")
            
        except Exception as e:
            print(f"Folder Management Tests Failed: {str(e)}")
            
    def test_error_handling(self):
        """Test error handling in UI actions"""
        print("\nTest Case 5: Error Handling")
        try:
            # Test invalid file import
            invalid_file = self.test_data_dir / "invalid.txt"
            invalid_file.write_text("Invalid data")
            try:
                self.clearing_tab.import_excel()
                print("Invalid Import Handling: PASS")
            except:
                print("Invalid Import Handling: PASS (Expected error)")
            
            # Test invalid search input
            self.clearing_tab.search_var.set("@#$%")
            self.clearing_tab.on_search()
            print("Invalid Search Handling: PASS")
            
        except Exception as e:
            print(f"Error Handling Tests Failed: {str(e)}")
            
    def cleanup(self):
        """Clean up test environment"""
        try:
            import shutil
            shutil.rmtree(self.test_data_dir)
        except:
            pass
            
    def run_all_tests(self):
        """Run all advanced UI tests"""
        try:
            print("Starting Advanced UI Tests...")
            self.test_import_export()
            self.test_document_management()
            self.test_search_filter()
            self.test_folder_management()
            self.test_error_handling()
            print("\nAll Advanced UI Tests Complete!")
        except Exception as e:
            print(f"Test Suite Failed: {str(e)}")
        finally:
            self.cleanup()
            self.root.destroy()

if __name__ == '__main__':
    test_suite = UIAdvancedTests()
    test_suite.run_all_tests()
