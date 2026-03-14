"""Analytics module - Data warehousing and business intelligence"""
from src.analytics.analytics_loader import load_to_snowflake_staging
from src.analytics.analytics_model import setup_analytics_schema, clear_all_data
from src.analytics.analytics_reports import report_all, get_kpi_summary

__all__ = [
    "clear_all_data",
    "load_to_snowflake_staging",
    "setup_analytics_schema",
    "report_all",
    "get_kpi_summary",
]
