#!/usr/bin/env python3
"""
Deploy AI Foundry Guardrails (Content Filters) to Azure.

Usage:
    python scripts/deploy_guardrails.py nonprod
    python scripts/deploy_guardrails.py prod
"""

import sys
import os
import subprocess
from pathlib import Path


def deploy_guardrails(environment: str = 'nonprod'):
    """
    Deploy guardrails using Bicep templates.
    
    Args:
        environment: Target environment (for deployment naming)
    """
    # Paths
    project_root = Path(__file__).parent.parent
    bicep_file = project_root / 'infrastructure' / 'modules' / 'guardrails' / 'content_filter.bicep'
    param_file = project_root / 'infrastructure' / 'parameters' / 'guardrails' / 'guardrails.bicepparam'
    
    if not bicep_file.exists():
        raise FileNotFoundError(f"Bicep template not found: {bicep_file}")
    
    if not param_file.exists():
        raise FileNotFoundError(f"Parameters file not found: {param_file}")
    
    # Get resource group from environment or use default
    resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'ad-usa-poc')
    
    print(f"\n{'='*70}")
    print(f"🛡️  Deploying AI Foundry Guardrails")
    print(f"{'='*70}")
    print(f"Environment:     {environment}")
    print(f"Resource Group:  {resource_group}")
    print(f"Bicep Template:  {bicep_file.name}")
    print(f"Parameters:      {param_file.name}")
    print(f"{'='*70}\n")
    
    # Step 1: Validate Bicep template
    print("Step 1: Validating Bicep template...")
    try:
        subprocess.run(
            ['az', 'bicep', 'build', '--file', str(bicep_file)],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Bicep template is valid\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Bicep validation failed:")
        print(e.stderr)
        sys.exit(1)
    
    # Step 2: Run what-if analysis
    print("Step 2: Running what-if analysis...")
    deployment_name = f"guardrails-{environment}-whatif"
    
    try:
        result = subprocess.run(
            [
                'az', 'deployment', 'group', 'what-if',
                '--resource-group', resource_group,
                '--template-file', str(bicep_file),
                '--parameters', str(param_file),
                '--name', deployment_name
            ],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  What-if analysis failed (this might be expected):")
        print(e.stderr)
        # Don't exit - what-if can fail for various reasons
    
    # Step 3: Deploy
    print("\nStep 3: Deploying content filter...")
    deployment_name = f"guardrails-{environment}"
    
    try:
        result = subprocess.run(
            [
                'az', 'deployment', 'group', 'create',
                '--resource-group', resource_group,
                '--template-file', str(bicep_file),
                '--parameters', str(param_file),
                '--name', deployment_name
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        print("✅ Deployment completed successfully!")
        print("\nDeployment outputs:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed:")
        print(e.stderr)
        sys.exit(1)
    
    # Step 4: Verify deployment
    print("\nStep 4: Verifying deployment...")
    try:
        result = subprocess.run(
            [
                'az', 'deployment', 'group', 'show',
                '--resource-group', resource_group,
                '--name', deployment_name,
                '--query', 'properties.provisioningState',
                '-o', 'tsv'
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        status = result.stdout.strip()
        if status == 'Succeeded':
            print(f"✅ Deployment verified: {status}")
        else:
            print(f"⚠️  Deployment status: {status}")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed:")
        print(e.stderr)
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"✅ Guardrails deployment completed successfully!")
    print(f"{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/deploy_guardrails.py [environment]")
        print("\nEnvironment (optional, defaults to 'nonprod'):")
        print("  nonprod  - Deploy to non-production")
        print("  prod     - Deploy to production")
        print("\nExample:")
        print("  python3 scripts/deploy_guardrails.py nonprod")
        sys.exit(1)
    
    environment = sys.argv[1].lower() if len(sys.argv) > 1 else 'nonprod'
    
    try:
        deploy_guardrails(environment)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
