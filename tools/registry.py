# tools/registry.py

from typing import List, Dict
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAISearchTool,
    FileSearchTool,
    OpenApiTool,
    CodeInterpreterTool,
    McpTool
)


def build_tools_from_yaml(project_client: AIProjectClient, tools_cfg: List[Dict]):
    """
    Convert logical YAML tool entries into concrete Tool objects
    for Azure AI Foundry Agent Service.

    - YAML defines: name, kind, config_profile
    - This registry owns: connection IDs, index names, vector store IDs, URLs, etc.
    """
    tools = []

    for t in tools_cfg or []:
        kind = t.get("kind")
        name = t.get("name")
        profile = t.get("config_profile")

        if not kind or not name:
            raise ValueError(f"Tool entry missing 'kind' or 'name': {t}")

        # 1) Generic Azure AI Search tool
        if kind == "azure_ai_search":
            if profile == "search_primary_v1":
                tools.append(
                    AzureAISearchTool(
                        name=name,
                        # These connection IDs must exist as project connections in AI Foundry
                        connection_id="CONN_PRIMARY_SEARCH",
                        index_name="primary-search-index",
                        query_type="hybrid",
                        top_k=10,
                    )
                )
            else:
                raise ValueError(f"Unknown config_profile '{profile}' for azure_ai_search")

        # 2) File Search / vector store for policy docs
        elif kind == "file_search":
            if profile == "policy_docs_v1":
                tools.append(
                    FileSearchTool(
                        name=name,
                        vector_store_id="VECTOR_POLICY_DOCS",
                    )
                )
            else:
                raise ValueError(f"Unknown config_profile '{profile}' for file_search")

        # 3) OpenAPI-based metrics API
        elif kind == "openapi":
            if profile == "metrics_api_v1":
                tools.append(
                    OpenApiTool.from_openapi_spec(
                        name=name,
                        # Replace with your org's metrics OpenAPI spec URL
                        spec_url="https://internal.example.com/apis/metrics/openapi.json",
                        connection_id="CONN_METRICS_API",
                    )
                )
            else:
                raise ValueError(f"Unknown config_profile '{profile}' for openapi")

        # 4) Optional MCP example (not used in key-insights-agent yet)
        elif kind == "mcp":
            if profile == "example_mcp_v1":
                tools.append(
                    McpTool(
                        name=name,
                        server_url="https://mcp.example.com",
                        allowed_tools=["get_entity", "search_entities"],
                    )
                )
            else:
                raise ValueError(f"Unknown config_profile '{profile}' for mcp")

        # 5) Code interpreter sandbox
        elif kind == "code_interpreter":
            # For now use same parameters for all profiles
            tools.append(
                CodeInterpreterTool(
                    name=name,
                    max_execution_time_seconds=30,
                    memory_limit_mb=512,
                )
            )

        else:
            raise ValueError(f"Unsupported tool kind '{kind}' in YAML")

    return tools