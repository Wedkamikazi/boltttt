from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

class StatusTracker:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.valid_statuses = [
            'PENDING', 'VALIDATED', 'APPROVED', 'REJECTED', 
            'PROCESSING', 'COMPLETED', 'FAILED'
        ]
        
    def create_status_directory(self, reference: str) -> bool:
        """Create a directory to store status history for a payment"""
        try:
            status_dir = self.file_manager.status_dir / reference
            status_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.file_manager.log_error(f"Error creating status directory for {reference}: {str(e)}")
            return False
            
    def update_status(self, reference: str, new_status: str, 
                     reason: str = None, user: str = None) -> bool:
        """Update payment status with history tracking"""
        try:
            if new_status not in self.valid_statuses:
                self.file_manager.log_error(
                    f"Invalid status {new_status} for {reference}"
                )
                return False
                
            # Create status directory if it doesn't exist
            if not self.create_status_directory(reference):
                return False
                
            # Get current status
            current_status = self.get_status(reference)
            if current_status and current_status['status'] == new_status:
                return True  # No change needed
                
            # Create new status entry
            timestamp = datetime.now().isoformat()
            status_data = {
                'status': new_status,
                'timestamp': timestamp,
                'reason': reason,
                'user': user,
                'previous_status': current_status['status'] if current_status else None
            }
            
            # Save status update
            if not self.file_manager.save_status(status_data, reference):
                return False
                
            # Add to history
            history_file = self.file_manager.status_dir / reference / f"{timestamp}.json"
            with open(history_file, 'w') as f:
                json.dump(status_data, f, indent=4)
                
            return True
            
        except Exception as e:
            self.file_manager.log_error(f"Error updating status for {reference}: {str(e)}")
            return False
            
    def get_status(self, reference: str) -> Optional[Dict]:
        """Get current status of a payment"""
        return self.file_manager.get_status(reference)
        
    def get_status_history(self, reference: str) -> List[Dict]:
        """Get complete status history of a payment"""
        try:
            status_dir = self.file_manager.status_dir / reference
            if not status_dir.exists():
                return []
                
            history = []
            for file in sorted(status_dir.glob("*.json")):
                with open(file, 'r') as f:
                    history.append(json.load(f))
                    
            return history
            
        except Exception as e:
            self.file_manager.log_error(
                f"Error retrieving status history for {reference}: {str(e)}"
            )
            return []
            
    def get_payments_by_status(self, status: str) -> List[str]:
        """Get all payment references with a specific status"""
        try:
            if status not in self.valid_statuses:
                self.file_manager.log_error(f"Invalid status filter: {status}")
                return []
                
            def status_filter(payment_data):
                if not payment_data:
                    return False
                current_status = self.get_status(payment_data.get('reference'))
                return current_status and current_status['status'] == status
                
            return self.file_manager.list_payments(status_filter)
            
        except Exception as e:
            self.file_manager.log_error(
                f"Error retrieving payments by status {status}: {str(e)}"
            )
            return []
            
    def can_transition_to(self, current_status: str, new_status: str) -> bool:
        """Check if status transition is valid"""
        # Define valid transitions
        transitions = {
            'PENDING': ['VALIDATED', 'REJECTED'],
            'VALIDATED': ['APPROVED', 'REJECTED'],
            'APPROVED': ['PROCESSING', 'REJECTED'],
            'PROCESSING': ['COMPLETED', 'FAILED'],
            'REJECTED': [],  # Terminal state
            'COMPLETED': [],  # Terminal state
            'FAILED': ['PENDING']  # Can retry from failed
        }
        
        return (current_status in transitions and 
                new_status in transitions[current_status])

    def update_all_statuses(self) -> dict:
        """Update statuses for all payments"""
        try:
            # Get all payment references from treasury
            all_payments = self.file_manager.get_all_payments()
            
            results = {
                'updated': 0,
                'errors': 0,
                'details': []
            }
            
            for payment in all_payments:
                reference = payment.get('reference')
                if reference:
                    # Check current status and update if needed
                    current_status = self.get_status(reference)
                    if not current_status:
                        # If no status exists, set to PENDING
                        if self.update_status(reference, 'PENDING'):
                            results['updated'] += 1
                            results['details'].append(f"Set status to PENDING for {reference}")
                        else:
                            results['errors'] += 1
                            results['details'].append(f"Failed to update status for {reference}")
                        
            return results
            
        except Exception as e:
            self.file_manager.log_error(f"Error updating all statuses: {str(e)}")
            return {
                'updated': 0,
                'errors': 1,
                'details': [f"Error: {str(e)}"]
            }
