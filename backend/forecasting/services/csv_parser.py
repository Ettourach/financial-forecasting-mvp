"""
CSV parsing and processing service.
"""

import io
import logging
from typing import Tuple, List, Dict, Any

import pandas as pd
from django.conf import settings

from core.exceptions import (
    CSVParsingError,
    MissingColumnsError,
    InvalidDataError,
)

logger = logging.getLogger(__name__)


class CSVParserService:
    """Service for parsing and validating CSV files."""

    REQUIRED_COLUMNS = getattr(settings, 'CSV_REQUIRED_COLUMNS', [
        'timestamp', 'open', 'high', 'low', 'close', 'volume'
    ])
    MAX_ROWS = getattr(settings, 'CSV_MAX_ROWS', 100000)

    @classmethod
    def parse_csv(cls, file) -> pd.DataFrame:
        """
        Parse CSV file and return DataFrame.

        Args:
            file: Uploaded file object

        Returns:
            Parsed DataFrame

        Raises:
            CSVParsingError: If CSV cannot be parsed
        """
        try:
            # Read CSV into DataFrame
            df = pd.read_csv(file, dtype=str)
            logger.info(f"Parsed CSV with {len(df)} rows and columns: {df.columns.tolist()}")
            return df
        except Exception as e:
            logger.exception(f"Failed to parse CSV: {str(e)}")
            raise CSVParsingError(
                detail=f"Failed to parse CSV file: {str(e)}",
                extra_data={"error": str(e)}
            )

    @classmethod
    def validate_columns(cls, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that all required columns are present.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (is_valid, missing_columns)
        """
        df_columns = set(df.columns.str.lower().str.strip())
        required_columns = set(cls.REQUIRED_COLUMNS)

        missing = required_columns - df_columns
        if missing:
            logger.warning(f"Missing columns: {missing}")
            raise MissingColumnsError(list(missing))

        return True, []

    @classmethod
    def validate_rows(cls, df: pd.DataFrame) -> None:
        """
        Validate data types and value ranges.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            InvalidDataError: If rows are invalid
        """
        if len(df) == 0:
            raise InvalidDataError("CSV file is empty")

        if len(df) > cls.MAX_ROWS:
            raise InvalidDataError(
                f"CSV file has {len(df)} rows but maximum allowed is {cls.MAX_ROWS}"
            )

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()

        # Validate timestamp column
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except Exception as e:
            logger.warning(f"Invalid timestamp format: {str(e)}")
            raise InvalidDataError(
                f"Invalid timestamp format. Error: {str(e)}"
            )

        # Validate numeric columns
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    if df[col].isna().any():
                        raise ValueError(f"Column '{col}' has non-numeric values")
                except Exception as e:
                    logger.warning(f"Invalid numeric data in {col}: {str(e)}")
                    raise InvalidDataError(
                        f"Column '{col}' contains invalid numeric values"
                    )

        # Validate data constraints
        if (df['high'] < df['low']).any():
            raise InvalidDataError("High price must be >= low price")

        if (df['volume'] < 0).any():
            raise InvalidDataError("Volume must be non-negative")

        logger.info(f"Validated {len(df)} rows successfully")

    @classmethod
    def transform_data(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transform DataFrame into candlestick records.

        Args:
            df: Validated DataFrame

        Returns:
            List of candlestick dictionaries
        """
        df.columns = df.columns.str.lower().str.strip()

        # Ensure numeric conversions
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        records = []
        for idx, row in df.iterrows():
            record = {
                'timestamp': row['timestamp'],
                'open_price': float(row['open']),
                'high_price': float(row['high']),
                'low_price': float(row['low']),
                'close_price': float(row['close']),
                'volume': float(row['volume']),
            }
            records.append(record)

        logger.info(f"Transformed {len(records)} records")
        return records

    @classmethod
    def process_csv_file(cls, file) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Complete CSV processing pipeline.

        Args:
            file: Uploaded file object

        Returns:
            Tuple of (DataFrame, transformed records)

        Raises:
            CSVParsingError: If parsing fails
            InvalidDataError: If validation fails
        """
        # Parse
        df = cls.parse_csv(file)

        # Validate columns
        cls.validate_columns(df)

        # Validate rows and data types
        cls.validate_rows(df)

        # Transform
        records = cls.transform_data(df)

        return df, records


