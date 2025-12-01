# tools/registry.py

from typing import List, Dict
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAISearchAgentTool,
    FileSearchTool,
    OpenApiAgentTool,
    CodeInterpreterTool,
    MCPTool
)


def build_tools_from_yaml(project_client: AIProjectClient, tools_cfg: List[Dict]):
    """
    Convert logical YAML tool entries into concrete Tool objects
    for Azure AI Foundry Agent Service.

    - YAML defines: type, id, options
    """
    tools = []

    for t in tools_cfg or []:
        tool_type = t.get("type")
        tool_id = t.get("id") # This is often the name
        options = t.get("options", {})
        
        # Fallback for older schema if 'kind'/'name' are used
        if not tool_type and "kind" in t:
             tool_type = t.get("kind")
        if not tool_id and "name" in t:
             tool_id = t.get("name")

        if not tool_type:
            print(f"⚠ Tool entry missing 'type': {t}, skipping")
            continue

        # 1) Generic Azure AI Search tool
        if tool_type == "azure_ai_search":
            connection_id = options.get("connection_id", "CONN_PRIMARY_SEARCH")
            index_name = options.get("index_name", "primary-search-index")
            tools.append(
                AzureAISearchAgentTool(
                    name=tool_id,
                    connection_id=connection_id,
                    index_name=index_name,
                )
            )

        # 2) File Search / vector store
        elif tool_type == "file_search":
            vector_store_id = options.get("vector_store_id")
            if not vector_store_id:
                 # Try to find a default or raise warning
                 print(f"⚠ file_search tool '{tool_id}' missing 'vector_store_id' in options")
            
            tools.append(
                FileSearchTool(
                    name=tool_id,
                    vector_store_id=vector_store_id,
                )
            )

        # 3) OpenAPI-based tool
        elif tool_type == "openapi":
            spec_url = options.get("specification")
            if not spec_url:
                 # Fallback to 'spec_url' if used in other schemas
                 spec_url = options.get("spec_url")
            
            if not spec_url:
                raise ValueError(f"OpenAPI tool '{tool_id}' missing 'specification' URL")

            # Check for auth config
            auth_config = options.get("auth", {"type": "anonymous"})
            # For now we only support anonymous in this simple registry, 
            # but you could expand to handle connection_id based auth.
            
            # If a connection_id is provided for the tool itself (not just auth)
            connection_id = options.get("connection_id")

            # Only pass supported arguments (spec_url, connection_id)
            if connection_id:
                tools.append(
                    OpenApiAgentTool(
                        spec_url=spec_url,
                        connection_id=connection_id
                    )
                )
            else:
                tools.append(
                    OpenApiAgentTool(
                        spec_url=spec_url
                    )
                )

        # 4) MCP Tool
        elif tool_type == "mcp":
            server_url = options.get("server_url")
            allowed_tools = options.get("allowed_tools", [])
            if not server_url:
                 raise ValueError(f"MCP tool '{tool_id}' missing 'server_url'")
            
            tools.append(
                MCPTool(
                    name=tool_id,
                    server_url=server_url,
                    allowed_tools=allowed_tools,
                )
            )

        # 5) Code interpreter
        elif tool_type == "code_interpreter":
            tools.append(
                CodeInterpreterTool(
                    name=tool_id,
                    # Optional overrides
                    max_execution_time_seconds=options.get("max_execution_time_seconds"),
                    memory_limit_mb=options.get("memory_limit_mb"),
                )
            )
            
        # 6) Bing Connection (if treated as a tool type or connection)
        elif tool_type == "bing_connection":
             # This might be a specific implementation or just a connection reference
             # For now, we can skip or implement if we have a class for it.
             # Assuming it might be an OpenAPI tool wrapping Bing or similar.
             pass

        else:
            print(f"⚠ Unsupported tool type '{tool_type}' in YAML")

    return tools