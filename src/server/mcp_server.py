from mcp.server.fastmcp import FastMCP
import httpx
import asyncio
from pathlib import Path
import os
import logging
import click
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Scope, Receive, Send
import uvicorn
import contextlib
from typing import AsyncIterator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Python360")


# --- Generic Tools ---

@mcp.tool()
async def fetch_weather(latitude: float, longitude: float) -> str:
    """Fetch current weather for a location using latitude and longitude"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&current=temperature_2m"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text




# --- File System Tools ---

@mcp.tool()
def list_items(path: str) -> dict:
    """
    Lists files and folders in a given directory path.
    Returns a dictionary with 'files' and 'directories' lists, or an 'error' message.
    """
    try:
        target_path = Path(path)
        if not target_path.exists():
            return {"error": f"Path not found: {path}"}
        if not target_path.is_dir():
            return {"error": f"Path is not a directory: {path}"}

        items = os.listdir(target_path)
        files = [item for item in items if (target_path / item).is_file()]
        directories = [item for item in items if (target_path / item).is_dir()]
        
        return {"files": files, "directories": directories, "path": str(target_path)}
    except PermissionError:
        return {"error": f"Permission denied for path: {path}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
def create_text_file(file_path: str, content: str) -> dict:
    """
    Creates a new file with the given text content at the specified path.
    Returns a success message or an error message.
    """
    try:
        target_file_path = Path(file_path)
        
        parent_dir = target_file_path.parent
        if not parent_dir.exists():
            return {"error": f"Parent directory does not exist: {parent_dir}"}
        if not parent_dir.is_dir():
            return {"error": f"Parent path is not a directory: {parent_dir}"}
        
        if target_file_path.exists():
            return {"error": f"File already exists: {file_path}"}

        with open(target_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"File created: {file_path}"}
    except PermissionError:
        return {"error": f"Permission denied for path: {file_path}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
def create_directory(directory_path: str) -> dict:
    """
    Creates a new directory at the specified path.
    Returns a success message or an error message.
    """
    try:
        target_dir_path = Path(directory_path)
        
        if target_dir_path.exists():
            if target_dir_path.is_dir():
                return {"error": f"Directory already exists: {directory_path}"}
            else:
                return {"error": f"A file with the same name already exists: {directory_path}"}
        
        parent_dir = target_dir_path.parent
        if not parent_dir.exists():
            return {"error": f"Parent directory does not exist: {parent_dir}"}
        if not parent_dir.is_dir():
             return {"error": f"Parent path is not a directory: {parent_dir}"}

        os.makedirs(target_dir_path, exist_ok=False)
        return {"success": True, "message": f"Directory created: {directory_path}"}
    except PermissionError:
        return {"error": f"Permission denied for path: {directory_path}"}
    except FileExistsError:
        return {"error": f"Directory already exists (caught by FileExistsError): {directory_path}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
def search_items(path: str, search_query: str) -> dict:
    """
    Searches for files and folders within a given path (recursively)
    whose names contain the search_query.
    Returns a dictionary with 'found_files' and 'found_directories' lists, or an 'error' message.
    """
    try:
        target_path = Path(path)
        if not target_path.exists():
            return {"error": f"Path not found: {path}"}
        if not target_path.is_dir():
            return {"error": f"Path is not a directory: {path}"}

        found_files = []
        found_directories = []

        for root, dirs, files_in_dir in os.walk(target_path):
            for dirname in dirs:
                if search_query.lower() in dirname.lower():
                    found_directories.append(str(Path(root) / dirname))
            for filename in files_in_dir:
                if search_query.lower() in filename.lower():
                    found_files.append(str(Path(root) / filename))
        
        return {
            "searched_path": str(target_path),
            "query": search_query,
            "found_files": found_files,
            "found_directories": found_directories
        }
    except PermissionError:
        return {"error": f"Permission denied while searching in path: {path}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred during search: {str(e)}"}


@click.command()
@click.option("--port", default=8085, help="Port to listen on for HTTP")
@click.option(
    "--host", default="127.0.0.1", help="Host to bind server to"
)
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
def main(
    port: int,
    host: str,
    log_level: str,
) -> int:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # ASGI handler for MCP server
    async def handle_mcp(scope: Scope, receive: Receive, send: Send) -> None:
        await mcp.handle_asgi(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for managing application lifecycle."""
        logger.info(f"MCP Server starting on {host}:{port}")
        try:
            yield
        finally:
            logger.info("MCP Server shutting down...")

    # Create an ASGI application using Starlette
    app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_mcp),
        ],
        lifespan=lifespan,
    )

    # Run the server with uvicorn
    uvicorn.run(app, host=host, port=port)
    return 0


if __name__ == "__main__":
    main()