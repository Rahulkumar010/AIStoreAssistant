import pandas as pd
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ExcelHandler:
    """Handle Excel file operations for structured data"""
    
    def __init__(self):
        self.supported_sheets = [
            'Store Data',
            'Transactional Data',
            'Employee Shifts'
            # 'sales',
            # 'staff',
            # 'location_data',
            # 'store_data',
            # 'transactional_data',
            # 'employee_shifts'
        ]
    
    def read_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """Read Excel file and return dataframes"""
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=3, usecols=lambda x: x not in ["Unnamed: 0"])
                return {sheet_name: df}
            else:
                # Read all sheets
                excel_file = pd.ExcelFile(file_path)
                dfs = {}
                for sheet in excel_file.sheet_names:
                    dfs[sheet] = pd.read_excel(file_path, sheet_name=sheet, header=3, usecols=lambda x: x not in ["Unnamed: 0"])
                return dfs
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise
    
    def get_sales_summary(self, sales_df: pd.DataFrame, store_id: Optional[str] = None) -> Dict[str, Any]:
        """Get sales summary from sales dataframe"""
        try:
            if store_id and 'store_id' in sales_df.columns:
                df = sales_df[sales_df['store_id'] == store_id]
            else:
                df = sales_df
            
            summary = {
                'total_sales': float(df['sales_amount'].sum()) if 'sales_amount' in df.columns else 0,
                'avg_order_value': float(df['order_value'].mean()) if 'order_value' in df.columns else 0,
                'total_transactions': len(df),
                'date_range': {
                    'start': str(df['date'].min()) if 'date' in df.columns else None,
                    'end': str(df['date'].max()) if 'date' in df.columns else None
                }
            }
            return summary
        except Exception as e:
            logger.error(f"Error getting sales summary: {str(e)}")
            return {}
    
    def get_staff_metrics(self, staff_df: pd.DataFrame, store_id: Optional[str] = None) -> Dict[str, Any]:
        """Get staff metrics from staff dataframe"""
        try:
            if store_id and 'store_id' in staff_df.columns:
                df = staff_df[staff_df['store_id'] == store_id]
            else:
                df = staff_df
            
            metrics = {
                'total_staff': len(df),
                'avg_shifts_per_employee': float(df['shifts'].mean()) if 'shifts' in df.columns else 0,
                'total_hours': float(df['hours'].sum()) if 'hours' in df.columns else 0
            }
            return metrics
        except Exception as e:
            logger.error(f"Error getting staff metrics: {str(e)}")
            return {}
    
    def query_data(self, df: pd.DataFrame, query_dict: Dict[str, Any]) -> pd.DataFrame:
        """Query dataframe with filters"""
        try:
            result_df = df.copy()
            for column, value in query_dict.items():
                if column in result_df.columns:
                    result_df = result_df[result_df[column] == value]
            return result_df
        except Exception as e:
            logger.error(f"Error querying data: {str(e)}")
            return pd.DataFrame()
    
    def aggregate_data(self, df: pd.DataFrame, group_by: str, agg_column: str, 
                      agg_func: str = 'sum') -> Dict[str, Any]:
        """Aggregate data by column"""
        try:
            if group_by not in df.columns or agg_column not in df.columns:
                return {}
            
            if agg_func == 'sum':
                result = df.groupby(group_by)[agg_column].sum().to_dict()
            elif agg_func == 'mean':
                result = df.groupby(group_by)[agg_column].mean().to_dict()
            elif agg_func == 'count':
                result = df.groupby(group_by)[agg_column].count().to_dict()
            else:
                result = {}
            
            return result
        except Exception as e:
            logger.error(f"Error aggregating data: {str(e)}")
            return {}

excel_handler = ExcelHandler()
