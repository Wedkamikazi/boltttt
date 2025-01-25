from pathlib import Path
import json
from datetime import datetime
import uuid
import threading
from decimal import Decimal
import re
import html
from validation_system import ValidationSystem

class PaymentError(Exception):
    """Base class for payment processing errors"""
    pass

class ValidationError(PaymentError):
    """Validation related errors"""
    pass

class FileSystemError(PaymentError):
    """File system related errors"""
    pass

class PaymentProcessor:
    """Non-GUI version of payment system for testing"""
    
    def __init__(self, files_dir):
        """Initialize payment processor"""
        self.files_dir = Path(files_dir)
        self.payments = {}
        self.lock = threading.Lock()
        self.validation_system = ValidationSystem()
        self.temp_files = set()  # Track temporary files
        
        try:
            self.files_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileSystemError(f"Failed to create files directory: {e}")

    def process_payment(self, payment_data):
        """Process a payment request with proper error handling"""
        result = {'success': False, 'error': None, 'error_type': None}
        payment_id = None
        temp_file = None
        
        try:
            # Validate payment data
            try:
                validation_result = self.validation_system.validate_input(payment_data)
                if not validation_result['valid']:
                    raise ValidationError(validation_result['error'])
                    
                # Check CNP requirement
                if validation_result.get('cnp_required', False) and not payment_data.get('cnp_approval'):
                    raise ValidationError("CNP approval required for this payment")
            except Exception as e:
                raise ValidationError(f"Validation error: {str(e)}")

            # Generate payment ID
            payment_id = str(uuid.uuid4())
            
            with self.lock:
                try:
                    # Check for duplicate reference
                    reference = payment_data['reference']
                    if any(p['reference'] == reference for p in self.payments.values()):
                        raise ValidationError("Duplicate payment reference")

                    # Create payment record
                    payment_record = {
                        'payment_id': payment_id,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'pending',
                        **payment_data
                    }

                    # Generate temporary file first
                    temp_file = self._generate_temp_file(payment_record)
                    self.temp_files.add(temp_file)

                    # Save payment record
                    self.payments[payment_id] = payment_record

                    # Move temporary file to final location
                    final_file = self._finalize_payment_file(temp_file, payment_id)
                    
                    # Update status
                    payment_record['status'] = 'completed'
                    self.payments[payment_id] = payment_record

                    result['success'] = True
                    result['payment_id'] = payment_id

                except OSError as e:
                    raise FileSystemError(f"File system error: {str(e)}")
                except Exception as e:
                    raise PaymentError(f"Payment processing error: {str(e)}")

        except ValidationError as e:
            result['error'] = str(e)
            result['error_type'] = 'validation'
        except FileSystemError as e:
            result['error'] = str(e)
            result['error_type'] = 'filesystem'
        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = 'general'
        finally:
            # Clean up temporary file if it exists
            if temp_file and temp_file in self.temp_files:
                try:
                    if Path(temp_file).exists():
                        Path(temp_file).unlink()
                    self.temp_files.remove(temp_file)
                except:
                    pass  # Ignore cleanup errors
                    
        return result

    def _generate_temp_file(self, payment_record):
        """Generate a temporary file for the payment"""
        temp_file = self.files_dir / f"temp_{uuid.uuid4()}.json"
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(payment_record, f, indent=4)
            return temp_file
        except Exception as e:
            raise FileSystemError(f"Failed to create temporary file: {e}")

    def _finalize_payment_file(self, temp_file, payment_id):
        """Move temporary file to final location"""
        final_file = self.files_dir / f"payment_{payment_id}.json"
        
        try:
            Path(temp_file).rename(final_file)
            return final_file
        except Exception as e:
            raise FileSystemError(f"Failed to finalize payment file: {e}")

    def get_payment_status(self, payment_id):
        """Get the status of a payment"""
        return self.payments.get(payment_id, {}).get('status', 'unknown')
