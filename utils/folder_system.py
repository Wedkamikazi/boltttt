from enum import Enum
from datetime import datetime
from pathlib import Path
import calendar
import subprocess

class Company(Enum):
    """Supported companies"""
    SALAM = "Salam"  # Fixed spelling
    MVNO = "MVNO"

class FolderManager:
    """Manages company folder structure and validation"""
    def __init__(self, root_dir="c:/WedxDev/KK/Companies"):
        self.root_dir = Path(root_dir)
        self.start_year = 2024
        
    def get_folder_path(self, company: Company, year: int, month: str) -> Path:
        """Generate full path for a specific company/year/month folder"""
        return self.root_dir / company.value / str(year) / month
        
    def check_folder_exists(self, company: Company, year: int, month: str) -> bool:
        """Check if a specific folder exists"""
        path = self.get_folder_path(company, year, month)
        return path.exists()
        
    def create_folder(self, company: Company, year: int, month: str) -> bool:
        """Create a folder if it doesn't exist"""
        path = self.get_folder_path(company, year, month)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
            
    def get_missing_folders(self, company: Company = None) -> dict:
        """Get all missing folders up to current date"""
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        missing = {}
        companies = [company] if company else list(Company)
        
        for comp in companies:
            comp_missing = []
            for year in range(self.start_year, current_year + 1):
                # Determine how many months to check
                if year == current_year:
                    months_to_check = range(1, current_month + 1)
                else:
                    months_to_check = range(1, 13)
                    
                for month_num in months_to_check:
                    month_name = calendar.month_name[month_num]
                    if not self.check_folder_exists(comp, year, month_name):
                        comp_missing.append(f"{month_name} {year}")
            
            if comp_missing:
                missing[comp.value] = comp_missing
                
        return missing
        
    def get_available_years(self) -> list:
        """Get list of years from start year to current year"""
        current_year = datetime.now().year
        return list(range(self.start_year, current_year + 1))
        
    def get_months(self) -> list:
        """Get list of all months"""
        return [calendar.month_name[i] for i in range(1, 13)]
        
    def open_folder(self, company: Company, year: int, month: str) -> bool:
        """Open folder in system file explorer"""
        path = self.get_folder_path(company, year, month)
        if not path.exists():
            return False
            
        try:
            subprocess.Popen(['explorer', str(path)])
            return True
        except Exception:
            return False
