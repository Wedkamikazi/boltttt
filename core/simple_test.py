from validation_system import ValidationSystem
from datetime import datetime

def test_basic_validation():
    """Test basic validation with simple rules"""
    validation = ValidationSystem()
    
    # Test Case 1: Valid Payment Data
    test_data = {
        'company': 'SALAM',
        'beneficiary': 'Test Company',
        'reference': 'ABC-2024-0001',
        'amount': '100.00',
        'date': '2024-01-18'
    }
    
    result = validation.validate_input(test_data)
    print("\nTest Case 1: Valid Payment Data")
    print(f"Result: {'PASS' if result['valid'] else 'FAIL'}")
    print(f"Error: {result['error']}")
    
    # Test Case 2: Missing Data
    test_data_missing = {
        'company': '',
        'beneficiary': '',
        'reference': '',
        'amount': '',
        'date': ''
    }
    
    result = validation.validate_input(test_data_missing)
    print("\nTest Case 2: Missing Data")
    print(f"Result: {'PASS' if not result['valid'] else 'FAIL'}")
    print(f"Error: {result['error']}")

    # Test Case 3: Invalid Reference Format
    test_data_invalid_ref = test_data.copy()
    test_data_invalid_ref['reference'] = '123-456'  # Wrong format
    
    result = validation.validate_input(test_data_invalid_ref)
    print("\nTest Case 3: Invalid Reference Format")
    print(f"Result: {'PASS' if not result['valid'] else 'FAIL'}")
    print(f"Error: {result['error']}")

    # Test Case 4: Invalid Amount
    test_data_invalid_amount = test_data.copy()
    test_data_invalid_amount['amount'] = '-100.00'  # Negative amount
    
    result = validation.validate_input(test_data_invalid_amount)
    print("\nTest Case 4: Invalid Amount")
    print(f"Result: {'PASS' if not result['valid'] else 'FAIL'}")
    print(f"Error: {result['error']}")

if __name__ == '__main__':
    print("Starting Simple Validation Tests...")
    test_basic_validation()
    print("\nTesting Complete!")
