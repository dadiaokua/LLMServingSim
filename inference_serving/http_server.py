"""
HTTP Server for LLMServingSim
Provides OpenAI-compatible REST API endpoints to receive external requests
"""

import json
import threading
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

class LLMServingHandler(BaseHTTPRequestHandler):
    """HTTP request handler for LLM serving requests"""
    
    def __init__(self, request_api, *args, **kwargs):
        self.request_api = request_api
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        # OpenAI-compatible endpoints
        if parsed_path.path == '/v1/chat/completions':
            self._handle_chat_completions()
        elif parsed_path.path == '/v1/completions':
            self._handle_completions()
        # Legacy endpoints
        elif parsed_path.path == '/generate':
            self._handle_generate()
        elif parsed_path.path == '/status':
            self._handle_status()
        else:
            self._send_error(404, "Endpoint not found")
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # OpenAI-compatible endpoints
        if parsed_path.path == '/v1/models':
            self._handle_models()
        # Health and status endpoints
        elif parsed_path.path == '/health':
            self._handle_health()
        elif parsed_path.path == '/status':
            self._handle_status()
        else:
            self._send_error(404, "Endpoint not found")
    
    def _handle_chat_completions(self):
        """Handle OpenAI chat completions API"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract OpenAI API parameters
            model = request_data.get('model', 'meta-llama/Llama-3.1-8B-Instruct')
            messages = request_data.get('messages', [])
            max_tokens = request_data.get('max_tokens', 128)
            temperature = request_data.get('temperature', 1.0)
            stream = request_data.get('stream', False)
            
            # Convert messages to prompt (simple concatenation for simulation)
            prompt = self._messages_to_prompt(messages)
            
            # Estimate token counts
            input_length = len(prompt.split()) * 1.3  # rough token estimation
            output_length = int(input_length + max_tokens)
            
            # Add request to scheduler
            self.request_api.add_request(
                model=model,
                input_length=int(input_length),
                output_length=output_length
            )
            
            # Generate OpenAI-compatible response
            if stream:
                self._send_streaming_response(model, messages, max_tokens)
            else:
                self._send_chat_completion_response(model, messages, max_tokens, input_length)
                
        except Exception as e:
            self._send_openai_error(400, "invalid_request_error", str(e))
    
    def _handle_completions(self):
        """Handle OpenAI completions API"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract OpenAI API parameters
            model = request_data.get('model', 'meta-llama/Llama-3.1-8B-Instruct')
            prompt = request_data.get('prompt', '')
            max_tokens = request_data.get('max_tokens', 128)
            temperature = request_data.get('temperature', 1.0)
            stream = request_data.get('stream', False)
            
            # Estimate token counts
            input_length = len(prompt.split()) * 1.3  # rough token estimation
            output_length = int(input_length + max_tokens)
            
            # Add request to scheduler
            self.request_api.add_request(
                model=model,
                input_length=int(input_length),
                output_length=output_length
            )
            
            # Generate OpenAI-compatible response
            if stream:
                self._send_streaming_completion_response(model, prompt, max_tokens)
            else:
                self._send_completion_response(model, prompt, max_tokens, input_length)
                
        except Exception as e:
            self._send_openai_error(400, "invalid_request_error", str(e))
    
    def _handle_models(self):
        """Handle OpenAI models API"""
        models_response = {
            "object": "list",
            "data": [
                {
                    "id": "meta-llama/Llama-3.1-8B-Instruct",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "llmservingsim",
                    "permission": [],
                    "root": "meta-llama/Llama-3.1-8B-Instruct",
                    "parent": None
                }
            ]
        }
        self._send_json_response(200, models_response)
    
    def _messages_to_prompt(self, messages):
        """Convert OpenAI messages format to a simple prompt"""
        prompt_parts = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        return "\n".join(prompt_parts)
    
    def _send_chat_completion_response(self, model, messages, max_tokens, input_tokens):
        """Send OpenAI chat completion response"""
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"[LLMServingSim] Request queued for processing. Input tokens: {int(input_tokens)}, Max output tokens: {max_tokens}"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": int(input_tokens),
                "completion_tokens": max_tokens,
                "total_tokens": int(input_tokens) + max_tokens
            }
        }
        self._send_json_response(200, response)
    
    def _send_completion_response(self, model, prompt, max_tokens, input_tokens):
        """Send OpenAI completion response"""
        response = {
            "id": f"cmpl-{uuid.uuid4().hex[:8]}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "text": f"[LLMServingSim] Request queued for processing. Input tokens: {int(input_tokens)}, Max output tokens: {max_tokens}",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": int(input_tokens),
                "completion_tokens": max_tokens,
                "total_tokens": int(input_tokens) + max_tokens
            }
        }
        self._send_json_response(200, response)
    
    def _send_streaming_response(self, model, messages, max_tokens):
        """Send streaming chat completion response"""
        # For simulation, we'll send a simple non-streaming response
        # In a real implementation, this would stream tokens
        self._send_chat_completion_response(model, messages, max_tokens, 0)
    
    def _send_streaming_completion_response(self, model, prompt, max_tokens):
        """Send streaming completion response"""
        # For simulation, we'll send a simple non-streaming response
        # In a real implementation, this would stream tokens
        self._send_completion_response(model, prompt, max_tokens, 0)
    
    def _send_openai_error(self, status_code, error_type, message):
        """Send OpenAI-compatible error response"""
        error_response = {
            "error": {
                "message": message,
                "type": error_type,
                "param": None,
                "code": None
            }
        }
        self._send_json_response(status_code, error_response)
    
    def _handle_generate(self):
        """Handle text generation requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract request parameters
            model = request_data.get('model', 'meta-llama/Llama-3.1-8B-Instruct')
            prompt = request_data.get('prompt', '')
            max_tokens = request_data.get('max_tokens', 128)
            
            # Estimate input length (rough approximation)
            input_length = len(prompt.split()) * 1.3  # rough token estimation
            output_length = int(input_length + max_tokens)
            
            # Add request to scheduler
            self.request_api.add_request(
                model=model,
                input_length=int(input_length),
                output_length=output_length
            )
            
            # Return response
            response = {
                "status": "accepted",
                "message": "Request added to processing queue",
                "estimated_input_tokens": int(input_length),
                "estimated_output_tokens": output_length,
                "model": model
            }
            
            self._send_json_response(200, response)
            
        except Exception as e:
            self._send_error(400, f"Invalid request: {str(e)}")
    
    def _handle_status(self):
        """Handle status requests"""
        try:
            status = self.request_api.get_status()
            self._send_json_response(200, status)
        except Exception as e:
            self._send_error(500, f"Status error: {str(e)}")
    
    def _handle_health(self):
        """Handle health check requests"""
        response = {
            "status": "healthy",
            "service": "LLMServingSim",
            "timestamp": time.time()
        }
        self._send_json_response(200, response)
    
    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """Send error response"""
        error_response = {
            "error": message,
            "status_code": status_code
        }
        self._send_json_response(status_code, error_response)
    
    def log_message(self, format, *args):
        """Override to use proper logging"""
        logging.info(f"{self.address_string()} - {format % args}")


class LLMServingServer:
    """HTTP Server for LLM Serving Simulation"""
    
    def __init__(self, request_api, host='localhost', port=8000):
        self.request_api = request_api
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the HTTP server"""
        try:
            # Create handler with request_api
            def handler(*args, **kwargs):
                return LLMServingHandler(self.request_api, *args, **kwargs)
            
            self.server = HTTPServer((self.host, self.port), handler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.logger.info(f"LLMServingSim HTTP server started on {self.host}:{self.port}")
            self.logger.info(f"🚀 OpenAI-compatible API endpoints:")
            self.logger.info(f"  POST http://{self.host}:{self.port}/v1/chat/completions - Chat completions (OpenAI compatible)")
            self.logger.info(f"  POST http://{self.host}:{self.port}/v1/completions      - Text completions (OpenAI compatible)")
            self.logger.info(f"  GET  http://{self.host}:{self.port}/v1/models           - List available models")
            self.logger.info(f"📊 Service endpoints:")
            self.logger.info(f"  GET  http://{self.host}:{self.port}/health              - Health check")
            self.logger.info(f"  GET  http://{self.host}:{self.port}/status              - Service status")
            self.logger.info(f"🔧 Legacy endpoints:")
            self.logger.info(f"  POST http://{self.host}:{self.port}/generate            - Custom generation endpoint")
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.logger.info("HTTP server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self.server is not None and self.server_thread.is_alive()


# Example usage and testing
if __name__ == "__main__":
    # This is just for testing the server module
    print("LLMServingSim HTTP Server module")
    print("This module should be imported and used with a RequestAPI instance")
