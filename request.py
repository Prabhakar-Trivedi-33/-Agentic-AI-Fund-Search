from pydantic import BaseModel, Field
from typing import Optional, List, Union

class QueryRequest(BaseModel):
    """User query request model."""
    query: str = Field(..., description="User query about mutual funds")
    max_results: Optional[int] = Field(5, description="Maximum number of results to return")
    include_historical_data: Optional[bool] = Field(False, description="Whether to include historical NAV data")

class ComparisonRequest(BaseModel):
    """Fund comparison request model."""
    fund_ids: List[str] = Field(..., description="List of fund scheme codes to compare")
    comparison_period: Optional[str] = Field("1Y", description="Time period for comparison (1M, 3M, 6M, 1Y, 3Y, 5Y)")