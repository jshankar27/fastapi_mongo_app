from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
    
class ProductRequest(BaseModel):
    product: str = Field(..., description="The name of the product")
    unit: str = Field(..., description="The unit of the product")
    description: str = Field(..., description="The description of the product")
    price: Optional[float] = Field(None, description="The price of the product in USD (optional)")
    
    model_config = ConfigDict(extra="forbid")
    __created_at: datetime = None
    __updated_at: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.price is None:
            self.price = f"${(self.get_default_price(self.unit)):.4f}"
        else:
            self.price = f"${self.price:.4f}"
            
    def to_dict(self):
        #return self.model_dump(exclude_unset=True)
        return {
            **self.model_dump(),  # Convert user-input fields
            "created_at": self.__created_at,
            "updated_at": self.__updated_at
        }
    
    # Function to return default price based on product unit
    def get_default_price(self, unit: str) -> float:
        price_defaults = {
            "cores": 0.1000,
            "GB": 0.0500,
            "units": 1.5000
        }
        print(price_defaults.get(unit))
        return price_defaults.get(unit, 1.00)
    
    
class SuccessResponse(BaseModel):
    success: bool = Field(default=True, description="Indicates if the operation was successful")
    data: Optional[Any] = Field(default=None, description="Response data as a dictionary")
    message: Optional[str] = Field(default=None, description="Response message")
    
    model_config = ConfigDict(populate_by_name=True, extra="forbid", serialization_exclude_none=True)


class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Indicates if the operation was successful")
    message: str = Field(..., description="Response message") 