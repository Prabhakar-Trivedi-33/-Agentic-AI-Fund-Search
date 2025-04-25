from typing import Dict, List, Any, Tuple, AsyncIterator
from langgraph.graph import StateGraph, END
from langchain.schema import AIMessage
from .nodes import (
    analyze_query,
    search_funds,
    fetch_fund_details,
    analyze_funds,
    generate_final_response
)

def create_fund_agent_graph() -> StateGraph:
    """
    Create the fund agent workflow graph.
    
    Returns:
        StateGraph: The configured workflow graph
    """
    # Define the workflow graph
    graph = StateGraph(name="FundAdvisorAgent")
    
    # Add nodes
    graph.add_node("analyze_query", analyze_query)
    graph.add_node("search_funds", search_funds)
    graph.add_node("fetch_fund_details", fetch_fund_details)
    graph.add_node("analyze_funds", analyze_funds)
    graph.add_node("generate_final_response", generate_final_response)
    
    # Define the workflow
    graph.add_edge("analyze_query", "search_funds")
    graph.add_edge("search_funds", "fetch_fund_details")
    graph.add_edge("fetch_fund_details", "analyze_funds")
    graph.add_edge("analyze_funds", "generate_final_response")
    graph.add_edge("generate_final_response", END)
    
    # Set entry point
    graph.set_entry_point("analyze_query")
    
    return graph

async def process_query(query: str) -> str:
    """
    Process a user query through the fund agent.
    
    Args:
        query: User query about mutual funds
        
    Returns:
        str: Agent's response
    """
    # Initialize graph
    fund_agent = create_fund_agent_graph().compile()
    
    # Run the agent
    result = await fund_agent.ainvoke({"query": query, "chat_history": []})
    
    return result["response"]

async def process_query_stream(query: str) -> AsyncIterator[str]:
    """
    Process a user query and stream the response.
    
    Args:
        query: User query about mutual funds
        
    Yields:
        str: Chunks of the agent's response
    """
    # Initialize graph
    fund_agent = create_fund_agent_graph().compile()
    
    # Stream the agent execution
    async for event in fund_agent.astream({"query": query, "chat_history": []}):
        # Stream only final response chunks
        if event["type"] == "on_chain_end" and event["name"] == "generate_final_response":
            if "response" in event["data"]:
                yield event["data"]["response"]
        
        # Yield node completion messages
        elif event["type"] == "on_chain_end":
            node_name = event["name"]
            if node_name == "analyze_query":
                yield "Analyzing your query about mutual funds...\n\n"
            elif node_name == "search_funds":
                yield "Searching for relevant mutual funds...\n\n"
            elif node_name == "fetch_fund_details":
                yield "Fetching detailed fund information...\n\n"
            elif node_name == "analyze_funds":
                yield "Analyzing fund performance and characteristics...\n\n"