#!/usr/bin/env python3
"""Simple AWS connectivity test."""

try:
    import boto3
    print("✅ boto3 is available")
    
    # Test AWS credentials
    session = boto3.Session()
    sts = session.client('sts')
    identity = sts.get_caller_identity()
    print(f"✅ AWS Identity: {identity.get('Arn', 'Unknown')}")
    
    # Test Bedrock access
    bedrock = session.client('bedrock', region_name='us-east-1')
    models = bedrock.list_foundation_models()
    print(f"✅ Bedrock access: Found {len(models.get('modelSummaries', []))} models")
    
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
except Exception as e:
    print(f"❌ AWS Error: {e}")