# Payment Processing System

## Overview
The Payment Processing System is a comprehensive solution for managing and tracking payments, bank statements, and related financial operations.

## Features
- Payment processing and validation
- Bank statement reconciliation
- Letter of Guarantee (LG) management
- Task management and tracking
- Audit trail logging
- Exception handling
- File operations management

## Directory Structure
```
PA SYS/
├── main.py                    # Main entry point
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── auth/                     # Authentication module
├── core/                     # Core system modules
│   ├── validation_system.py
│   ├── file_operations.py
│   ├── status_tracker.py
│   ├── exception_handler.py
│   └── audit_trail.py
├── ui/                       # UI components
│   ├── bank_accounts_tab.py
│   ├── clearing_tab.py
│   ├── folder_tab.py
│   ├── todo_tab.py
│   └── lg_operations.py
├── utils/                    # Support modules
│   ├── payment_processor.py
│   ├── folder_system.py
│   └── todo_system.py
└── data/                     # Data directories
    ├── Companies/
    ├── treasury/
    ├── bank_statements/
    ├── cnp/
    ├── exceptions/
    ├── todo_data.json
    └── treasury_current.csv
```

## Installation
1. Ensure Python 3.8+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run the system: `python main.py`

## Dependencies
- tkcalendar>=1.6.1 - Calendar widget for date selection
- python-dateutil>=2.8.2 - Advanced date/time operations
- pandas>=1.3.0 - Data manipulation and analysis
- openpyxl>=3.0.0 - Excel file operations
