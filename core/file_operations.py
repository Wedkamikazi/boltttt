from datetime import datetime
import csv
from pathlib import Path

class FileOperations:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.file_paths = {
            'BS-SALAM': self.base_dir / 'data/bank_statements/SALAM/BS_SALAM_CURRENT.csv',
            'BS-MVNO': self.base_dir / 'data/bank_statements/mvno/BS_MVNO_CURRENT.csv',
            'CNP-SALAM': self.base_dir / 'data/cnp/SALAM/CNP_SALAM_CURRENT.csv',
            'CNP-MVNO': self.base_dir / 'data/cnp/mvno/CNP_MVNO_CURRENT.csv',
            'Treasury': self.base_dir / 'data/treasury/TREASURY_CURRENT.csv'
        }
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            'data',
            'data/bank_statements',
            'data/bank_statements/SALAM',
            'data/bank_statements/mvno',
            'data/cnp',
            'data/cnp/SALAM',
            'data/cnp/mvno',
            'data/treasury'
        ]
        for directory in directories:
            dir_path = self.base_dir / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
                # Ensure write permissions
                dir_path.chmod(0o777)

        # Ensure files exist with proper permissions
        for file_key, file_path in self.file_paths.items():
            if not file_path.exists():
                # Create empty CSV with headers
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['company', 'beneficiary', 'reference', 'amount', 'date', 'status', 'timestamp'])
                # Set file permissions
                file_path.chmod(0o666)

    def verify_payment(self, payment_data):
        """Verify payment across all relevant sheets"""
        results = {
            'matches': False,
            'details': [],
            'files': [],
            'matching_records': []
        }

        # Step 1: Check Bank Statement
        bs_result = self._check_bank_statement(payment_data)
        if bs_result['matches']:
            results['matches'] = True
            for match in bs_result['matches']:
                record = match['record']
                results['details'].append(
                    f"Match found in {match['file']}:\n"
                    f"  Reference: {record['reference']}\n"
                    f"  Amount: {record['amount']}\n"
                    f"  Date: {record['date']}\n"
                    f"  Status: {record['status']}\n"
                    f"  Timestamp: {record['timestamp']}"
                )
                results['matching_records'].append(record)
            results['files'].append(f"BS-{payment_data['company']}")

        # Add bank statement messages
        if bs_result.get('messages'):
            results['details'].extend(bs_result['messages'])

        # Step 2: Check CNP if needed (old payment)
        cnp_result = {'matches': [], 'messages': []}  # Initialize with empty result
        if self._is_old_payment(payment_data['date']):
            cnp_result = self._check_cnp(payment_data)
            if cnp_result['matches']:
                results['matches'] = True
                for match in cnp_result['matches']:
                    record = match['record']
                    results['details'].append(
                        f"Match found in {match['file']}:\n"
                        f"  Reference: {record['reference']}\n"
                        f"  Amount: {record['amount']}\n"
                        f"  Date: {record['date']}\n"
                        f"  Status: {record['status']}\n"
                        f"  Timestamp: {record['timestamp']}"
                    )
                    results['matching_records'].append(record)
                results['files'].append(f"CNP-{payment_data['company']}")

        # Add CNP messages
        if cnp_result.get('messages'):
            results['details'].extend(cnp_result['messages'])

        return results

    def _check_bank_statement(self, payment_data):
        """Check bank statement with basic validation"""
        result = {
            'matches': [],
            'messages': []
        }
        
        try:
            company = payment_data.get('company', '')
            bs_file = self.file_paths.get(f'BS-{company}')
            
            if not bs_file or not bs_file.exists():
                result['messages'].append(f"Bank statement file not found for company: {company}")
                return result
                
            with open(bs_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for record in reader:
                    if (record['reference'] == payment_data['reference'] and
                        float(record['amount']) == float(payment_data['amount'])):
                        result['matches'].append({
                            'file': f'BS-{company}',
                            'record': record
                        })
                        
        except (ValueError, KeyError) as e:
            result['messages'].append(f"Error processing bank statement: {str(e)}")
        except Exception as e:
            result['messages'].append(f"Unexpected error in bank statement check: {str(e)}")
            
        return result

    def _check_cnp(self, payment_data):
        """Check CNP with basic validation"""
        result = {
            'matches': [],
            'messages': []
        }
        
        try:
            company = payment_data.get('company', '')
            cnp_file = self.file_paths.get(f'CNP-{company}')
            
            if not cnp_file or not cnp_file.exists():
                result['messages'].append(f"CNP file not found for company: {company}")
                return result
                
            with open(cnp_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for record in reader:
                    if (record['reference'] == payment_data['reference'] and
                        float(record['amount']) == float(payment_data['amount'])):
                        result['matches'].append({
                            'file': f'CNP-{company}',
                            'record': record
                        })
                        
        except (ValueError, KeyError) as e:
            result['messages'].append(f"Error processing CNP: {str(e)}")
        except Exception as e:
            result['messages'].append(f"Unexpected error in CNP check: {str(e)}")
            
        return result

    def _check_file(self, file_key, payment_data):
        """Check payment in specific file"""
        results = {
            'matches': [],
            'messages': []
        }

        if file_key not in self.file_paths:
            results['messages'].append(f"Invalid file key: {file_key}")
            return results

        file_path = self.file_paths[file_key]
        try:
            if not file_path.exists():
                results['messages'].append(f"File not found: {file_path}")
                return results

            print(f"Checking file: {file_path}")  # Debug print
            with open(file_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    print(f"Checking row: {row}")  # Debug print
                    if self._is_matching_record(row, payment_data):
                        results['matches'].append({
                            'file': file_key,
                            'record': row
                        })
        except Exception as e:
            results['messages'].append(f"Error reading {file_key}: {str(e)}")
            print(f"Error: {str(e)}")  # Debug print

        return results

    def _is_matching_record(self, record, payment_data):
        """Check if record matches payment data"""
        try:
            # Match reference number (exact match required)
            if record['reference'].strip() != payment_data['reference'].strip():
                return False

            # Match amount (with threshold handling)
            amount = float(record['amount'])
            payment_amount = float(payment_data['amount'])
            if amount > 15000:
                # 1% tolerance for amounts over 15000
                difference = abs(amount - payment_amount) / amount
                if difference > 0.01:
                    return False
            elif amount != payment_amount:
                return False

            return True
        except (KeyError, ValueError) as e:
            return False

    def _is_old_payment(self, payment_date):
        """Check if payment is from previous month"""
        payment_date = datetime.strptime(payment_date, '%Y-%m-%d')
        current_date = datetime.now()
        
        return (payment_date.year < current_date.year or 
                payment_date.month < current_date.month)

    def get_file_path(self, file_key):
        """Get absolute path for a file"""
        return self.file_paths.get(file_key)

    def open_file(self, file_key):
        """Get the path for a file and ensure its directory exists"""
        if file_key not in self.file_paths:
            raise ValueError(f"Invalid file key: {file_key}")
            
        file_path = self.file_paths[file_key]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path

    def save_payment(self, payment_data):
        """Save payment to Treasury with Under Process status"""
        try:
            file_path = self.file_paths['Treasury']
            fieldnames = ['company', 'beneficiary', 'reference', 'amount', 'date', 'status', 'timestamp']
            
            # Read existing payments
            existing_payments = []
            if file_path.exists():
                with open(file_path, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    existing_payments = list(reader)
            
            # Add new payment
            new_payment = {
                'reference': payment_data['reference'],
                'amount': payment_data['amount'],
                'date': payment_data['date'],
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'company': payment_data['company'],
                'beneficiary': payment_data['beneficiary']
            }
            existing_payments.append(new_payment)
            
            # Write all payments back to file
            with open(file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(existing_payments)
            
            return True, "Payment added to Treasury successfully"
        except Exception as e:
            error_msg = f"Error saving to Treasury: {str(e)}"
            return False, error_msg

    def log_error(self, error_message: str):
        """Log an error message to the error log file"""
        try:
            log_dir = self.base_dir / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / 'error.log'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] ERROR: {error_message}\n")
                
        except Exception as e:
            print(f"Failed to log error: {str(e)}")
