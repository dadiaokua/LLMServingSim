#!/bin/bash

# 启动LLMServingSim在空闲模式
# 这将启动服务但不生成任何请求

echo "Starting LLMServingSim in idle mode..."
echo "The service will start and wait for requests without generating any traffic."
echo ""

python main.py \
    --model_name 'meta-llama/Llama-3.1-8B-Instruct' \
    --hardware 'RTX3090' \
    --npu_num 1 \
    --npu_group 1 \
    --npu_mem 40 \
    --remote_bw 512 \
    --link_bw 256 \
    --fp 16 \
    --block_size 4 \
    --idle_mode \
    --verbose

echo "Service has been stopped."
