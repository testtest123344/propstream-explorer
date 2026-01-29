#!/usr/bin/env python3
"""
PropStream Data Extractor CLI

Command-line tool for extracting property data from PropStream API.
"""

import argparse
import sys
from pathlib import Path

from extractor import PropStreamClient, Property, export_to_json, export_to_csv, export_to_sqlite
from extractor.models import parse_properties
from extractor.export import ExportManager, export_raw_json, create_database_schema


def cmd_test(args):
    """Test API connection."""
    print("Testing PropStream API connection...")
    
    try:
        client = PropStreamClient(args.config)
        if client.test_connection():
            print("Connection successful! Authentication is working.")
            return 0
        else:
            print("Connection failed. Check your auth token.")
            return 1
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Connection error: {e}")
        return 1


def cmd_search(args):
    """Search for properties."""
    try:
        client = PropStreamClient(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    print(f"Searching for properties...")
    
    try:
        # Build search based on provided criteria
        response = client.search_properties(
            address=args.address,
            city=args.city,
            state=args.state,
            zip_code=args.zip,
            county=args.county,
            apn=args.apn,
            limit=args.limit,
        )
        
        # Parse and display results
        properties = parse_properties(response)
        
        if not properties:
            print("No properties found.")
            if args.raw:
                print("\nRaw API response:")
                print(response)
            return 0
        
        print(f"\nFound {len(properties)} properties:\n")
        
        for i, prop in enumerate(properties, 1):
            addr = prop.address
            print(f"{i}. {addr.street or 'N/A'}, {addr.city}, {addr.state} {addr.zip_code}")
            if prop.details.bedrooms or prop.details.bathrooms:
                print(f"   {prop.details.bedrooms or '?'}bd/{prop.details.bathrooms or '?'}ba, {prop.details.sqft or '?'} sqft")
            if prop.valuation.estimated_value:
                print(f"   Est. Value: ${prop.valuation.estimated_value:,}")
            print()
        
        # Export if requested
        if args.output:
            export_results(properties, args.output, args.format, response if args.raw else None)
        
        return 0
        
    except Exception as e:
        print(f"Search error: {e}")
        if args.raw:
            import traceback
            traceback.print_exc()
        return 1


def cmd_lookup(args):
    """Look up a specific property by address."""
    try:
        client = PropStreamClient(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    # Combine address parts into single query
    address_query = args.address
    
    print(f"Looking up: {address_query}")
    
    try:
        # Use the new lookup_address method with autocomplete
        response = client.lookup_address(address_query)
        
        # Check for errors
        if "error" in response:
            print(f"Error: {response['error']}")
            if args.raw:
                print("\nRaw API response:")
                print(response)
            return 1
        
        properties = parse_properties(response)
        
        if not properties:
            print("Property not found.")
            if args.raw:
                print("\nRaw API response:")
                print(response)
            return 0
        
        # Display detailed property info
        prop = properties[0]
        print_property_details(prop)
        
        # Export if requested
        if args.output:
            export_results(properties, args.output, args.format, response if args.raw else None)
        
        return 0
        
    except Exception as e:
        print(f"Lookup error: {e}")
        if args.raw:
            import traceback
            traceback.print_exc()
        return 1


def cmd_batch(args):
    """Batch search by ZIP code or county."""
    try:
        client = PropStreamClient(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    all_properties = []
    
    if args.zips:
        for zip_code in args.zips:
            print(f"Searching ZIP code: {zip_code}...")
            try:
                response = client.search_by_zip(zip_code, limit=args.limit)
                properties = parse_properties(response)
                all_properties.extend(properties)
                print(f"  Found {len(properties)} properties")
            except Exception as e:
                print(f"  Error: {e}")
    
    if args.counties:
        if not args.state:
            print("Error: --state is required when searching by county")
            return 1
        
        for county in args.counties:
            print(f"Searching county: {county}, {args.state}...")
            try:
                response = client.search_by_county(county, args.state, limit=args.limit)
                properties = parse_properties(response)
                all_properties.extend(properties)
                print(f"  Found {len(properties)} properties")
            except Exception as e:
                print(f"  Error: {e}")
    
    print(f"\nTotal properties found: {len(all_properties)}")
    
    if all_properties and args.output:
        export_results(all_properties, args.output, args.format)
    
    return 0


def cmd_init_db(args):
    """Initialize the database with schema."""
    db_path = Path(args.output or "data/properties.db")
    create_database_schema(db_path)
    print(f"Database initialized at: {db_path}")
    return 0


def cmd_stats(args):
    """Show request statistics and rate limit status."""
    try:
        client = PropStreamClient(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    stats = client.get_request_stats()
    
    print("\n" + "=" * 50)
    print("REQUEST STATISTICS")
    print("=" * 50)
    print(f"\nSession Stats:")
    print(f"  Requests this session: {stats['session_requests']}")
    print(f"  Session duration: {stats['session_duration_minutes']} minutes")
    print(f"  Hourly limit: {stats['hourly_limit']}")
    print(f"  Hourly remaining: {stats['hourly_remaining']}")
    print(f"\nDaily Stats:")
    print(f"  Requests today: {stats['daily_requests']}")
    print(f"  Daily limit: {stats['daily_limit']}")
    print(f"  Daily remaining: {stats['daily_remaining']}")
    print(f"\nRate Limit Settings:")
    print(f"  Min delay: {client.min_delay}s")
    print(f"  Max delay: {client.max_delay}s")
    print("=" * 50 + "\n")
    
    return 0


def print_property_details(prop: Property):
    """Print detailed property information."""
    print("\n" + "=" * 60)
    print("PROPERTY DETAILS")
    print("=" * 60)
    
    # Address
    print(f"\nAddress: {prop.address.full_address or f'{prop.address.street}, {prop.address.city}, {prop.address.state} {prop.address.zip_code}'}")
    print(f"County: {prop.address.county}")
    print(f"APN: {prop.apn}")
    
    # Owner
    print(f"\n--- Owner Information ---")
    print(f"Name: {prop.owner.name}")
    print(f"Type: {prop.owner.owner_type}")
    print(f"Absentee: {'Yes' if prop.owner.is_absentee else 'No'}")
    if prop.owner.mailing_address:
        print(f"Mailing: {prop.owner.mailing_address}, {prop.owner.mailing_city}, {prop.owner.mailing_state} {prop.owner.mailing_zip}")
    
    # Property Details
    print(f"\n--- Property Details ---")
    print(f"Type: {prop.details.property_type}")
    print(f"Beds/Baths: {prop.details.bedrooms or '?'}/{prop.details.bathrooms or '?'}")
    print(f"Sqft: {prop.details.sqft:,}" if prop.details.sqft else "Sqft: N/A")
    print(f"Lot Size: {prop.details.lot_size_sqft:,} sqft ({prop.details.lot_size_acres:.2f} acres)" if prop.details.lot_size_sqft else "Lot Size: N/A")
    print(f"Year Built: {prop.details.year_built or 'N/A'}")
    print(f"Stories: {prop.details.stories or 'N/A'}")
    print(f"Pool: {'Yes' if prop.details.pool else 'No'}")
    
    # Valuation
    print(f"\n--- Valuation ---")
    print(f"Estimated Value: ${prop.valuation.estimated_value:,}" if prop.valuation.estimated_value else "Estimated Value: N/A")
    print(f"Estimated Equity: ${prop.valuation.estimated_equity:,}" if prop.valuation.estimated_equity else "Estimated Equity: N/A")
    print(f"Last Sale: ${prop.valuation.last_sale_price:,} on {prop.valuation.last_sale_date}" if prop.valuation.last_sale_price else "Last Sale: N/A")
    
    # Tax Info
    print(f"\n--- Tax Information ---")
    print(f"Annual Tax: ${prop.tax_info.annual_tax:,.2f}" if prop.tax_info.annual_tax else "Annual Tax: N/A")
    print(f"Tax Delinquent: {'Yes' if prop.tax_info.tax_delinquent else 'No'}")
    
    # Mortgage
    print(f"\n--- Mortgage ---")
    print(f"Has Mortgage: {'Yes' if prop.mortgage.has_mortgage else 'No'}")
    if prop.mortgage.has_mortgage:
        print(f"Balance: ${prop.mortgage.mortgage_balance:,}" if prop.mortgage.mortgage_balance else "Balance: N/A")
        print(f"Open Liens: {prop.mortgage.open_lien_count}" if prop.mortgage.open_lien_count else "Open Liens: N/A")
        print(f"Lien Amount: ${prop.mortgage.open_lien_amount:,}" if prop.mortgage.open_lien_amount else "Lien Amount: N/A")
    
    print("\n" + "=" * 60)


def export_results(properties, output_path, formats, raw_data=None):
    """Export search results to specified formats."""
    output_path = Path(output_path)
    
    if not formats:
        # Detect format from extension
        ext = output_path.suffix.lower()
        if ext == ".json":
            formats = ["json"]
        elif ext == ".csv":
            formats = ["csv"]
        elif ext in (".db", ".sqlite"):
            formats = ["sqlite"]
        else:
            formats = ["json"]  # Default
    
    manager = ExportManager(output_path.parent)
    
    for fmt in formats:
        fmt = fmt.lower()
        
        if fmt == "json":
            path = output_path if output_path.suffix == ".json" else output_path.with_suffix(".json")
            export_to_json(properties, path, include_raw=raw_data is not None)
            
        elif fmt == "csv":
            path = output_path if output_path.suffix == ".csv" else output_path.with_suffix(".csv")
            export_to_csv(properties, path)
            
        elif fmt in ("sqlite", "db"):
            path = output_path if output_path.suffix in (".db", ".sqlite") else output_path.with_suffix(".db")
            if not path.exists():
                create_database_schema(path)
            export_to_sqlite(properties, path)
    
    # Optionally save raw response
    if raw_data:
        raw_path = output_path.with_name(f"{output_path.stem}_raw.json")
        export_raw_json(raw_data, raw_path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PropStream Data Extractor - Extract property data from PropStream API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to config file (default: config.json)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test API connection")
    test_parser.set_defaults(func=cmd_test)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for properties")
    search_parser.add_argument("-a", "--address", help="Street address")
    search_parser.add_argument("--city", help="City")
    search_parser.add_argument("--state", help="State (2-letter code)")
    search_parser.add_argument("-z", "--zip", help="ZIP code")
    search_parser.add_argument("--county", help="County name")
    search_parser.add_argument("--apn", help="Assessor's Parcel Number")
    search_parser.add_argument("-l", "--limit", type=int, default=50, help="Max results (default: 50)")
    search_parser.add_argument("-o", "--output", help="Output file path")
    search_parser.add_argument("-f", "--format", nargs="+", choices=["json", "csv", "sqlite"], help="Export format(s)")
    search_parser.add_argument("--raw", action="store_true", help="Include raw API response")
    search_parser.set_defaults(func=cmd_search)
    
    # Lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Look up a specific property by address")
    lookup_parser.add_argument("address", help="Full or partial address (e.g., '123 Main St, Phoenix, AZ')")
    lookup_parser.add_argument("-o", "--output", help="Output file path")
    lookup_parser.add_argument("-f", "--format", nargs="+", choices=["json", "csv", "sqlite"], help="Export format(s)")
    lookup_parser.add_argument("--raw", action="store_true", help="Include raw API response")
    lookup_parser.set_defaults(func=cmd_lookup)
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch search by ZIP codes or counties")
    batch_parser.add_argument("--zips", nargs="+", help="ZIP codes to search")
    batch_parser.add_argument("--counties", nargs="+", help="Counties to search")
    batch_parser.add_argument("--state", help="State (required for county search)")
    batch_parser.add_argument("-l", "--limit", type=int, default=100, help="Max results per area (default: 100)")
    batch_parser.add_argument("-o", "--output", help="Output file path")
    batch_parser.add_argument("-f", "--format", nargs="+", choices=["json", "csv", "sqlite"], help="Export format(s)")
    batch_parser.set_defaults(func=cmd_batch)
    
    # Init-db command
    initdb_parser = subparsers.add_parser("init-db", help="Initialize database with schema")
    initdb_parser.add_argument("-o", "--output", help="Database file path (default: data/properties.db)")
    initdb_parser.set_defaults(func=cmd_init_db)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show request statistics and rate limits")
    stats_parser.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
