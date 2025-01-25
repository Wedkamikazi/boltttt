import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from ui.bank_accounts_tab import BankAccountsTab
from ui.clearing_tab import ClearingTab
from ui.folder_tab import FolderTab
from auth.user_management import UserManager, UserRole, User

class TestWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UI Test Window")
        self.root.geometry("800x600")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create test user
        self.test_user = User("testuser", UserRole.ADMIN, "dummy_hash")
        
        # Initialize tabs
        self.init_tabs()
        
    def init_tabs(self):
        """Initialize all tabs for testing"""
        # Bank Accounts Tab
        self.bank_tab = BankAccountsTab(self.notebook, self)
        self.notebook.add(self.bank_tab.bank_frame, text="Bank Accounts")
        
        # Clearing Tab
        self.clearing_tab = ClearingTab(self.notebook, self)
        self.notebook.add(self.clearing_tab.clearing_frame, text="Clearing")
        
        # Folder Tab
        self.folder_tab = FolderTab(self.notebook, self.test_user)
        self.notebook.add(self.folder_tab.main_frame, text="Folders")

def test_ui_components():
    """Test basic UI functionality"""
    print("\nTest Case 1: Window Creation")
    try:
        window = TestWindow()
        print("Window Creation: PASS")
        
        print("\nTest Case 2: Tab Initialization")
        # Check if all tabs are created
        if (hasattr(window, 'bank_tab') and 
            hasattr(window, 'clearing_tab') and 
            hasattr(window, 'folder_tab')):
            print("Tab Initialization: PASS")
        else:
            print("Tab Initialization: FAIL")
        
        print("\nTest Case 3: Bank Tab Components")
        # Check bank tab components
        bank_tab = window.bank_tab
        if hasattr(bank_tab, 'tree'):
            print("Bank Tab Tree: PASS")
            # Test data loading
            bank_tab.load_bank_data()
            print("Bank Data Loading: PASS")
        else:
            print("Bank Tab Components: FAIL")
        
        print("\nTest Case 4: Clearing Tab Components")
        # Check clearing tab components
        clearing_tab = window.clearing_tab
        if hasattr(clearing_tab, 'tree'):
            print("Clearing Tab Tree: PASS")
            # Test data loading
            clearing_tab.load_data()
            print("Clearing Data Loading: PASS")
        else:
            print("Clearing Tab Components: FAIL")
        
        print("\nTest Case 5: Folder Tab Components")
        # Check folder tab components
        folder_tab = window.folder_tab
        if (hasattr(folder_tab, 'company_combo') and 
            hasattr(folder_tab, 'year_combo')):
            print("Folder Tab Components: PASS")
        else:
            print("Folder Tab Components: FAIL")
        
        print("\nAll UI Tests Complete!")
        window.root.destroy()
        
    except Exception as e:
        print(f"Test Failed: {str(e)}")
        try:
            window.root.destroy()
        except:
            pass

if __name__ == '__main__':
    print("Starting UI Component Tests...")
    test_ui_components()
