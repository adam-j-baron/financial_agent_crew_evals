from datetime import timedelta
from mcp.server.fastmcp import FastMCP
from ollama import web_fetch, web_search
import os
import pandas as pd
import sys
from typing import Any, Dict
import yfinance as yf


def retreive_analyst_predictions(ticker: str) -> str:
    """ For a given Ticker, return the most recent analyst Price Targets and Recommendations
    """
    # Retreive the dataframe of Price Targets and Recommendations
    stock = yf.Ticker(ticker)
    all_estimates_df = stock.upgrades_downgrades

    # Only return last estimate per analyst, since there might be multiple in the time series
    unique_firm_idx = all_estimates_df.groupby('Firm')['Firm'].idxmax()
    last_estimate_df  = all_estimates_df.loc[unique_firm_idx]

    # Filter to last 30 days, to avoid stale estimates
    look_back = pd.Timestamp.now() - timedelta(days=30)
    recent_estimates_df = last_estimate_df[last_estimate_df.index >= look_back]

    # Filter out no Price Targets, since use of 0 can throw off mathematical analysis
    valid_price_targets_df = recent_estimates_df[recent_estimates_df.currentPriceTarget > 0]

    # Only focus on columns that will be useful for an AI Agent
    slim_df = valid_price_targets_df[['Firm','currentPriceTarget','ToGrade']]

    # Convert to JSON for ease of use by AI Agent 
    estimates_json = slim_df.to_json(orient='records')
    return estimates_json

def retreive_prices(ticker: str) -> str:
    """ For a given Ticker, return the most recent Close Prices
    """
    # Retreive the dataframe of Price History
    stock = yf.Ticker(ticker)
    prices_df =  stock.history(period="3mo", interval="1d").reset_index()

    # Only focus on columns that will be useful for an AI Agent
    slim_df = prices_df[['Date','Close']]

    # Convert to JSON for ease of use by AI Agent 
    prices_json = slim_df.to_json(orient='records', date_format='iso')
    return prices_json

def _webpage_search_impl(query: str, max_results: int = 5) -> Dict[str, Any]:
  """"Perform a web search using the query. 
  """
  response = web_search(query=query, max_results=max_results)
  return response.model_dump()

def _webpage_fetch_impl(url: str) -> Dict[str, Any]:
    """ For a given URL, return the title, content and links from the webpage.
    """
    response = web_fetch(url=url)
    return response.model_dump()




# Create the MCP server
mcp_server = FastMCP("YFinance MCP Server")


# Register the tools
@mcp_server.tool(
    name="stock_prices",
    description="Get daily close prices for a given stock ticker.  The JSON returned will conttain Date and Close (i.e. Close Price)).  There will only be one price per day.  To avoid staleness, only prices in the last 3 months are included."
) 
async def retreive_prices_tool(ticker: str) -> str:
    return retreive_prices(ticker)



# Register the tools
@mcp_server.tool(
    name="stock_analyst_estimates",
    description="Get analyst recommendations and price targets for a given stock ticker.  The JSON returned will contain Firm (a.k.a. Analyst), currentPriceTarget and ToGrade (a.k.a. Recommendation).  There will only be one forecast per Firm/Analyst and currentPriceTarget=0 records are excluded.  To avoid staleness, only estimates in the last 30 days are included."
) 
async def retreive_analyst_predictions_tool(ticker: str) -> str:
    return retreive_analyst_predictions(ticker)

@mcp_server.tool(
    name="webpage_search",
    description="Perform a web search using the query.  The response contains URL, title and content for each search result.  The title and the content are the most important parts of the webpage retrieval.  The URL is useful for citing the source."
) 
async def webpage_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Perform a web search using Ollama's hosted search API.

    Args:
      query: The search query to run.
      max_results: Maximum results to return (default: 3).

    Returns:
      JSON-serializable dict matching ollama.WebSearchResult.model_dump()
      The response contains URL, title and content for each search result.  The title and the content are the most important parts of the webpage retrieval.  The URL is useful for citing the source.
    """
    return _webpage_search_impl(query, max_results)

@mcp_server.tool(
    name="webpage_fetch",
    description="Fetch the content of a web page for the provided URL.  The result are title, content and links.  The title and the content are the most important parts of the webpage retrieval.  The links is just a list of links mentioned on the webpage."
) 
async def webpage_fetch(url: str) -> Dict[str, Any]:
    """
    Fetch the content of a web page for the provided URL.

    Args:
      url: The absolute URL to fetch.

    Returns:
      JSON-serializable dict matching ollama.WebFetchResponse.model_dump()
      The result are title, content and links.  The title and the content are the most important parts of the webpage retrieval.  The links is just a list of links mentioned on the webpage.
    """
    return _webpage_fetch_impl(url=url)





if __name__ == "__main__":

    # Check if OLLAMA_API_KEY is set
    if not os.getenv("OLLAMA_API_KEY"):
        print("Error: OLLAMA_API_KEY environment variable is not set.")
        print("Please set the OLLAMA_API_KEY environment variable and try again.")
        sys.exit(1)

    # Proceed with starting the FastMCP server
    # Your server startup code here
    print("OLLAMA_API_KEY is set. Starting the FastMCP server...")

    mcp_server.run(transport="streamable-http")