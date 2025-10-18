# Observability & Evaluations on a Financial AI Agent Crew

This repository contains an experimental and educational project demonstrating how to implement Observability and Evaluations on a Crew of Financial AI agents that retrieves financial data, analyzes that financial data, runs follow-up investigation and summarizes the results in a user-facing Stock Analysis Report.

The project consists of two main files:

- `mcp_server_financial_tools.py`: A Model Context Protocol (MCP) server that provides financial data and live web search tools.
- `financial_agent_crew_evals.ipynb`: A Jupyter Notebook that acts as a client to connect to the MCP server, creates a Financial AI Agent Crew, performs a complex multi-step analysis for single stock, generates a report summarizing the stock analysis, examines the tracing spans and runs some LLM-as-a-Judge evaluators.

## 🚀 Getting Started

To run this project, you need to first start the MCP server, and then run the client notebook.

### Step 1: Start the MCP Server

Open your terminal and run the Python server file. This will make the financial data and live web search tools available to your client.

```bash
python mcp_server_financial_tools.py
```

Ensure that OLLAMA_API_KEY environment variable is set from the Terminal beforehand, or the MCP Server will not run.  This key is needed for the live web search.  Get your free Ollama API Key here: https://ollama.com/settings/keys

For Windows PowerShell users, the command is:
```bash
$Env:OLLAMA_API_KEY = "your_api_key"
```


### Step 2: Run the Client Notebook

Open `financial_agent_crew_evals.ipynb` in your Jupyter environment. You can then run the cells in the notebook sequentially to:

1. Connect to the MCP Server.
    * You'll need to run `python mcp_server_financial_tools.py` in a Terminal before running this notebook.
    * Ensure that OLLAMA_API_KEY environment variable is set from the Terminal beforehand, or the MCP Server will not run.  Get your free Ollama API Key here: https://ollama.com/settings/keys
        * For Windows PowerShell users, the command is: `$Env:OLLAMA_API_KEY = "your_api_key"`
2. Retreive and list all the available MCP Tools.
3. Define the LLM to be used by each Agent.  While the same LLM is used across Agents, I use different `temperature` settings to give different agents more creativity (i.e. higher temperature).
    * With `use_local_llm = True` it will use Ollama model locally (llama3.1).
    * With `use_local_llm = False` it will use Ollama Cloud (gpt-oss:120b-cloud).  For this choice you'll need to set `ollama_cloud_api_key` with your Ollama API Key (get it free here:  https://ollama.com/settings/keys)
4. Define the Agents to be used in the Crew.  Each Agent has a specialized ability (e.g. analyze stock prices, analyze estimates data, run web searches, write stock reports).  I've enabled `reasoning` for all Agents since these tasks are somewhat complex and need some autonomous thought.
5. Define the Tasks to be run by the Crew.  It's important that follow-on Tasks receive the `context` from the previous Task it depends on (e.g. can't search for bullish analyst reasons if it doesn't know the most bullish analysts.)
6. Define the Crew.  Since this is `sequential`, the order of Tasks matters.
7. Review the final Stock Report.
8. Examine some Spans from the tracing.  I'm particularly focused on Tool usage by the Crew of Agents.
9. Create and execute LLM-as-a-Judge Evaluators to verify whether the final Stock Report cites the most Bullish analyst and most Bearish analyst, along with their reasoning for their views.
10. (Optional) Debugging Zone to explore individual Tools, Agents and Tasks.

## 🔧 Project Details

This project uses the following key technologies:

- **MCP (Model Context Protocol):** For building and communicating with the tool server.
- **`yfinance`:** The library used by the server to fetch financial data.
- **`ollama`:** An LLM used to power the AI agent, with both local and cloud options.  Ollama recently added `web_search` and `web_fetch` tools for access to live web results.
- **`crewai`:** A library for building agent crews to perform multi-step tasks.
- **`phoenix`:** A library for observability and evaluation.

This is a simplified setup intended for learning. It's not designed for production use, as noted in the notebook, due to the way connections are handled for ease of experimentation.