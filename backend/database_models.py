from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, time as timetype, date as datetype
import uuid


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    def model_dump(self, *, by_alias: bool = False, **kwargs):
        return super().model_dump(by_alias=by_alias, **kwargs)
    
class Store(CustomBaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    store_id: str = Field(alias="Store ID")
    full_address: str = Field(alias="Full Address")
    geo_location_id: str = Field(alias="Geo Location ID")
    store_images: Optional[str] = None
    store_videos: Optional[str] = None

class EmployeeShifts(CustomBaseModel):
    employee_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="Employee_ID")
    employee_name: str = Field(alias="Name")
    store_id: str = Field(alias="Store")
    assigned_role: str = Field(alias="Assigned Role")
    date: datetype = Field(alias="Date")
    month: str = Field(alias="Month")
    clock_in: timetype = Field(alias="Clock_In")
    clock_out: timetype = Field(alias="Clock_Out")
    shift_hours: timetype = Field(alias="Shift_Hours")

class EmployeeInfo(CustomBaseModel):
    employee_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="Employee_ID")
    employee_name: str = Field(alias="Name")
    store_id: str = Field(alias="Store")
    assigned_role: str = Field(alias="Assigned Role")
    hire_date: datetype = Field(alias="Hire Date")
    tenure_years: float = Field(alias="Tenure (Years)")
    overall_employee_performance_rating: int = Field(alias="Overall Employee Performance Rating")

class CustomerTransactions(CustomBaseModel):
    transaction_id: Union[int, str] = Field(alias="Transaction_ID")
    customer_id: Union[int, str] = Field(alias="Customer_ID")
    store_id: str = Field(alias="Store")
    age: int = Field(alias="Age")
    gender: str = Field(alias="Gender")
    income: str = Field(alias="Income")
    date: datetype = Field(alias="Date")
    year: int = Field(alias="Year")
    month: str = Field(alias="Month")
    day: int = Field(alias="Day")
    time: timetype = Field(alias="Time")
    total_quantity: int = Field(alias="Total_Quantity")
    unit_price: float = Field(alias="Unit_Price")
    total_amount: float = Field(alias="Total_Amount")
    product: str = Field(alias="Product")
    product_category: str = Field(alias="Product_Category")
    customer_feedback: Optional[str] = Field(alias="Customer_Feedback")
    payment_method: str = Field(alias="Payment_Method")
