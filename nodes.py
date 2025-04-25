from typing import Dict, List, Any, Tuple, Optional
import json
import re
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from ..services.mfapi_service import mutual_fund_service
from ..core.llm import generate_response
from .prompts import (
    QUERY_ANALYSIS_PROMPT,
    FUND_SEARCH_PROMPT,
    FUND_ANALYSIS_PROMPT,
    FUND_COMPARISON_PROMPT,
    FINAL_RESPONSE_PROMPT
)

async def analyze_query(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the user query to understand intent and extract key information.
    
    Args:
        state: Current state containing user query
        
    Returns:
        Updated state with query analysis
    """
    query = state["query"]
    chat_history = state.get("chat_history", [])
    
    # Prepare prompt
    messages = QUERY_ANALYSIS_PROMPT.format_messages(
        query=query
    )
    
    # Generate analysis
    analysis = await generate_response(messages)
    
    # Extract fund names if mentioned
    fund_names = extract_fund_names(analysis)
    
    # Update state
    return {
        **state,
        "query_analysis": analysis,
        "fund_names": fund_names,
        "chat_history": chat_history + [
            HumanMessage(content=query),
            AIMessage(content="I'm analyzing your query about mutual funds.")
        ]
    }

async def search_funds(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for funds based on the query analysis.
    
    Args:
        state: Current state containing query and analysis
        
    Returns:
        Updated state with search results
    """
    query = state["query"]
    chat_history = state.get("chat_history", [])
    fund_names = state.get("fund_names", [])
    
    # If specific funds were mentioned, search for them
    search_results = []
    
    if fund_names:
        for fund_name in fund_names:
            results = await mutual_fund_service.search_funds(fund_name, limit=5)
            search_results.extend(results)
    else:
        # Generate search terms
        messages = FUND_SEARCH_PROMPT.format_messages(
            query=query,
            chat_history=chat_history
        )
        search_terms_text = await generate_response(messages)
        
        # Parse search terms
        try:
            search_terms = parse_search_terms(search_terms_text)
            
            # Search for each term
            for term in search_terms:
                results = await mutual_fund_service.search_funds(term, limit=5)
                search_results.extend(results)
        except Exception as e:
            # Fallback: search using the original query
            search_results = await mutual_fund_service.search_funds(query, limit=10)
    
    # Deduplicate results
    unique_results = {result.scheme_code: result for result in search_results}
    
    return {
        **state, 
        "search_results": list(unique_results.values()),
        "chat_history": chat_history + [
            AIMessage(content=f"I found {len(unique_results)} funds that match your query.")
        ]
    }

async def fetch_fund_details(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch detailed information for the funds found.
    
    Args:
        state: Current state containing search results
        
    Returns:
        Updated state with fund details
    """
    search_results = state.get("search_results", [])
    chat_history = state.get("chat_history", [])
    
    # Get details for top funds (limit to 3 to avoid rate limiting)
    fund_details = []
    
    for fund in search_results[:3]:
        details = await mutual_fund_service.get_fund_details(
            fund.scheme_code, 
            include_nav_data=True
        )
        if details:
            fund_details.append(details)
    
    return {
        **state,
        "fund_details": fund_details,
        "chat_history": chat_history + [
            AIMessage(content=f"I've gathered detailed information on {len(fund_details)} funds.")
        ]
    }

async def analyze_funds(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze fund data based on user query.
    
    Args:
        state: Current state containing fund details
        
    Returns:
        Updated state with fund analysis
    """
    query = state["query"]
    fund_details = state.get("fund_details", [])
    chat_history = state.get("chat_history", [])
    
    if not fund_details:
        return {
            **state,
            "response": "I couldn't find any mutual funds matching your query. Could you please provide more specific information?",
            "chat_history": chat_history + [
                AIMessage(content="I couldn't find any mutual funds matching your query.")
            ]
        }
    
    # Check if this is a comparison query
    if len(fund_details) >= 2 and is_comparison_query(query):
        # Compare top 2 funds
        messages = FUND_COMPARISON_PROMPT.format_messages(
            query=query,
            fund_data_1=json.dumps(fund_details[0].dict(), indent=2),
            fund_data_2=json.dumps(fund_details[1].dict(), indent=2),
            chat_history=chat_history
        )
        
        analysis = await generate_response(messages)
        
    else:
        # Analyze single fund
        messages = FUND_ANALYSIS_PROMPT.format_messages(
            query=query,
            fund_data=json.dumps(fund_details[0].dict(), indent=2),
            chat_history=chat_history
        )
        
        analysis = await generate_response(messages)
    
    return {
        **state,
        "fund_analysis": analysis,
        "chat_history": chat_history + [
            AIMessage(content="I've analyzed the fund data based on your query.")
        ]
    }

async def generate_final_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate the final comprehensive response.
    
    Args:
        state: Current state containing all analysis
        
    Returns:
        Updated state with final response
    """
    query = state["query"]
    chat_history = state.get("chat_history", [])
    fund_analysis = state.get("fund_analysis", "")
    
    context = fund_analysis
    
    # Generate final response
    messages = FINAL_RESPONSE_PROMPT.format_messages(
        query=query,
        context=context,
        chat_history=chat_history
    )
    
    response = await generate_response(messages, temperature=0.3)
    
    return {
        **state,
        "response": response,
        "chat_history": chat_history + [
            AIMessage(content=response)
        ]
    }

# Helper functions

def extract_fund_names(analysis: str) -> List[str]:
    """Extract fund names from query analysis."""
    fund_names = []
    
    # Look for fund names in the analysis
    lines = analysis.split('\n')
    for line in lines:
        if "fund" in line.lower() and ":" in line:
            name_part = line.split(':', 1)[1].strip()
            if name_part and name_part.lower() not in ["none", "not mentioned", "not specified"]:
                fund_names.append(name_part)
    
    return fund_names

def parse_search_terms(search_terms_text: str) -> List[str]:
    """Parse search terms from LLM response."""
    # Try to find a list in the text
    list_match = re.search(r'\[(.+?)\]', search_terms_text, re.DOTALL)
    
    if list_match:
        # Extract terms from list format
        terms_text = list_match.group(1)
        terms = re.findall(r'"([^"]+)"', terms_text)
        
        if not terms:
            terms = re.findall(r"'([^']+)'", terms_text)
            
        if not terms:
            terms = [term.strip() for term in terms_text.split(',')]
            
        return [term for term in terms if term and term.strip()]
    else:
        # Fallback: split by newlines or commas
        if '\n' in search_terms_text:
            return [term.strip() for term in search_terms_text.split('\n') if term.strip()]
        else:
            return [term.strip() for term in search_terms_text.split(',') if term.strip()]

def is_comparison_query(query: str) -> bool:
    """Determine if the query is asking for a comparison."""
    comparison_keywords = [
        "compare", "comparison", "versus", "vs", "vs.", 
        "better", "difference", "differences", "which is better",
        "contrast", "against"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in comparison_keywords)