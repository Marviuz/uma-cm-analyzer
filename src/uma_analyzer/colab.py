"""Colab-friendly interface for Uma Analyzer."""

from pathlib import Path
import pandas as pd

from uma_analyzer.analyzer import Analyzer
from uma_analyzer.parser import parse_csv


def analyze_csv(filepath: str) -> Analyzer:
    """Load and analyze a CSV file.
    
    Args:
        filepath: Path to CSV file (or upload in Colab)
    
    Returns:
        Analyzer instance ready for querying
    """
    result = parse_csv(Path(filepath))
    if not result.is_valid:
        errors = [e.message for e in result.validation_errors]
        raise ValueError(f"CSV validation failed: {errors}")
    
    return Analyzer(result.entries)


def analyze_google_sheet(
    sheet_url: str,
    sheet_name: str = "Sheet1"
) -> Analyzer:
    """Load and analyze data from a Google Spreadsheet.
    
    Args:
        sheet_url: URL to the Google Spreadsheet
        sheet_name: Name of the sheet tab (default: "Sheet1")
    
    Returns:
        Analyzer instance ready for querying
    """
    from google.colab import auth
    from googleapiclient.discovery import build
    
    auth.authenticate_user()
    
    # Extract spreadsheet ID from URL
    # Format: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
    spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0]
    
    service = build("sheets", "v4", credentials=auth.get_user_credentials())
    
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=sheet_name)
        .execute()
    )
    
    values = result.get("values", [])
    if not values:
        raise ValueError("No data found in sheet")
    
    headers = values[0]
    data = values[1:]
    
    df = pd.DataFrame(data, columns=headers)
    df.columns = df.columns.str.strip()
    
    csv_path = Path("/tmp/uma_data.csv")
    df.to_csv(csv_path, index=False)
    
    return analyze_csv(str(csv_path))


def quick_report(filepath_or_url: str) -> dict:
    """Generate a quick analysis report from CSV or Google Sheet URL.
    
    Args:
        filepath_or_url: Path to CSV file or Google Spreadsheet URL
    
    Returns:
        dict with strategy_stats, correlations, skill_impacts, envelope
    """
    if "docs.google.com" in filepath_or_url:
        analyzer = analyze_google_sheet(filepath_or_url)
    else:
        analyzer = analyze_csv(filepath_or_url)
    
    return {
        "strategy_stats": analyzer.calculate_strategy_stats(),
        "correlations": analyzer.calculate_stat_correlations(),
        "skill_impacts": analyzer.calculate_skill_impacts(),
        "envelope": analyzer.calculate_success_envelope(),
    }
