from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging

from ..schemas.fund import FundSummary, FundDetail, FundAnalysis
from ..schemas.request import QueryRequest, ComparisonRequest
from ..services.mfapi_service import mutual_fund_service
from ..agents.fund_agent import process_query, process_query_stream

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/funds/search", response_model=List[FundSummary])
async def search_funds(
    q: str = Query(..., description="Search query for mutual funds"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Search for mutual funds based on query string.
    """
    try:
        results = await mutual_fund_service.search_funds(q, limit=limit)
        return results
    except Exception as e:
        logger.error(f"Error searching funds: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search funds")

@router.get("/funds/{scheme_code}", response_model=FundDetail)
async def