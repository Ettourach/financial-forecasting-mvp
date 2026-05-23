#!/usr/bin/env python
"""
Quick start script to run the Financial Forecasting MVP Backend.

This script handles:
1. Environment setup
2. Database migrations
3. Starting the development server

Usage:
    python start_dev_server.py
"""

import os
import sys
import subprocess
import platform


def run_command(cmd, description):
    """Run a shell command and report results."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"✗ Command failed: {cmd}")
        return False
    print(f"✓ {description} completed successfully")
    return True


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("  Financial Forecasting MVP - Backend Quick Start")
    print("="*60)

    # Check if we're in the backend directory
    if not os.path.exists('manage.py'):
        print("\n✗ Error: manage.py not found. Please run this script from the backend directory.")
        print("  cd backend")
        print("  python start_dev_server.py")
        return False

    # Run migrations
    if not run_command('python manage.py migrate', 'Running database migrations'):
        return False

    # Run tests
    print("\n" + "="*60)
    print("  Running tests to verify setup...")
    print("="*60)
    result = subprocess.run(['python', 'manage.py', 'test', 'forecasting.tests'],
                          capture_output=True, text=True)
    if 'OK' in result.stderr or 'OK' in result.stdout:
        print("✓ All tests passed!")
    else:
        print("⚠ Some tests may have failed, but proceeding anyway...")

    # Start development server
    print("\n" + "="*60)
    print("  Starting development server...")
    print("="*60)
    print("\n✓ Backend is starting on http://localhost:8000")
    print("✓ API endpoints: http://localhost:8000/api/")
    print("✓ Admin panel: http://localhost:8000/admin/")
    print("✓ API docs: http://localhost:8000/api/docs/")
    print("\nPress Ctrl+C to stop the server.\n")

    run_command('python manage.py runserver', 'Starting Django development server')
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

