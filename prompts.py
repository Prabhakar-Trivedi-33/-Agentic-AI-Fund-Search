from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_PROMPT = """You are a mutual fund expert advisor specialized in Indian mutual funds. 
Your role is to analyze fund data and provide insights and recommendations based on users' queries.
Use the available tools to search for funds, fetch fund details, and analyze performance.
Always provide balanced, factual information based on the data available.
When comparing funds, consider factors like performance, risk, expense ratio, and fund category.
"""

QUERY_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{query}"),
    ("system", """Analyze this query about mutual funds. Extract the key information:
1. What specific funds are mentioned (if any)?
2. What information is the user looking for (performance, comparison, recommendations, etc.)?
3. What time period is relevant (if mentioned)?
4. Any specific criteria mentioned (risk level, fund size, fund house, etc.)?

Provide your analysis in a structured format.""")
])

FUND_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{query}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", """Based on the user query, what search terms should be used to find relevant mutual funds?
Generate 1-3 search terms that would be most effective for finding the funds the user is interested in.
Return a list of search terms in the format: ["term1", "term2", "term3"]""")
])

FUND_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{query}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", """Analyze the following fund data to answer the user's query:

Fund Information:
{fund_data}

Provide a comprehensive analysis including:
1. Fund overview and category
2. Performance analysis
3. Risk assessment
4. Relevant insights
5. Recommendations based on the user's query

Be specific and data-driven in your analysis.""")
])

FUND_COMPARISON_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{query}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", """Compare the following funds based on the user query:

Fund 1:
{fund_data_1}

Fund 2:
{fund_data_2}

Provide a comprehensive comparison including:
1. Performance comparison across different time periods
2. Risk assessment comparison
3. Fund characteristics comparison
4. Advantages and disadvantages of each fund
5. Recommendation based on the query

Be balanced and objective in your comparison.""")
])

FINAL_RESPONSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{query}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", """Based on all the information gathered:

{context}

Provide a comprehensive, well-structured response to the user's query. Include relevant fund data, insights, and recommendations.
Ensure your response is balanced, factual, and tailored to the user's specific questions.""")
])