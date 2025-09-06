#!/usr/bin/env python3
"""
Test runner script for the new schema implementation.
Run this to validate all the changes work correctly.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Run all tests to validate the new schema implementation."""
    
    print("🚀 Swiss Auction Platform - New Schema Test Suite")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Test results
    results = []
    
    # 1. Install test dependencies
    results.append(run_command(
        "pip install pytest pytest-asyncio aiosqlite",
        "Installing test dependencies"
    ))
    
    # 2. Run database model tests
    results.append(run_command(
        "python -m pytest tests/test_new_schema.py::TestDatabaseModels -v",
        "Testing database models and relationships"
    ))
    
    # 3. Run API integration tests
    results.append(run_command(
        "python -m pytest tests/test_new_schema.py::TestAPIIntegration -v",
        "Testing API endpoints with new schema"
    ))
    
    # 4. Run data validation tests
    results.append(run_command(
        "python -m pytest tests/test_new_schema.py::TestDataValidation -v",
        "Testing data validation and edge cases"
    ))
    
    # 5. Run Celery task tests
    results.append(run_command(
        "python -m pytest tests/test_celery_tasks.py -v",
        "Testing Celery background tasks"
    ))
    
    # 6. Run SHAB parser tests
    results.append(run_command(
        "python -m pytest tests/test_shab_parser_new_schema.py -v",
        "Testing SHAB parser with new schema"
    ))
    
    # 7. Run all tests together
    results.append(run_command(
        "python -m pytest tests/ -v --tb=short",
        "Running complete test suite"
    ))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The new schema implementation is working correctly.")
        print("\n✨ Key Features Validated:")
        print("   • Database models with new schema")
        print("   • Multilingual titles (JSONB)")
        print("   • Person/Company debtor types")
        print("   • Circulation/Registration deadlines")
        print("   • Spatial data for maps")
        print("   • Payment system (subscriptions)")
        print("   • Analytics tracking")
        print("   • API endpoints (free vs premium)")
        print("   • Celery background tasks")
        print("   • SHAB parser integration")
        return 0
    else:
        print(f"\n💥 {total - passed} TEST(S) FAILED! Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
