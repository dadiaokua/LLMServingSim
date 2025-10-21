#!/bin/bash

# 简化版服务器启动脚本 - 绕过 ASTRA-Sim 构建问题
# 只启动 HTTP 服务器，不进行实际的硬件仿真

echo "🚀 Starting LLMServingSim HTTP Server (Simplified Mode)"
echo "⚠️  Note: This is a simplified mode that bypasses ASTRA-Sim simulation"
echo "   It provides OpenAI-compatible API endpoints for testing purposes"
echo ""

# 默认配置
MODEL_NAME="qwen/Qwen3-8B"
HARDWARE="V100"
NPU_NUM=1
NPU_GROUP=1
NPU_MEM=32
HTTP_HOST="localhost"
HTTP_PORT=8000

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            HTTP_PORT="$2"
            shift 2
            ;;
        --host)
            HTTP_HOST="$2"
            shift 2
            ;;
        --model)
            MODEL_NAME="$2"
            shift 2
            ;;
        --npu_num)
            NPU_NUM="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT     HTTP server port (default: 8000)"
            echo "  --host HOST     HTTP server host (default: localhost)"
            echo "  --model MODEL   Model name (default: qwen/Qwen3-8B)"
            echo "  --npu_num NUM   Number of NPUs (default: 1)"
            echo "  --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Start with default settings"
            echo "  $0 --port 8080             # Start on port 8080"
            echo "  $0 --host 0.0.0.0 --port 8000  # Listen on all interfaces"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "Configuration:"
echo "  Model: $MODEL_NAME"
echo "  Hardware: $HARDWARE"
echo "  NPUs: $NPU_NUM"
echo "  Server: http://$HTTP_HOST:$HTTP_PORT"
echo ""

# 检查模型配置是否存在
echo "🔍 Checking model configuration..."
python3 -c "
import sys
sys.path.append('.')
from inference_serving.utils import get_config
config = get_config('$MODEL_NAME')
if config:
    print(f'✅ Model config loaded: {config.get(\"model_type\", \"unknown\")}')
else:
    print('❌ Model config not found')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Model configuration check failed"
    exit 1
fi

echo ""
echo "🌐 Starting HTTP server only (simulation bypassed)..."

# 创建一个简化的 Python 脚本来启动 HTTP 服务器
cat > /tmp/simple_server.py << 'EOF'
import sys
import os
import time
import argparse
from http.server import HTTPServer
import logging

# 添加项目路径
sys.path.append('.')

try:
    from inference_serving.http_server import LLMServingHandler
    from inference_serving.request_api import RequestAPI
    from inference_serving.scheduler import Scheduler
    from inference_serving.utils import get_config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)

def create_mock_scheduler(model_name, npu_num, npu_mem):
    """创建一个模拟的调度器，不依赖 ASTRA-Sim"""
    
    class MockMemoryModel:
        def __init__(self, model_name, npu_num, npu_mem):
            self.config = get_config(model_name)
            if not self.config:
                raise ValueError(f"Cannot load config for model: {model_name}")
            
            self.npu_num = npu_num
            self.npu_mem = npu_mem * 1024  # Convert GB to MB
            
            # 计算模型权重大小 (简化计算)
            hidden_size = self.config.get('hidden_size', 4096)
            num_layers = self.config.get('num_hidden_layers', 32)
            vocab_size = self.config.get('vocab_size', 50000)
            
            # 简化的权重计算 (实际会更复杂)
            param_count = (
                vocab_size * hidden_size +  # embedding
                num_layers * hidden_size * hidden_size * 4 +  # transformer layers
                vocab_size * hidden_size  # output layer
            )
            
            # 假设 FP16，每个参数 2 字节
            self.model_weight_mb = (param_count * 2) // (1024 * 1024)
            self.used_mem = self.model_weight_mb
            
            print(f"Memory: model weight {self.model_weight_mb}MB loaded")
    
    class MockScheduler:
        def __init__(self, model_name, npu_num, npu_mem):
            self.model = model_name
            self.memory = MockMemoryModel(model_name, npu_num, npu_mem)
            self.request = []
            self.inflight = []
            self.done = []
            
        def add_request(self, request_data):
            """添加请求到队列"""
            self.request.append(request_data)
            print(f"Added request: {request_data}")
            
        def is_request_empty(self):
            return len(self.request) == 0 and len(self.inflight) == 0
    
    return MockScheduler(model_name, npu_num, npu_mem)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', default='qwen/Qwen3-8B')
    parser.add_argument('--npu_num', type=int, default=1)
    parser.add_argument('--npu_mem', type=int, default=32)
    parser.add_argument('--http_host', default='localhost')
    parser.add_argument('--http_port', type=int, default=8000)
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # 创建模拟调度器
        scheduler = create_mock_scheduler(args.model_name, args.npu_num, args.npu_mem)
        
        # 创建请求 API
        request_api = RequestAPI(scheduler)
        
        # 创建 HTTP 服务器
        class MockLLMServingHandler(LLMServingHandler):
            def __init__(self, *args, **kwargs):
                self.request_api = request_api
                super().__init__(*args, **kwargs)
        
        server = HTTPServer((args.http_host, args.http_port), MockLLMServingHandler)
        
        # 启动服务器
        logging.info(f"🚀 LLMServingSim HTTP server started on {args.http_host}:{args.http_port}")
        logging.info("🚀 OpenAI-compatible API endpoints:")
        logging.info(f"  POST http://{args.http_host}:{args.http_port}/v1/chat/completions - Chat completions (OpenAI compatible)")
        logging.info(f"  POST http://{args.http_host}:{args.http_port}/v1/completions      - Text completions (OpenAI compatible)")
        logging.info(f"  GET  http://{args.http_host}:{args.http_port}/v1/models           - List available models")
        logging.info("📊 Service endpoints:")
        logging.info(f"  GET  http://{args.http_host}:{args.http_port}/health              - Health check")
        logging.info(f"  GET  http://{args.http_host}:{args.http_port}/status              - Service status")
        logging.info("🔧 Legacy endpoints:")
        logging.info(f"  POST http://{args.http_host}:{args.http_port}/generate            - Custom generation endpoint")
        
        print("Starting LLMServingSim in simplified mode - HTTP API only")
        print("Service is ready to accept requests...")
        print("⚠️  Note: Responses will be mock responses for testing purposes")
        print("")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# 运行简化服务器
python3 /tmp/simple_server.py \
    --model_name "$MODEL_NAME" \
    --npu_num $NPU_NUM \
    --npu_mem $NPU_MEM \
    --http_host "$HTTP_HOST" \
    --http_port $HTTP_PORT

echo ""
echo "Server has been stopped."
