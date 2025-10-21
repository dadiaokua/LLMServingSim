#!/bin/bash

# 启动LLMServingSim作为OpenAI兼容的API服务器
# 只监听端口接收外部流量，不自己生成流量

echo "🚀 Starting LLMServingSim as OpenAI-compatible API server..."
echo "This will start the service and listen for OpenAI-compatible requests."
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
            echo "  --model MODEL   Model name (default: meta-llama/Llama-3.1-8B-Instruct)"
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

echo "Starting server..."
python main.py \
    --model_name "$MODEL_NAME" \
    --hardware "$HARDWARE" \
    --npu_num $NPU_NUM \
    --npu_group $NPU_GROUP \
    --npu_mem $NPU_MEM \
    --remote_bw 512 \
    --link_bw 256 \
    --fp 16 \
    --block_size 4 \
    --idle_mode \
    --http_host "$HTTP_HOST" \
    --http_port $HTTP_PORT \
    --verbose

echo ""
echo "Server has been stopped."
