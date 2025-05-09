# Project Readme

## Setup

1.  **Conda Env:**
    *   Make a conda env: `conda create -n mcp_env python=3.10` 
    *   Activate it: `conda activate mcp_env`

2.  **Install Stuff:**
    *   `pip install -r requirements.txt` 

## Run

*   Just run the client: `python src/client/mcp_client.py`
*   The client starts the server by itself.
*   If you want to run server alone: `python src/server/mcp_server.py` 

## Models
- You wll need to have ollama running, or any Openai API spec server
- Currently using `qwen3:8b`. I have added `/no_think` to the system prompt so that it doesnt spend time on the thinking tokens, you can remove those if you need it to reason more.


Oh, and type `exit` to stop the conversation.

