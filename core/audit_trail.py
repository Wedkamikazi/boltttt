from datetime import datetime
import csv
from pathlib import Path

class AuditTrail:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.audit_file = self.base_dir / 'data/exceptions/AUDIT_LOG.csv'
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure audit directory exists"""
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)

    def log_action(self, action_data):
        """Log system action"""
        audit_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action_data.get('action', 'Unknown'),
            'reference': action_data.get('reference', 'N/A'),
            'details': action_data.get('details', ''),
            'user': action_data.get('user', 'System'),
            'status': action_data.get('status', 'Completed')
        }
        
        self._write_to_audit_log(audit_data)
        return audit_data

    def get_actions(self, reference=None, action_type=None, start_date=None, end_date=None):
        """Get audit trail entries with optional filters"""
        actions = []
        
        if self.audit_file.exists():
            with open(self.audit_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if self._matches_filters(row, reference, action_type, start_date, end_date):
                        actions.append(row)
        
        return actions

    def _matches_filters(self, row, reference=None, action_type=None, start_date=None, end_date=None):
        """Check if row matches all provided filters"""
        if reference and row['reference'] != reference:
            return False
            
        if action_type and row['action'] != action_type:
            return False
            
        if start_date or end_date:
            row_date = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            if start_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                if row_date < start:
                    return False
                    
            if end_date:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                if row_date > end:
                    return False
        
        return True

    def _write_to_audit_log(self, data):
        """Write data to audit log"""
        file_exists = self.audit_file.exists()
        
        try:
            mode = 'a' if file_exists else 'w'
            with open(self.audit_file, mode, newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['timestamp', 'action', 'reference', 'details', 'user', 'status'])
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
        except Exception as e:
            print(f"Error writing to audit log: {str(e)}")
            raise

    def export_audit_trail(self, output_file, reference=None, action_type=None, start_date=None, end_date=None):
        """Export filtered audit trail to a new file"""
        actions = self.get_actions(reference, action_type, start_date, end_date)
        
        if actions:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=actions[0].keys())
                writer.writeheader()
                writer.writerows(actions)
            return True
            
        return False
