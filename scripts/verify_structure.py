#!/usr/bin/env python3
"""
Verify that all scripts and pipelines reference the correct file paths
after the repository reorganization.
"""

import sys
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and print result."""
    path = Path(file_path)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_file_content(file_path: str, search_strings: list, description: str) -> bool:
    """Check if file contains expected strings."""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ {description}: File not found - {file_path}")
        return False
    
    content = path.read_text()
    all_found = True
    
    for search_str in search_strings:
        if search_str in content:
            print(f"✅ {description}: Found '{search_str}'")
        else:
            print(f"❌ {description}: Missing '{search_str}'")
            all_found = False
    
    return all_found

def main():
    print("=" * 70)
    print("Repository Structure Verification")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # Check infrastructure files
    print("📁 Infrastructure Files:")
    all_checks_passed &= check_file_exists(
        "infrastructure/modules/connections/connection.bicep",
        "Connections Bicep template"
    )
    all_checks_passed &= check_file_exists(
        "infrastructure/modules/connections/api.json",
        "OpenAPI specification"
    )
    all_checks_passed &= check_file_exists(
        "infrastructure/modules/guardrails/content_filter.bicep",
        "Guardrails Bicep template"
    )
    all_checks_passed &= check_file_exists(
        "infrastructure/parameters/connections.bicepparam",
        "Connections parameters"
    )
    all_checks_passed &= check_file_exists(
        "infrastructure/parameters/guardrails.bicepparam",
        "Guardrails parameters"
    )
    print()
    
    # Check scripts
    print("🔧 Deployment Scripts:")
    all_checks_passed &= check_file_exists(
        "scripts/deploy_infrastructure.py",
        "Infrastructure deployment script"
    )
    all_checks_passed &= check_file_exists(
        "scripts/deploy_agent.py",
        "Agent deployment script"
    )
    all_checks_passed &= check_file_exists(
        "scripts/deploy_guardrails.py",
        "Guardrails deployment script"
    )
    all_checks_passed &= check_file_exists(
        "scripts/tool_factory.py",
        "Tool factory"
    )
    print()
    
    # Check pipelines
    print("🚀 CI/CD Pipelines:")
    all_checks_passed &= check_file_exists(
        "pipelines/infrastructure-pipeline.yml",
        "Infrastructure pipeline"
    )
    all_checks_passed &= check_file_exists(
        "pipelines/agent-pipeline.yml",
        "Agent pipeline"
    )
    all_checks_passed &= check_file_exists(
        "pipelines/guardrails-pipeline.yml",
        "Guardrails pipeline"
    )
    print()
    
    # Check script references
    print("🔍 Script Path References:")
    all_checks_passed &= check_file_content(
        "scripts/deploy_infrastructure.py",
        ["infrastructure/modules/connections/connection.bicep",
         "infrastructure/parameters/connections.bicepparam"],
        "deploy_infrastructure.py paths"
    )
    # deploy_guardrails.py uses Path objects, so check for path components
    all_checks_passed &= check_file_content(
        "scripts/deploy_guardrails.py",
        ["'infrastructure'", "'modules'", "'guardrails'", "'content_filter.bicep'",
         "'parameters'", "'guardrails.bicepparam'"],
        "deploy_guardrails.py path components"
    )
    print()
    
    # Check pipeline references
    print("🔍 Pipeline Path References:")
    all_checks_passed &= check_file_content(
        "pipelines/infrastructure-pipeline.yml",
        ["infrastructure/parameters/connections.bicepparam"],
        "infrastructure-pipeline.yml paths"
    )
    all_checks_passed &= check_file_content(
        "pipelines/guardrails-pipeline.yml",
        ["infrastructure/modules/guardrails/content_filter.bicep",
         "infrastructure/parameters/guardrails.bicepparam"],
        "guardrails-pipeline.yml paths"
    )
    print()
    
    # Check documentation
    print("📚 Documentation:")
    all_checks_passed &= check_file_exists(
        "README.md",
        "Main README"
    )
    all_checks_passed &= check_file_exists(
        "docs/GUARDRAILS.md",
        "Guardrails documentation"
    )
    all_checks_passed &= check_file_exists(
        "ORGANIZATION.md",
        "Organization guide"
    )
    print()
    
    # Summary
    print("=" * 70)
    if all_checks_passed:
        print("✅ All checks passed! Repository structure is correct.")
        print("=" * 70)
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
