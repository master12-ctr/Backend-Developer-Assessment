
import subprocess
import sys
import os
from datetime import datetime

def run_test(command, description):
    """Run a single test command and print the results"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    # Print the command being run
    print(f"Running: {command}")
    
    # Run the command
    result = subprocess.run(command, shell=True, text=True)
    
    # Return whether the test passed
    return result.returncode == 0

def main():
    """Main function to run all tests"""
    print("="*60)
    print("IDEEZA Analytics API - Test Suite Runner")
    print("="*60)
    
    # Check if we're in the correct directory
    if not os.path.exists("manage.py"):
        print("ERROR: manage.py not found!")
        print("Please run this script from the project root directory.")
        print("Current directory:", os.getcwd())
        return 1
    
    all_tests_passed = True
    
    # Run the specific test modules
    test_modules = [
        ("python manage.py test analytics_app.tests.test_models", "Model Tests"),
        ("python manage.py test analytics_app.tests.test_services", "Service Tests"),
        ("python manage.py test analytics_app.tests.test_views", "View Tests"),
        ("python manage.py test analytics_app.tests.test_integration", "Integration Tests"),
    ]
    
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    for command, description in test_modules:
        passed = run_test(command, description)
        if not passed:
            all_tests_passed = False
        print(f"\n✓ {description} COMPLETE")
    
    # Run all tests together
    print("\n" + "="*60)
    print("RUNNING ALL TESTS TOGETHER")
    print("="*60)
    
    all_passed = run_test("python manage.py test analytics_app", "All Tests")
    if not all_passed:
        all_tests_passed = False
    
    # Run performance tests
    print("\n" + "="*60)
    print("RUNNING PERFORMANCE TESTS")
    print("="*60)
    
    perf_passed = run_test("python manage.py run_performance_tests", "Performance Tests")
    if not perf_passed:
        all_tests_passed = False
    
    # Print final summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Timestamp: {timestamp}")
    
    if all_tests_passed:
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe IDEEZA Analytics API is ready for production!")
        print("\nNext steps:")
        print("1. Run server: python manage.py runserver")
        print("2. View docs: http://localhost:8000/swagger/")
        print("3. Admin panel: http://localhost:8000/admin/")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("\nPlease check the test output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())