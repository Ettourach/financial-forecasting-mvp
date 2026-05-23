"""
Unit tests for forecasting API.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from uuid import uuid4

from forecasting.models.candlestick import UploadedDataset, CandlestickData


class CSVUploadTestCase(APITestCase):
    """Test cases for CSV upload endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.upload_url = '/api/upload/'

    def test_upload_valid_csv(self):
        """Test uploading a valid CSV file."""
        csv_content = b"""timestamp,open,high,low,close,volume
2024-01-01,185.10,187.30,184.20,186.50,54122000
2024-01-02,186.40,188.10,185.00,187.80,49345000
"""
        file = SimpleUploadedFile(
            "test.csv",
            csv_content,
            content_type="text/csv"
        )

        data = {
            'file': file,
            'symbol': 'AAPL',
            'timeframe': '1d'
        }

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('dataset_id', response.data['data'])
        self.assertEqual(response.data['data']['rows_processed'], 2)

    def test_upload_missing_columns(self):
        """Test uploading CSV with missing columns."""
        csv_content = b"""timestamp,open,high
2024-01-01,185.10,187.30
"""
        file = SimpleUploadedFile(
            "test.csv",
            csv_content,
            content_type="text/csv"
        )

        data = {
            'file': file,
            'symbol': 'AAPL',
        }

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class HealthCheckTestCase(APITestCase):
    """Test cases for health check endpoint."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['status'], 'ok')

