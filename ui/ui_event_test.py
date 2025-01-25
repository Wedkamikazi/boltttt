import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from ui.bank_accounts_tab import BankAccountsTab
from ui.clearing_tab import ClearingTab
from ui.folder_tab import FolderTab
from auth.user_management import UserManager, UserRole, User
from utils.folder_system import Company

class MockEvent:
    """Mock event for testing UI callbacks"""
    def __init__(self, widget=None):
        self.widget = widget

class UIEventTests:
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
    
    def test_bank_tab_events(self):
        """Test bank tab UI events"""
        print("\nTest Case 1: Bank Tab Events")
        try:
            # Test company change event
            self.bank_tab.company_var.set("MVNO")
            self.bank_tab.on_company_change()
            print("Company Change Event: PASS")
            
            # Test account selection
            if hasattr(self.bank_tab, 'tree'):
                mock_event = MockEvent(self.bank_tab.tree)
                self.bank_tab.on_account_click(mock_event)
                print("Account Selection Event: PASS")
        except Exception as e:
            print(f"Bank Tab Events Failed: {str(e)}")
    
    def test_clearing_tab_events(self):
        """Test clearing tab UI events"""
        print("\nTest Case 2: Clearing Tab Events")
        try:
            # Test company change
            self.clearing_tab.company_var.set("MVNO")
            self.clearing_tab.on_company_change()
            print("Company Change Event: PASS")
            
            # Test search functionality
            self.clearing_tab.search_var.set("test")
            self.clearing_tab.on_search()
            print("Search Event: PASS")
            
            # Test reconciliation change
            self.clearing_tab.reconcile_var.set("Month")  # Changed from "Yes" to "Month"
            mock_event = MockEvent()
            self.clearing_tab.on_reconcile_change(mock_event)
            print("Reconciliation Change Event: PASS")
            
            # Test transaction summary
            if hasattr(self.clearing_tab, 'total_amount_var'):
                current_total = self.clearing_tab.total_amount_var.get()
                print(f"Transaction Summary: PASS - {current_total}")
            else:
                print("Transaction Summary: FAIL - No total amount variable")
        except Exception as e:
            print(f"Clearing Tab Events Failed: {str(e)}")
    
    def test_folder_tab_events(self):
        """Test folder tab UI events"""
        print("\nTest Case 3: Folder Tab Events")
        try:
            # Test company selection
            self.folder_tab.company_var.set(Company.MVNO.value)
            mock_event = MockEvent()
            self.folder_tab.on_company_select(mock_event)
            print("Company Selection Event: PASS")
            
            # Test folder check
            self.folder_tab.check_missing_folders()
            print("Folder Check Event: PASS")
        except Exception as e:
            print(f"Folder Tab Events Failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all UI event tests"""
        try:
            print("Starting UI Event Tests...")
            self.test_bank_tab_events()
            self.test_clearing_tab_events()
            self.test_folder_tab_events()
            print("\nAll UI Event Tests Complete!")
        except Exception as e:
            print(f"Test Suite Failed: {str(e)}")
        finally:
            self.root.destroy()

if __name__ == '__main__':
    test_suite = UIEventTests()
    test_suite.run_all_tests()
