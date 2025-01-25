from user_management import UserManager, UserRole, User

def test_basic_auth():
    """Test basic authentication functionality"""
    user_manager = UserManager()
    
    print("\nTest Case 1: Default Admin Login")
    # Default admin credentials
    username = "admin"
    password = "admin123"  # Default password
    
    # Try to authenticate
    user = user_manager.authenticate(username, password, remember=False)
    print(f"Result: {'PASS' if user else 'FAIL'}")
    print(f"User Role: {user.role if user else 'N/A'}")
    
    print("\nTest Case 2: Invalid Login")
    # Try invalid credentials
    invalid_user = user_manager.authenticate("invalid", "invalid", remember=False)
    print(f"Result: {'PASS' if not invalid_user else 'FAIL'}")
    
    print("\nTest Case 3: Create New User")
    # Try to create a new user
    try:
        user_manager.create_user("testuser2", "password123", UserRole.USER)
        print("Result: PASS")
        # Try to authenticate with new user
        new_user = user_manager.authenticate("testuser2", "password123", remember=False)
        print(f"New User Auth: {'PASS' if new_user else 'FAIL'}")
    except Exception as e:
        print(f"Result: FAIL - {str(e)}")
    
    print("\nTest Case 4: User Roles")
    # Check user roles
    admin_role = user_manager.get_user_role("admin")
    print(f"Admin Role Correct: {'PASS' if admin_role == UserRole.ADMIN else 'FAIL'}")
    
    print("\nTest Case 5: Password Change")
    # Test password change functionality
    try:
        # Change password for admin
        user_manager.change_password("admin", "newpassword123")
        # Try to login with new password
        user = user_manager.authenticate("admin", "newpassword123", remember=False)
        print(f"Password Change: {'PASS' if user else 'FAIL'}")
        # Change back to original password
        user_manager.change_password("admin", "admin123")
    except Exception as e:
        print(f"Password Change: FAIL - {str(e)}")
    
    print("\nTest Case 6: Remember Token")
    # Test remember-me functionality
    user = user_manager.authenticate("admin", "admin123", remember=True)
    if user and user.remember_token:
        # Validate session with token
        valid_session = user_manager.validate_session("admin", user.remember_token)
        print(f"Remember Token: {'PASS' if valid_session else 'FAIL'}")
    else:
        print("Remember Token: FAIL - Could not get token")

if __name__ == '__main__':
    print("Starting Simple Authentication Tests...")
    test_basic_auth()
    print("\nTesting Complete!")
