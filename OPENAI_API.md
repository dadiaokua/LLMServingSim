# LLMServingSim OpenAI兼容API使用指南

## 概述

LLMServingSim现在支持**OpenAI兼容的API接口**，可以作为OpenAI API的替代品进行性能仿真和测试。

### ✨ 主要特性

- 🔌 **完全兼容OpenAI API格式**：支持chat/completions和completions端点
- 📊 **性能仿真**：基于真实硬件性能数据进行延迟和吞吐量仿真
- 🚀 **零配置启动**：一键启动OpenAI兼容服务
- 📈 **实时监控**：提供详细的服务状态和性能指标
- 🔧 **灵活配置**：支持多种硬件和模型配置

## 快速开始

### 1. 启动OpenAI兼容服务器

```bash
# 使用默认配置启动（端口8000）
./run_openai_server.sh

# 自定义端口和主机
./run_openai_server.sh --port 8080 --host 0.0.0.0

# 查看所有选项
./run_openai_server.sh --help
```

### 2. 测试API连接

```bash
# 运行自动化测试
python test_openai_api.py

# 或指定服务器地址
python test_openai_api.py http://localhost:8080
```

## API端点

### 🚀 OpenAI兼容端点

| 端点 | 方法 | 描述 | OpenAI兼容性 |
|------|------|------|-------------|
| `/v1/chat/completions` | POST | 聊天补全 | ✅ 完全兼容 |
| `/v1/completions` | POST | 文本补全 | ✅ 完全兼容 |
| `/v1/models` | GET | 列出可用模型 | ✅ 完全兼容 |

### 📊 服务端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/status` | GET | 详细服务状态 |

## 使用示例

### 1. 使用curl测试

#### Chat Completions
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "max_tokens": 150
  }'
```

#### Text Completions
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "prompt": "The future of AI is",
    "max_tokens": 100
  }'
```

#### 列出模型
```bash
curl http://localhost:8000/v1/models
```

### 2. 使用OpenAI Python客户端

```python
from openai import OpenAI

# 创建客户端，指向本地服务器
client = OpenAI(
    api_key="dummy-key",  # LLMServingSim不需要真实API密钥
    base_url="http://localhost:8000/v1"
)

# Chat Completions
response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing."}
    ],
    max_tokens=200
)

print(response.choices[0].message.content)
print(f"Usage: {response.usage}")
```

### 3. 使用其他OpenAI兼容库

任何支持自定义base_url的OpenAI客户端都可以使用：

```python
# LangChain
from langchain.llms import OpenAI
llm = OpenAI(openai_api_base="http://localhost:8000/v1")

# LlamaIndex  
from llama_index.llms import OpenAI
llm = OpenAI(api_base="http://localhost:8000/v1")
```

## 响应格式

### Chat Completions响应
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699896916,
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[LLMServingSim] Request queued for processing..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 150,
    "total_tokens": 170
  }
}
```

### Models响应
```json
{
  "object": "list",
  "data": [
    {
      "id": "meta-llama/Llama-3.1-8B-Instruct",
      "object": "model",
      "created": 1699896916,
      "owned_by": "llmservingsim"
    }
  ]
}
```

## 配置选项

### 启动参数

```bash
python main.py \
    --idle_mode \                    # 启用空闲模式（只监听，不生成流量）
    --http_host localhost \          # HTTP服务器主机
    --http_port 8000 \              # HTTP服务器端口
    --model_name meta-llama/Llama-3.1-8B-Instruct \  # 模型名称
    --hardware RTX3090 \            # 硬件类型
    --npu_num 1 \                   # NPU数量
    --npu_mem 40 \                  # NPU内存(GB)
    --verbose                       # 详细日志
```

### 环境变量支持

```bash
export LLMSERVINGSIM_HOST=0.0.0.0
export LLMSERVINGSIM_PORT=8000
export LLMSERVINGSIM_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

## 性能监控

### 实时状态查询

```bash
curl http://localhost:8000/status
```

响应示例：
```json
{
  "pending_requests": 5,
  "inflight_batches": 2,
  "completed_requests": 100,
  "memory_usage": {
    "total": 42949672960,
    "used": 2147483648,
    "available": 40802189312
  }
}
```

### 日志监控

服务器会输出详细的请求处理日志：
```
2024-01-15 10:30:15 - INFO - 127.0.0.1 - POST /v1/chat/completions
Scheduler: added request to LLMServingSim
Added request: input_len=25, output_len=175
[0.500s] Service is idle, waiting for requests...
```

## 集成示例

### 1. 替换OpenAI API

```python
# 原来的代码
import openai
openai.api_key = "sk-..."
openai.api_base = "https://api.openai.com/v1"

# 替换为LLMServingSim
import openai
openai.api_key = "dummy"
openai.api_base = "http://localhost:8000/v1"
```

### 2. 性能测试脚本

```python
import time
import requests
import concurrent.futures

def send_request():
    response = requests.post("http://localhost:8000/v1/chat/completions", 
        json={
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100
        })
    return response.status_code == 200

# 并发测试
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(send_request) for _ in range(100)]
    results = [f.result() for f in futures]
    
print(f"Success rate: {sum(results)/len(results)*100:.1f}%")
```

## 故障排除

### 常见问题

**Q: 服务器启动失败**
```bash
# 检查端口是否被占用
lsof -i :8000

# 使用不同端口
./run_openai_server.sh --port 8080
```

**Q: API响应格式不正确**
```bash
# 检查Content-Type头
curl -H "Content-Type: application/json" ...
```

**Q: 请求被拒绝**
```bash
# 检查服务器日志
python main.py --idle_mode --verbose
```

### 调试模式

```bash
# 启用详细日志
python main.py --idle_mode --verbose --http_port 8000

# 检查服务状态
curl http://localhost:8000/health
curl http://localhost:8000/status
```

## 限制和注意事项

### 当前限制

1. **仿真响应**：返回的是仿真响应，不是真实的文本生成
2. **单模型支持**：目前只支持配置的单个模型
3. **无流式响应**：暂不支持真正的流式响应
4. **基础认证**：不需要真实的API密钥验证

### 性能考虑

- 适用于性能测试和架构验证
- 不适用于生产环境的实际文本生成
- 响应延迟基于硬件性能模型预测

## 扩展开发

### 添加新端点

```python
# 在http_server.py中添加
def _handle_custom_endpoint(self):
    # 自定义处理逻辑
    pass
```

### 自定义响应格式

```python
def _send_custom_response(self, data):
    # 自定义响应格式
    response = {"custom": data}
    self._send_json_response(200, response)
```

---

🎉 现在你可以将LLMServingSim作为OpenAI API的完全兼容替代品使用了！
