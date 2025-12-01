import sys
import os
import yaml
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.registry import build_tools_from_yaml

def test_tool_creation():
    print("Testing tool creation from YAML...")
    
    # Mock client
    mock_client = MagicMock()
    
    # Test case 1: OpenAPI tool (as in simple-agent.yaml)
    yaml_config = [
        {
            "type": "openapi",
            "id": "WebSearch",
            "description": "Search the web",
            "options": {
                "specification": "https://example.com/spec.json",
                "auth": {"type": "anonymous"}
            }
        }
    ]
    
    tools = build_tools_from_yaml(mock_client, yaml_config)
    assert len(tools) == 1
    print("✓ OpenAPI tool created")
    
    # Test case 2: Azure AI Search
    yaml_config_search = [
        {
            "type": "azure_ai_search",
            "id": "MySearch",
            "options": {
                "connection_id": "CONN_1",
                "index_name": "index-1"
            }
        }
    ]
    tools = build_tools_from_yaml(mock_client, yaml_config_search)
    assert len(tools) == 1
    print("✓ Azure AI Search tool created")

    print("\nAll tests passed!")

if __name__ == "__main__":
    test_tool_creation()
