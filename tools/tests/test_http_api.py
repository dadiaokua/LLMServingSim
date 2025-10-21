#!/usr/bin/env python3
"""
Test script for LLMServingSim HTTP API
This script demonstrates how to send requests to the HTTP server
"""

import requests
import json
import time
import sys

def test_health_check(base_url):
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_status(base_url):
    """Test status endpoint"""
    print("\n📊 Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            print("✅ Status check passed")
            status = response.json()
            print(f"   Pending requests: {status.get('pending_requests', 'N/A')}")
            print(f"   Inflight batches: {status.get('inflight_batches', 'N/A')}")
            print(f"   Completed requests: {status.get('completed_requests', 'N/A')}")
            memory = status.get('memory_usage', {})
            print(f"   Memory usage: {memory.get('used', 'N/A')}/{memory.get('total', 'N/A')} bytes")
        else:
            print(f"❌ Status check failed: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_generate_request(base_url, prompt, max_tokens=128):
    """Test text generation endpoint"""
    print(f"\n🚀 Testing generation request...")
    print(f"   Prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
    print(f"   Max tokens: {max_tokens}")
    
    try:
        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            f"{base_url}/generate",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            print("✅ Generation request accepted")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Estimated input tokens: {result.get('estimated_input_tokens')}")
            print(f"   Estimated output tokens: {result.get('estimated_output_tokens')}")
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Generation request error: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🧪 Testing LLMServingSim HTTP API at {base_url}")
    print("=" * 60)
    
    # Test health check
    if not test_health_check(base_url):
        print("\n❌ Server appears to be down or not responding")
        print("Make sure to start LLMServingSim with --idle_mode flag:")
        print("python main.py --idle_mode --verbose")
        return
    
    # Test status
    test_status(base_url)
    
    # Test generation requests
    test_prompts = [
        "Hello, how are you today?",
        "Explain quantum computing in simple terms.",
        "Write a short story about a robot learning to paint.",
        "What is the capital of France?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}/{len(test_prompts)} ---")
        test_generate_request(base_url, prompt, max_tokens=64)
        
        # Check status after each request
        time.sleep(1)  # Give the server a moment
        test_status(base_url)
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed!")
    print("\nTo monitor the server logs, check the LLMServingSim console output.")

if __name__ == "__main__":
    main()
