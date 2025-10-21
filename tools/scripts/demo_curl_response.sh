#!/bin/bash

echo "🧪 LLMServingSim curl响应演示"
echo "================================"
echo ""

echo "📝 发送的请求："
echo "curl -X POST http://localhost:8000/v1/chat/completions \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"model\": \"meta-llama/Llama-3.1-8B-Instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}], \"max_tokens\": 100}'"
echo ""

echo "📤 预期的响应格式："
cat << 'EOF'
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion", 
  "created": 1703123456,
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[LLMServingSim] Request queued for processing. Input tokens: 2, Max output tokens: 100"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 2,
    "completion_tokens": 100,
    "total_tokens": 102
  }
}
EOF

echo ""
echo "🔍 关键说明："
echo "• content字段包含仿真响应，不是真实AI生成的文本"
echo "• usage字段显示token使用统计"
echo "• 请求会被添加到LLMServingSim的处理队列中"
echo "• ASTRA-Sim会进行性能仿真计算"
echo ""

echo "🚀 要实际测试，请先启动服务器："
echo "./run_openai_server.sh"
echo ""
echo "然后在另一个终端运行上面的curl命令"
