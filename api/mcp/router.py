from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.get("/tools/get_sales_data")
def get_sales_data():
    """Get sales data"""
    return {"sales": [{"id": "1", "name": "Sales 1", "description": "Sales 1 description"}, {"id": "2", "name": "Sales 2", "description": "Sales 2 description"}, {"id": "3", "name": "Sales 3", "description": "Sales 3 description"}]}

@router.get("/tools/get_finance_data")
def get_finance_data():
    """Get finance data"""
    return {"finance": [{"id": "1", "name": "Finance 1", "description": "Finance 1 description"}, {"id": "2", "name": "Finance 2", "description": "Finance 2 description"}, {"id": "3", "name": "Finance 3", "description": "Finance 3 description"}]}
