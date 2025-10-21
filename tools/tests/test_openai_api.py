#!/usr/bin/env python3
"""
Test script for LLMServingSim OpenAI-compatible API
This script demonstrates how to use the OpenAI-compatible endpoints
"""

import requests
import json
import time
import sys

def test_models_endpoint(base_url):
    """Test the models endpoint"""
    print("📋 Testing /v1/models endpoint...")
    try:
        response = requests.get(f"{base_url}/v1/models")
        if response.status_code == 200:
            print("✅ Models endpoint working")
            models = response.json()
            print(f"   Available models: {len(models['data'])}")
            for model in models['data']:
                print(f"   - {model['id']}")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False

def test_chat_completions(base_url):
    """Test OpenAI chat completions endpoint"""
    print("\n💬 Testing /v1/chat/completions endpoint...")
    
    try:
        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! How are you today?"}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            print("✅ Chat completions endpoint working")
            result = response.json()
            print(f"   Response ID: {result.get('id')}")
            print(f"   Model: {result.get('model')}")
            print(f"   Message: {result['choices'][0]['message']['content']}")
            print(f"   Usage: {result.get('usage')}")
        else:
            print(f"❌ Chat completions failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Chat completions error: {e}")
        return False

def test_completions(base_url):
    """Test OpenAI completions endpoint"""
    print("\n📝 Testing /v1/completions endpoint...")
    
    try:
        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "prompt": "The future of artificial intelligence is",
            "max_tokens": 100,
            "temperature": 0.8
        }
        
        response = requests.post(
            f"{base_url}/v1/completions",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            print("✅ Completions endpoint working")
            result = response.json()
            print(f"   Response ID: {result.get('id')}")
            print(f"   Model: {result.get('model')}")
            print(f"   Text: {result['choices'][0]['text']}")
            print(f"   Usage: {result.get('usage')}")
        else:
            print(f"❌ Completions failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Completions error: {e}")
        return False

def test_with_openai_client(base_url):
    """Test using the official OpenAI Python client"""
    print("\n🐍 Testing with OpenAI Python client...")
    
    try:
        # Try to import OpenAI client
        try:
            from openai import OpenAI
        except ImportError:
            print("⚠️  OpenAI client not installed. Install with: pip install openai")
            return False
        
        # Create client pointing to our local server
        client = OpenAI(
            api_key="dummy-key",  # LLMServingSim doesn't require real API key
            base_url=base_url + "/v1"
        )
        
        # Test chat completions
        print("   Testing chat completions with OpenAI client...")
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Explain quantum computing briefly."}
            ],
            max_tokens=100
        )
        
        print("✅ OpenAI client working!")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI client error: {e}")
        return False

def test_curl_examples(base_url):
    """Show curl examples for testing"""
    print(f"\n🌐 Curl examples for testing {base_url}:")
    print("=" * 60)
    
    print("1. List models:")
    print(f"curl {base_url}/v1/models")
    
    print("\n2. Chat completions:")
    print(f"""curl -X POST {base_url}/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [
      {{"role": "user", "content": "Hello!"}}
    ],
    "max_tokens": 100
  }}'""")
    
    print("\n3. Text completions:")
    print(f"""curl -X POST {base_url}/v1/completions \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "prompt": "The future of AI is",
    "max_tokens": 50
  }}'""")
    
    print("\n4. Health check:")
    print(f"curl {base_url}/health")

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🧪 Testing LLMServingSim OpenAI-compatible API at {base_url}")
    print("=" * 70)
    
    # Test all endpoints
    success_count = 0
    total_tests = 4
    
    if test_models_endpoint(base_url):
        success_count += 1
    
    if test_chat_completions(base_url):
        success_count += 1
    
    if test_completions(base_url):
        success_count += 1
    
    if test_with_openai_client(base_url):
        success_count += 1
    
    # Show curl examples
    test_curl_examples(base_url)
    
    print("\n" + "=" * 70)
    print(f"🎯 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Your OpenAI-compatible API is working!")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
    
    print(f"\n📝 To use with OpenAI client libraries, set base_url to: {base_url}/v1")

if __name__ == "__main__":
    main()
