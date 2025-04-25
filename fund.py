from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class NavDataPoint(BaseModel):
    """Represents a single NAV data point."""
    date: str
    nav: float

class FundSummary(BaseModel):
    """Minimal fund information for search results."""
    scheme_code: str
    scheme_name: str
    fund_house: Optional[str] = None
    category: Optional[str] = None

class FundDetail(BaseModel):
    """Detailed fund information."""
    scheme_code: str
    scheme_name: str
    fund_house: Optional[str] = None
    scheme_type: Optional[str] = None
    scheme_category: Optional[str] = None
    scheme_nav: Optional[float] = None
    scheme_nav_date: Optional[str] = None
    
    # Performance metrics
    one_month_return: Optional[float] = None
    three_month_return: Optional[float] = None
    six_month_return: Optional[float] = None
    one_year_return: Optional[float] = None
    three_year_return: Optional[float] = None
    five_year_return: Optional[float] = None
    
    # Historical NAV data - optional as it may be large
    nav_data: Optional[List[NavDataPoint]] = None

class FundSearchResults(BaseModel):
    """Collection of fund search results."""
    query: str
    results: List[FundSummary]
    total_results: int
    
class FundAnalysis(BaseModel):
    """Fund analysis and insights."""
    fund_id: str
    fund_name: str
    summary: str
    performance_insights: str
    risk_assessment: Optional[str] = None
    recommendations: Optional[str] = None