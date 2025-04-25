import httpx
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging
from ..core.config import settings
from ..schemas.fund import FundSummary, FundDetail, NavDataPoint

logger = logging.getLogger(__name__)

class MutualFundService:
    """Service for interacting with the MFAPI.in API."""
    
    def __init__(self):
        self.base_url = settings.mfapi_base_url
        self.timeout = settings.mfapi_timeout
        self.cache = {}  # Simple in-memory cache
        
    async def search_funds(self, query: str, limit: int = 10) -> List[FundSummary]:
        """
        Search for mutual funds based on query string.
        
        Args:
            query: Search term (fund name, AMC, etc.)
            limit: Maximum number of results
            
        Returns:
            List of FundSummary objects
        """
        cache_key = f"search:{query}:{limit}"
        if settings.enable_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Since MFAPI doesn't have a direct search endpoint, 
        # we need to fetch all funds and filter them
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}")
                response.raise_for_status()
                all_funds = response.json()
                
                # Filter funds based on query
                filtered_funds = []
                for fund in all_funds:
                    if query.lower() in fund.get("schemeName", "").lower():
                        filtered_funds.append(
                            FundSummary(
                                scheme_code=fund.get("schemeCode"),
                                scheme_name=fund.get("schemeName"),
                                fund_house=self._extract_fund_house(fund.get("schemeName", ""))
                            )
                        )
                        
                        if len(filtered_funds) >= limit:
                            break
                
                if settings.enable_cache:
                    self.cache[cache_key] = filtered_funds
                    
                return filtered_funds
                
        except httpx.HTTPError as e:
            logger.error(f"Error searching funds: {str(e)}")
            return []
    
    async def get_fund_details(self, scheme_code: str, include_nav_data: bool = False) -> Optional[FundDetail]:
        """
        Get detailed information about a specific fund.
        
        Args:
            scheme_code: Fund scheme code
            include_nav_data: Whether to include historical NAV data
            
        Returns:
            FundDetail object or None if not found
        """
        cache_key = f"fund:{scheme_code}:{include_nav_data}"
        if settings.enable_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/{scheme_code}")
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "SUCCESS":
                    fund_data = data.get("meta", {})
                    nav_data_raw = data.get("data", [])
                    
                    # Calculate returns based on NAV data
                    returns = self._calculate_returns(nav_data_raw)
                    
                    fund_detail = FundDetail(
                        scheme_code=scheme_code,
                        scheme_name=fund_data.get("scheme_name", ""),
                        fund_house=fund_data.get("fund_house", ""),
                        scheme_type=fund_data.get("scheme_type", ""),
                        scheme_category=fund_data.get("scheme_category", ""),
                        scheme_nav=float(nav_data_raw[0].get("nav", 0)) if nav_data_raw else None,
                        scheme_nav_date=nav_data_raw[0].get("date", "") if nav_data_raw else None,
                        one_month_return=returns.get("1M"),
                        three_month_return=returns.get("3M"),
                        six_month_return=returns.get("6M"),
                        one_year_return=returns.get("1Y"),
                        three_year_return=returns.get("3Y"),
                        five_year_return=returns.get("5Y"),
                    )
                    
                    # Add NAV data if requested
                    if include_nav_data:
                        fund_detail.nav_data = [
                            NavDataPoint(date=item.get("date", ""), nav=float(item.get("nav", 0)))
                            for item in nav_data_raw[:365]  # Limit to last year
                        ]
                    
                    if settings.enable_cache:
                        self.cache[cache_key] = fund_detail
                        
                    return fund_detail
                
                return None
                
        except httpx.HTTPError as e:
            logger.error(f"Error fetching fund details: {str(e)}")
            return None
            
    def _extract_fund_house(self, scheme_name: str) -> str:
        """Extract fund house from scheme name."""
        common_fund_houses = [
            "HDFC", "SBI", "ICICI", "Axis", "Kotak", "Aditya Birla", 
            "Nippon", "DSP", "UTI", "IDFC", "Franklin", "Tata", "Mirae"
        ]
        
        for fund_house in common_fund_houses:
            if fund_house in scheme_name:
                return fund_house
                
        return ""
        
    def _calculate_returns(self, nav_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate returns for different time periods."""
        returns = {}
        if not nav_data or len(nav_data) < 2:
            return returns
            
        # Most recent NAV
        latest_nav = float(nav_data[0].get("nav", 0))
        latest_date = datetime.strptime(nav_data[0].get("date", ""), "%d-%m-%Y")
        
        # Define periods
        periods = {
            "1M": timedelta(days=30),
            "3M": timedelta(days=91),
            "6M": timedelta(days=182),
            "1Y": timedelta(days=365),
            "3Y": timedelta(days=1095),
            "5Y": timedelta(days=1825)
        }
        
        # Calculate returns for each period
        for period_key, period_delta in periods.items():
            target_date = latest_date - period_delta
            
            # Find closest NAV to target date
            closest_nav = None
            min_diff = timedelta(days=365)
            
            for entry in nav_data:
                entry_date = datetime.strptime(entry.get("date", ""), "%d-%m-%Y")
                diff = abs(entry_date - target_date)
                
                if diff < min_diff:
                    min_diff = diff
                    closest_nav = float(entry.get("nav", 0))
                    
            # Calculate return if we found a suitable NAV
            if closest_nav and closest_nav > 0:
                period_return = ((latest_nav - closest_nav) / closest_nav) * 100
                returns[period_key] = round(period_return, 2)
                
        return returns

# Create service instance
mutual_fund_service = MutualFundService()