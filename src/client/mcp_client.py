from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import logging
import json
import os
import asyncio
import ollama



# Enable logging but set to INFO to reduce noise
logging.basicConfig(level=logging.INFO)

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=["src/server/mcp_server.py"],  # relative path to the server script
    env=None  # Optional environment variables
)

# Initialize Ollama client
ollama_client = ollama.AsyncClient()

# Store conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

async def run():
    print("\n===== MCP CLIENT WITH OLLAMA INTEGRATION =====")
    print("This client connects to a local MCP server and a local Ollama instance")
    
    async with stdio_client(server_params) as (read, write):
        print("\nConnected to server via stdio")
        
        # Create a sampling callback that uses Ollama
        async def handle_ollama_sampling(message: types.CreateMessageRequestParams) -> types.CreateMessageResult:
            try:
                # Get the user's message content
                user_content = ""
                if message.messages and len(message.messages) > 0:
                    last_message = message.messages[-1]
                    if hasattr(last_message, "content"):
                        for content_item in last_message.content:
                            if content_item.type == "text":
                                user_content += content_item.text
                
                if not user_content:
                    user_content = "Hello, please assist me."
                
                # Update conversation history
                conversation_history.append({"role": "user", "content": user_content})
                
                # Call Ollama API with the full conversation history
                response = await ollama_client.chat(
                    model="qwen3:8b",
                    messages=conversation_history
                )
                
                # Get the generated text from Ollama
                ai_text = response['message']['content']
                
                # Update conversation history with assistant's response
                conversation_history.append({"role": "assistant", "content": ai_text})
                
                return types.CreateMessageResult(
                    role="assistant",
                    content=types.TextContent(
                        type="text",
                        text=ai_text,
                    ),
                    model="qwen3:8b",
                    stopReason="endTurn",
                )
            except Exception as e:
                print(f"Error in Ollama sampling: {e}")
                return types.CreateMessageResult(
                    role="assistant",
                    content=types.TextContent(
                        type="text",
                        text=f"I encountered an error: {str(e)}",
                    ),
                    model="qwen3:8b",
                    stopReason="error",
                )
        

        async with ClientSession(read, write, sampling_callback=handle_ollama_sampling) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            print("Checking available tools...")
            tools = await session.list_tools()
            
            # Prepare tool definitions for Ollama
            server_tools_list_for_prompt = []
            ollama_tools_definition = []
            if tools and tools.tools:
                for tool_def in tools.tools:
                    # Ensure parameters is a valid JSON schema object, even if empty
                    parameters_schema_for_ollama = {}
                    if hasattr(tool_def, 'input_schema') and tool_def.input_schema and isinstance(tool_def.input_schema, dict):
                        parameters_schema_for_ollama = tool_def.input_schema
                    else:
                        # Ollama requires a parameters object, even if it's for a tool with no parameters.
                        # It should be a valid JSON schema.
                        parameters_schema_for_ollama = {"type": "object", "properties": {}}

                    server_tools_list_for_prompt.append({
                        "name": tool_def.name,
                        "description": tool_def.description,
                        "parameters": parameters_schema_for_ollama # Corrected usage
                    })
                    ollama_tools_definition.append({
                        "type": "function",
                        "function": {
                            "name": tool_def.name,
                            "description": tool_def.description,
                            "parameters": parameters_schema_for_ollama, # Corrected usage
                        }
                    })
                
                tool_names_for_print = [tool_def.name for tool_def in tools.tools]
                print(f"Found {len(tools.tools)} tools available for LLM: {', '.join(tool_names_for_print)}\n")
            else:
                print("No server-side tools found for LLM to use.\n")

            
            conversation_history = [
                {"role": "system", "content": "You are a helpful assistant. You have access to tools and should use them when appropriate to answer user queries or perform actions. /no_think"}
            ]
            
            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() == 'exit':
                    break
                    
                conversation_history.append({"role": "user", "content": user_input})
                
                try:
                    # Call Ollama with tool definitions
                    response = await ollama_client.chat(
                        model="qwen3:8b",
                        messages=conversation_history,
                        tools=ollama_tools_definition if ollama_tools_definition else None
                    )
                    
                    print(f"Ollama response: {response}")
                    assistant_message = response['message']
                    conversation_history.append(assistant_message) # Add assistant's response (potentially with tool_calls)
                    
                    if assistant_message.get('tool_calls'):
                        print("\nAssistant wants to use tools:")
                        for tool_call in assistant_message['tool_calls']:
                            tool_name = tool_call['function']['name']
                            tool_args_from_llm = tool_call['function']['arguments']
                            tool_call_id = tool_call.get('id', f"tool_{len(conversation_history)}")

                            # Map arguments if necessary (e.g., for calculate_bmi)
                            tool_args_for_server = tool_args_from_llm.copy()
                            if tool_name == "calculate_bmi":
                                if "weight" in tool_args_for_server and "weight_kg" not in tool_args_for_server:
                                    tool_args_for_server["weight_kg"] = tool_args_for_server.pop("weight")
                                if "height" in tool_args_for_server and "height_m" not in tool_args_for_server:
                                    tool_args_for_server["height_m"] = tool_args_for_server.pop("height")

                            print(f"  - Calling tool: {tool_name} with processed args: {json.dumps(tool_args_for_server)}")
                            
                            try:
                                tool_call_response_object = await session.call_tool(tool_name, arguments=tool_args_for_server)
                                
                                # Check for server-side error in CallToolResult before accessing .result
                                if hasattr(tool_call_response_object, 'error') and tool_call_response_object.error:
                                    error_content = tool_call_response_object.error
                                    print(f"  - Tool '{tool_name}' reported an error: {error_content}")
                                    # Store the error content for the LLM to process
                                    actual_tool_output_for_llm = {"error": error_content}
                                elif hasattr(tool_call_response_object, 'result'):
                                    actual_tool_output_for_llm = tool_call_response_object.result
                                    print(f"  - Tool '{tool_name}' result: {json.dumps(actual_tool_output_for_llm)}")
                                elif hasattr(tool_call_response_object, 'content') and \
                                        isinstance(tool_call_response_object.content, list) and \
                                        len(tool_call_response_object.content) > 0 and \
                                        hasattr(tool_call_response_object.content[0], 'text') and \
                                        getattr(tool_call_response_object.content[0], 'type', None) == 'text':
                                    # Extract text from the first text content block
                                    actual_tool_output_for_llm = tool_call_response_object.content[0].text
                                    print(f"  - Tool '{tool_name}' result (from content.text): {json.dumps(actual_tool_output_for_llm)}")
                                else:
                                    # Fallback if structure is unexpected
                                    print(f"  - Tool '{tool_name}' returned an unexpected object: {tool_call_response_object}")

                                conversation_history.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call_id, 
                                    "name": tool_name,
                                    "content": json.dumps(actual_tool_output_for_llm) 
                                })
                            except Exception as e:
                                print(f"  - Error calling tool {tool_name}: {e}")
                                conversation_history.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call_id,
                                    "name": tool_name,
                                    "content": json.dumps({"error": str(e)}) # Report error back to LLM
                                })
                        
                        # Get final response from Ollama after tool execution
                        final_response_obj = await ollama_client.chat(
                            model="qwen3:8b",
                            messages=conversation_history,
                            tools=ollama_tools_definition if ollama_tools_definition else None # Good to pass tools again
                        )
                        final_assistant_text = final_response_obj['message']['content']
                        print(f"\nAssistant: {final_assistant_text}")
                        conversation_history.append(final_response_obj['message'])
                        
                    else:
                        # No tool calls, direct response
                        assistant_response_text = assistant_message['content']
                        print(f"\nAssistant: {assistant_response_text}")
                        # Assistant message already added to history
                
                except Exception as e:
                    print(f"\nError during chat processing: {e}")
                    # Add a generic error message to history to inform the LLM if needed for context
                    conversation_history.append({"role": "assistant", "content": f"An error occurred: {str(e)}"})

   
                

if __name__ == "__main__":
    asyncio.run(run())
