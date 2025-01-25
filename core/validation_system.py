from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import re
from pathlib import Path
import json
import os

class ValidationSystem:
    def __init__(self):
        self.threshold_amount = Decimal('15000.00')
        self.tolerance = Decimal('0.01')  # 1% tolerance
        self.base_dir = Path(__file__).parent.parent
        self.allowed_companies = ['SALAM', 'MVNO']

    def validate_company(self, company):
        """Validate company name"""
        if not company or not isinstance(company, str):
            return False, "Company must be a non-empty string"
            
        company = company.strip().upper()
        if company not in self.allowed_companies:
            return False, f"Company must be one of {self.allowed_companies}"
            
        return True, None

    def validate_beneficiary(self, beneficiary):
        """Validate beneficiary details"""
        if not isinstance(beneficiary, dict):
            return False, "Beneficiary must be a dictionary"
            
        required_fields = ['name', 'account', 'bank']
        if not all(field in beneficiary for field in required_fields):
            return False, "Missing required beneficiary fields"
            
        # Validate name
        name = beneficiary['name']
        if not name or not isinstance(name, str):
            return False, "Invalid beneficiary name"
            
        # Check name length
        if len(name.strip()) < 2:
            return False, "Beneficiary name too short"
            
        if len(name.strip()) > 100:
            return False, "Beneficiary name too long"
            
        # Check for special characters in name
        if re.search(r'[<>{}\\[\]~`!@#$%^&*()+=]', name):
            return False, "Beneficiary name contains invalid characters"
            
        # Validate account (IBAN format for Saudi Arabia)
        account = beneficiary['account']
        if not isinstance(account, str):
            return False, "Account must be a string"
            
        # Simplified IBAN check - just check format
        if not re.match(r'^SA\d{22}$', account):
            return False, "Invalid IBAN format"
            
        # Validate bank name
        bank = beneficiary['bank']
        if not bank or not isinstance(bank, str):
            return False, "Invalid bank name"
            
        if len(bank.strip()) < 2:
            return False, "Bank name too short"
            
        return True, None

    def validate_reference(self, reference):
        """Validate reference number format"""
        if not reference or not isinstance(reference, str):
            return False, "Reference must be a non-empty string"
            
        # Format: XXX-YYYY-NNNN
        if not re.match(r'^[A-Z]{3}-\d{4}-\d{4}$', reference):
            return False, "Reference must be in format XXX-YYYY-NNNN"
            
        # Extract year
        try:
            year = int(reference.split('-')[1])
            current_year = datetime.now().year
            if year < current_year - 1 or year > current_year + 1:
                return False, "Reference year must be within ±1 year of current year"
        except (IndexError, ValueError):
            return False, "Invalid reference year format"
            
        return True, None

    def validate_amount(self, amount):
        """Validate payment amount"""
        try:
            # Convert to Decimal if not already
            if not isinstance(amount, Decimal):
                if isinstance(amount, (int, float)):
                    amount = Decimal(str(amount))
                elif isinstance(amount, str):
                    amount = Decimal(amount)
                else:
                    return False, "Invalid amount type"

            # Check if amount is positive
            if amount <= Decimal('0'):
                return False, "Amount must be greater than 0"
                
            # Check if amount is within limits
            if amount > Decimal('1000000'):
                return False, "Amount exceeds maximum limit"
                
            return True, None
            
        except (InvalidOperation, ValueError, TypeError):
            return False, "Invalid amount format"

    def validate_date(self, date_obj):
        """Validate payment date"""
        if not isinstance(date_obj, datetime):
            return False, "Date must be a datetime object"
            
        current_date = datetime.now().date()
        payment_date = date_obj.date()
        
        # Check if date is not too old (more than 1 year)
        if payment_date < (current_date - timedelta(days=365)):
            return False, "Date too old"
            
        # Check if date is not in future
        if payment_date > current_date:
            return False, "Future date not allowed"
            
        return True, None

    def validate_payment_data(self, data):
        """Validate complete payment data"""
        if not isinstance(data, dict):
            return False, "Payment data must be a dictionary"
            
        required_fields = ['company', 'reference', 'amount', 'date', 'beneficiary']
        
        # Check all required fields exist
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
            
        # Validate each field
        company_valid, company_error = self.validate_company(data['company'])
        if not company_valid:
            return False, company_error
            
        ref_valid, ref_error = self.validate_reference(data['reference'])
        if not ref_valid:
            return False, ref_error
            
        amount_valid, amount_error = self.validate_amount(data['amount'])
        if not amount_valid:
            return False, amount_error
            
        date_valid, date_error = self.validate_date(data['date'])
        if not date_valid:
            return False, date_error
            
        ben_valid, ben_error = self.validate_beneficiary(data['beneficiary'])
        if not ben_valid:
            return False, ben_error
            
        return True, None

    def validate_input(self, data):
        """Validate all input fields and return validation result"""
        result = {'valid': True, 'error': None, 'cnp_required': False}
        
        # Validate company
        company_valid, company_error = self.validate_company(data.get('company'))
        if not company_valid:
            result['valid'] = False
            result['error'] = company_error
            return result
            
        # Validate beneficiary
        ben_valid, ben_error = self.validate_beneficiary(data.get('beneficiary'))
        if not ben_valid:
            result['valid'] = False
            result['error'] = ben_error
            return result
            
        # Validate reference number
        ref_valid, ref_error = self.validate_reference(data.get('reference'))
        if not ref_valid:
            result['valid'] = False
            result['error'] = ref_error
            return result
            
        # Validate amount
        amount_valid, amount_error = self.validate_amount(data.get('amount'))
        if not amount_valid:
            result['valid'] = False
            result['error'] = amount_error
            return result
            
        # Validate date
        date_valid, date_error = self.validate_date(data.get('date'))
        if not date_valid:
            result['valid'] = False
            result['error'] = date_error
            return result
            
        result['cnp_required'] = date_valid and date_error is None
        return result

    def cross_reference_check(self, payment, file_handler):
        """Check for duplicate references in existing files"""
        result = {'valid': True, 'error': None}
        
        try:
            existing_payments = file_handler.read_treasury_file()
            for existing in existing_payments:
                if existing['reference'] == payment['reference']:
                    result['valid'] = False
                    result['error'] = f"Reference {payment['reference']} already exists in the system"
                    break
        except Exception as e:
            result['valid'] = False
            result['error'] = f"Error checking reference: {str(e)}"
            
        return result

    def _check_file(self, file_type, data, results, file_handler):
        """Check for matches in specific file"""
        try:
            file_data = file_handler.read_file(file_type)
            for record in file_data:
                if self._is_matching_record(record, data):
                    match = {
                        'file': file_type,
                        'reference': record['reference'],
                        'amount': record['amount'],
                        'date': record['date']
                    }
                    results['matches'].append(match)
        except Exception as e:
            results['warnings'].append(f"Error checking {file_type}: {str(e)}")

    def _is_matching_record(self, record, data):
        """Check if record matches the input data"""
        # Reference match
        if record['reference'].strip() == data['reference'].strip():
            # For amounts > 15000, allow 1% tolerance
            amount = Decimal(record['amount'])
            input_amount = Decimal(data['amount'])
            
            if amount > self.threshold_amount:
                difference = abs(amount - input_amount) / amount
                return difference <= self.tolerance
            else:
                return amount == input_amount
        return False

    def validate_status_update(self, payment_data, file_paths):
        """Validate status update data and files"""
        errors = []
        
        # Validate file paths
        if not file_paths:
            errors.append("No file paths provided")
            return {'valid': False, 'errors': errors}
            
        for path in file_paths:
            if not self._validate_file_path(path):
                errors.append(f"Invalid file path: {path}")
            elif not self._validate_json_file(path):
                errors.append(f"Invalid JSON file: {path}")
                
        # Validate payment data
        if not isinstance(payment_data, dict):
            errors.append("Payment data must be a dictionary")
        else:
            required_fields = ['reference', 'amount', 'date', 'status', 'company']
            for field in required_fields:
                if field not in payment_data:
                    errors.append(f"Missing required field: {field}")
                elif not payment_data[field]:
                    errors.append(f"{field.title()} cannot be empty")
                    
            # Validate status
            if 'status' in payment_data:
                status = payment_data['status']
                if not isinstance(status, str):
                    errors.append("Status must be a string")
                elif status not in ['Pending', 'Under Process', 'Completed', 'Rejected']:
                    errors.append("Invalid status value")
                    
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
        
    def _validate_file_path(self, path_str):
        """Validate file path exists"""
        try:
            path = Path(path_str)
            if not path.exists():
                return False
            return True
        except Exception:
            return False
            
    def _validate_json_file(self, path_str):
        """Validate JSON file path and content"""
        try:
            path = Path(path_str)
            if not path.exists() or path.suffix != '.json':
                return False
                
            with open(path, 'r', encoding='utf-8') as f:
                json.load(f)  # Try to parse JSON
            return True
        except Exception:
            return False

    def update_payment_status(self, payment_data, file_paths):
        """Update payment status"""
        validation_result = self.validate_status_update(payment_data, file_paths)
        if not validation_result['valid']:
            return {'updated': 0, 'errors': validation_result['errors']}
            
        updated_count = 0
        errors = []
        
        try:
            for path in file_paths:
                if not self._validate_file_path(path) or not self._validate_json_file(path):
                    continue
                    
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    errors.append(f"Invalid JSON format in file: {path}")
                    continue
                    
                if 'payments' not in data:
                    errors.append(f"Invalid data structure in file: {path}")
                    continue
                    
                modified = False
                for payment in data['payments']:
                    if payment.get('reference') == payment_data['reference']:
                        payment['status'] = payment_data['status']
                        modified = True
                        updated_count += 1
                        
                if modified:
                    try:
                        with open(path, 'w') as f:
                            json.dump(data, f, indent=4)
                    except Exception as e:
                        errors.append(f"Error writing to file {path}: {str(e)}")
                        updated_count -= 1
                        
        except Exception as e:
            errors.append(f"Error updating status: {str(e)}")
            
        return {
            'updated': updated_count,
            'errors': errors
        }
