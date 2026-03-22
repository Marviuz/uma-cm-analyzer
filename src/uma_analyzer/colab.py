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
    
    Requires gspread and Google OAuth credentials.
    
    Args:
        sheet_url: URL to the Google Spreadsheet
        sheet_name: Name of the sheet tab (default: "Sheet1")
    
    Returns:
        Analyzer instance ready for querying
    """
    import gspread
    from google.colab import auth
    auth.authenticate_user()
    
    gc = gspread.authorize(auth.default_credentials())
    
    spreadsheet = gc.open_by_url(sheet_url)
    worksheet = spreadsheet.worksheet(sheet_name)
    
    df = pd.DataFrame(worksheet.get_all_records())
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
