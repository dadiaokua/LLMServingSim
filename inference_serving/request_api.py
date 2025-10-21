"""
Request API for dynamically adding requests to LLMServingSim
This module provides functionality to add requests to a running simulator instance.
"""

import json
import time
from .request import Request

class RequestAPI:
    """API for managing requests in LLMServingSim"""
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.request_queue = []
        
    def add_request(self, model, input_length, output_length, arrival_time=None):
        """
        Add a new request to the scheduler
        
        Args:
            model: Model name
            input_length: Input sequence length
            output_length: Output sequence length  
            arrival_time: Request arrival time (default: current time)
        """
        if arrival_time is None:
            arrival_time = int(time.time() * 1e9)  # Current time in nanoseconds
            
        self.scheduler.add_request([model, input_length, output_length, arrival_time])
        print(f"Added request: input_len={input_length}, output_len={output_length}")
        
    def add_batch_requests(self, requests):
        """
        Add multiple requests at once
        
        Args:
            requests: List of request dictionaries with keys: model, input_length, output_length, arrival_time
        """
        for req in requests:
            self.add_request(
                req.get('model'),
                req.get('input_length'),
                req.get('output_length'),
                req.get('arrival_time')
            )
            
    def get_status(self):
        """Get current status of the scheduler"""
        return {
            'pending_requests': len(self.scheduler.request),
            'inflight_batches': len(self.scheduler.inflight),
            'completed_requests': len(self.scheduler.done),
            'memory_usage': {
                'total': self.scheduler.memory.npu_mem,
                'used': self.scheduler.memory.used_mem,
                'available': self.scheduler.memory.npu_mem - self.scheduler.memory.used_mem
            }
        }
        
    def load_requests_from_file(self, filepath):
        """Load requests from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                requests = json.load(f)
            self.add_batch_requests(requests)
            print(f"Loaded {len(requests)} requests from {filepath}")
        except Exception as e:
            print(f"Error loading requests from {filepath}: {e}")
