"""Export functions for property data to various formats."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from .models import Property


def export_to_json(
    properties: List[Property],
    output_path: Union[str, Path],
    include_raw: bool = False,
    indent: int = 2,
) -> Path:
    """
    Export properties to a JSON file.

    Args:
        properties: List of Property objects to export
        output_path: Path for the output JSON file
        include_raw: If True, include raw API response data
        indent: JSON indentation level (None for compact)

    Returns:
        Path to the created file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = []
    for prop in properties:
        prop_dict = prop.to_dict()
        if not include_raw:
            prop_dict.pop("raw_data", None)
        data.append(prop_dict)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)

    print(f"Exported {len(properties)} properties to {output_path}")
    return output_path


def export_to_csv(
    properties: List[Property],
    output_path: Union[str, Path],
) -> Path:
    """
    Export properties to a CSV file.

    Uses flattened property data for tabular format.

    Args:
        properties: List of Property objects to export
        output_path: Path for the output CSV file

    Returns:
        Path to the created file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to flat dictionaries for CSV
    data = [prop.to_flat_dict() for prop in properties]

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)

    print(f"Exported {len(properties)} properties to {output_path}")
    return output_path


def export_to_sqlite(
    properties: List[Property],
    db_path: Union[str, Path],
    table_name: str = "properties",
    if_exists: str = "append",
) -> Path:
    """
    Export properties to a SQLite database.

    Args:
        properties: List of Property objects to export
        db_path: Path to the SQLite database file
        table_name: Name of the table to insert into
        if_exists: How to handle existing table ('append', 'replace', 'fail')

    Returns:
        Path to the database file
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to flat dictionaries
    data = [prop.to_flat_dict() for prop in properties]

    df = pd.DataFrame(data)

    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)

    print(f"Exported {len(properties)} properties to {db_path} (table: {table_name})")
    return db_path


def export_raw_json(
    data: Union[dict, list],
    output_path: Union[str, Path],
    indent: int = 2,
) -> Path:
    """
    Export raw API response data to JSON.

    Useful for saving unprocessed API responses for debugging
    or custom processing.

    Args:
        data: Raw API response data
        output_path: Path for the output file
        indent: JSON indentation level

    Returns:
        Path to the created file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)

    print(f"Exported raw data to {output_path}")
    return output_path


def create_database_schema(db_path: Union[str, Path]) -> None:
    """
    Create the database schema with proper indexes.

    Call this once to set up an optimized database structure
    before bulk imports.

    Args:
        db_path: Path to the SQLite database
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema = """
    CREATE TABLE IF NOT EXISTS properties (
        id TEXT PRIMARY KEY,
        apn TEXT,
        fetched_at TEXT,
        
        -- Address
        street TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        county TEXT,
        full_address TEXT,
        
        -- Owner
        owner_name TEXT,
        owner_mailing_address TEXT,
        owner_mailing_city TEXT,
        owner_mailing_state TEXT,
        owner_mailing_zip TEXT,
        owner_type TEXT,
        is_absentee INTEGER,
        
        -- Property Details
        property_type TEXT,
        bedrooms INTEGER,
        bathrooms REAL,
        sqft INTEGER,
        lot_size_sqft INTEGER,
        lot_size_acres REAL,
        year_built INTEGER,
        stories INTEGER,
        garage_spaces INTEGER,
        pool INTEGER,
        construction_type TEXT,
        roof_type TEXT,
        
        -- Valuation
        estimated_value INTEGER,
        estimated_equity INTEGER,
        assessed_value INTEGER,
        tax_assessed_value INTEGER,
        last_sale_price INTEGER,
        last_sale_date TEXT,
        price_per_sqft REAL,
        
        -- Tax Info
        annual_tax REAL,
        tax_year INTEGER,
        tax_rate REAL,
        tax_delinquent INTEGER,
        delinquent_amount REAL,
        
        -- Mortgage Info
        has_mortgage INTEGER,
        mortgage_amount INTEGER,
        mortgage_date TEXT,
        lender_name TEXT,
        loan_type TEXT,
        interest_rate REAL,
        estimated_balance INTEGER
    );

    -- Create indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_zip_code ON properties(zip_code);
    CREATE INDEX IF NOT EXISTS idx_city_state ON properties(city, state);
    CREATE INDEX IF NOT EXISTS idx_county ON properties(county);
    CREATE INDEX IF NOT EXISTS idx_apn ON properties(apn);
    CREATE INDEX IF NOT EXISTS idx_owner_name ON properties(owner_name);
    CREATE INDEX IF NOT EXISTS idx_property_type ON properties(property_type);
    CREATE INDEX IF NOT EXISTS idx_estimated_value ON properties(estimated_value);
    CREATE INDEX IF NOT EXISTS idx_is_absentee ON properties(is_absentee);
    CREATE INDEX IF NOT EXISTS idx_tax_delinquent ON properties(tax_delinquent);
    """

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)

    print(f"Database schema created at {db_path}")


def generate_filename(
    prefix: str = "properties",
    extension: str = "json",
    include_timestamp: bool = True,
) -> str:
    """
    Generate a filename for exports.

    Args:
        prefix: Filename prefix
        extension: File extension (without dot)
        include_timestamp: If True, add timestamp to filename

    Returns:
        Generated filename
    """
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    return f"{prefix}.{extension}"


class ExportManager:
    """
    Manages exports to multiple formats with consistent output paths.
    """

    def __init__(self, output_dir: Union[str, Path] = "data"):
        """
        Initialize the export manager.

        Args:
            output_dir: Base directory for all exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        properties: List[Property],
        formats: List[str],
        filename_prefix: str = "properties",
        include_raw: bool = False,
    ) -> dict:
        """
        Export properties to multiple formats.

        Args:
            properties: List of Property objects
            formats: List of formats ('json', 'csv', 'sqlite')
            filename_prefix: Prefix for output filenames
            include_raw: Include raw API data in JSON export

        Returns:
            Dictionary mapping format to output path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outputs = {}

        for fmt in formats:
            fmt = fmt.lower()
            
            if fmt == "json":
                path = self.output_dir / f"{filename_prefix}_{timestamp}.json"
                export_to_json(properties, path, include_raw=include_raw)
                outputs["json"] = path
                
            elif fmt == "csv":
                path = self.output_dir / f"{filename_prefix}_{timestamp}.csv"
                export_to_csv(properties, path)
                outputs["csv"] = path
                
            elif fmt in ("sqlite", "db", "database"):
                path = self.output_dir / f"{filename_prefix}.db"
                # Create schema if this is a new database
                if not path.exists():
                    create_database_schema(path)
                export_to_sqlite(properties, path)
                outputs["sqlite"] = path
                
            else:
                print(f"Warning: Unknown export format '{fmt}'")

        return outputs
