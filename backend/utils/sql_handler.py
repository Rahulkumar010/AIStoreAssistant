import pandas as pd
import pandas.io.sql as pdsql
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
import logging
from pathlib import Path
from config import config

logger = logging.getLogger(__name__)


class SQLServerHandler:
    def __init__(self):
        """Initialize SQL Server connection"""
        self.supported_tables = [
            'dbo.customer_transactions',
            'dbo.employee_info',
            'dbo.employee_shifts',
            'dbo.store_info'
        ]
        
        try:
            self.engine = create_engine(
                f"mssql+pyodbc://{config.USERNAME}:{config.PASSWORD}@{config.SERVER_NAME}/{config.DATABASE_NAME}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )
            logger.info("Connected to SQL Server successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {str(e)}")
            raise

    def read_table(self, table_name: str, where_clause: Optional[str] = None) -> pd.DataFrame:
        """Read data from a SQL Server table into a DataFrame"""
        try:
            query = f"SELECT * FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            df = pdsql.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"Error reading table {table_name}: {str(e)}")
            raise

    def get_sales_summary(self, table_name: str, store_id: Optional[str] = None) -> Dict[str, Any]:
        """Get sales summary from sales table"""
        try:
            where_clause = f"[Store ID] = '{store_id}'" if store_id else None
            sales_df = self.read_table(table_name, where_clause)
            
            summary = {
                "total_sales": float(sales_df["Total_Amount"].sum()) if "Total_Amount" in sales_df.columns else 0,
                "avg_order_value": float((sales_df["Total_Amount"].sum()/len(sales_df))) if "Total_Amount" in sales_df.columns else 0,
                "total_transactions": len(sales_df),
                "date_range": {
                    "start": str(sales_df["Date"].min()) if "Date" in sales_df.columns else None,
                    "end": str(sales_df["Date"].max()) if "Date" in sales_df.columns else None
                }
            }
            return summary
        except Exception as e:
            logger.error(f"Error getting sales summary: {str(e)}")
            return {}

    def get_staff_metrics(self, table_name: str, store_id: Optional[str] = None) -> Dict[str, Any]:
        """Get staff metrics from staff table"""
        try:
            where_clause = f"[Store ID] = '{store_id}'" if store_id else None
            staff_df = self.read_table(table_name, where_clause)
            
            metrics = {
                "total_staff": len(staff_df),
                "avg_shifts_per_employee": float(staff_df["shifts"].mean()) if "shifts" in staff_df.columns else 1,
                "total_hours": float(staff_df["Shift_Hours"].sum()) if "Shift_Hours" in staff_df.columns else 0
            }
            return metrics
        except Exception as e:
            logger.error(f"Error getting staff metrics: {str(e)}")
            return {}

    def query_data(self, table_name: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """Query SQL table dynamically using filters"""
        try:
            conditions = " AND ".join([f"[{col}] = '{val}'" for col, val in filters.items()])
            query = f"SELECT * FROM {table_name} WHERE {conditions}" if filters else f"SELECT * FROM {table_name}"
            df = pdsql.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"Error querying data: {str(e)}")
            return pd.DataFrame()

    def aggregate_data(self, table_name: str, group_by: str, agg_column: str, agg_func: str = "SUM") -> Dict[str, Any]:
        """Aggregate SQL table data"""
        try:
            query = f"SELECT {group_by}, {agg_func}({agg_column}) as agg_value FROM {table_name} GROUP BY {group_by}"
            df = pdsql.read_sql(query, self.engine)
            return dict(zip(df[group_by], df["agg_value"]))
        except Exception as e:
            logger.error(f"Error aggregating data: {str(e)}")
            return {}


sql_handler = SQLServerHandler()
