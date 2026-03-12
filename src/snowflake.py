"""Snowflake connection manager"""
import snowflake.connector
from src.env import SF_ACCOUNT, SF_USER, SF_PASSWORD, SF_DATABASE, SF_WAREHOUSE, SF_SCHEMA


def get_snowflake_connection():
    """Get a Snowflake connection"""
    return snowflake.connector.connect(
        user=SF_USER,
        password=SF_PASSWORD,
        account=SF_ACCOUNT,
        warehouse=SF_WAREHOUSE,
        database=SF_DATABASE,
        schema=SF_SCHEMA,
        ocsp_fail_open=False
    )


def execute_query(query: str):
    """Execute a query and return results"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()


def execute_query_dict(query: str):
    """Execute a query and return results with column names"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        # Fetch all rows
        results = cursor.fetchall()
        # Convert to list of dicts
        return [dict(zip(col_names, row)) for row in results]
    finally:
        cursor.close()
        conn.close()
