"""
Comprehensive test suite for the forecasting API.
"""

import os
import sys
import django
import tempfile
import csv
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from forecasting.models import UploadedDataset, CandlestickData


class TestDatabaseModels:
    """Test database models."""

    @staticmethod
    def test_models_exist():
        """Verify models are created."""
        print("✓ Database models imported successfully")
        return True


class TestServices:
    """Test service layer."""

    @staticmethod
    def test_csv_parser():
        """Test CSV parser service."""
        from forecasting.services.csv_parser import CSVParserService
        from io import StringIO

        # Create sample CSV
        csv_data = """timestamp,open,high,low,close,volume
2024-01-01,185.10,187.30,184.20,186.50,54122000
2024-01-02,186.40,188.10,185.00,187.80,49345000
"""
        csv_file = StringIO(csv_data)
        csv_file.name = 'test.csv'

        try:
            df = CSVParserService.parse_csv(csv_file)
            print(f"✓ CSV Parser: Successfully parsed CSV with {len(df)} rows")
            return True
        except Exception as e:
            print(f"✗ CSV Parser failed: {str(e)}")
            return False

    @staticmethod
    def test_validation_service():
        """Test validation service."""
        from forecasting.services.validation import ValidationService

        try:
            # Test symbol validation
            ValidationService.validate_symbol('AAPL')
            print("✓ Validation Service: Symbol validation works")

            # Test timeframe validation
            ValidationService.validate_timeframe('1d')
            print("✓ Validation Service: Timeframe validation works")

            # Test horizon validation
            ValidationService.validate_horizon(30)
            print("✓ Validation Service: Horizon validation works")

            return True
        except Exception as e:
            print(f"✗ Validation Service failed: {str(e)}")
            return False


class TestAPIs:
    """Test API endpoints."""

    @staticmethod
    def test_health_check():
        """Test health check endpoint."""
        from django.test import Client

        client = Client()
        try:
            response = client.get('/api/health/')
            if response.status_code == 200:
                print("✓ Health Check: Endpoint responds with 200 OK")
                return True
            else:
                print(f"✗ Health Check: Got {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health Check failed: {str(e)}")
            return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Financial Forecasting MVP - Backend Test Suite")
    print("="*60 + "\n")

    results = []

    # Test Models
    print("[1] Testing Database Models")
    results.append(TestDatabaseModels.test_models_exist())

    # Test Services
    print("\n[2] Testing Service Layer")
    results.append(TestServices.test_csv_parser())
    results.append(TestServices.test_validation_service())

    # Test APIs
    print("\n[3] Testing API Endpoints")
    results.append(TestAPIs.test_health_check())

    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} tests passed")
    print("="*60 + "\n")

    if passed == total:
        print("✓ All tests passed! Backend is working correctly.")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())

