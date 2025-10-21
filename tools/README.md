# LLMServingSim 工具目录

这个目录包含了LLMServingSim的各种工具和脚本，按功能分类组织。

## 📁 目录结构

```
tools/
├── scripts/           # 启动和运行脚本
├── perf_models/       # 性能模型生成工具
├── tests/            # 测试工具
└── README.md         # 本文档
```

## 🚀 scripts/ - 启动脚本

### `run_openai_server.sh`
启动OpenAI兼容的API服务器

```bash
# 使用方法
tools/scripts/run_openai_server.sh [选项]

# 选项
--port PORT         HTTP服务器端口 (默认: 8000)
--host HOST         HTTP服务器主机 (默认: localhost)  
--model MODEL       模型名称
--npu_num NUM       NPU数量 (默认: 1)

# 示例
tools/scripts/run_openai_server.sh --port 8080 --model "qwen/Qwen3-8B" --hardware A100
```

### `run_idle.sh`
启动空闲模式服务器（只监听，不生成流量）

```bash
tools/scripts/run_idle.sh
```

### `demo_curl_response.sh`
显示curl使用示例和预期响应格式

```bash
tools/scripts/demo_curl_response.sh
```

## 🔧 perf_models/ - 性能模型工具

### `generate_perf_models.py`
为多种硬件生成性能模型文件

```bash
# 生成所有硬件的性能模型
python3 tools/perf_models/generate_perf_models.py

# 生成的硬件类型
- H100 (3.5x faster than RTX3090)
- A100 (2.2x faster)
- L40, RTX4090, A6000, A40, RTX4080, RTX3090, A10, V100, T4
```

### `extend_perf_models.py`
为现有硬件添加新模型支持

```bash
# 为所有硬件添加新模型支持
python3 tools/perf_models/extend_perf_models.py

# 支持的模型
- qwen/Qwen3-8B
- meta-llama/Llama-3.1-8B-Instruct  
- facebook/opt-6.7b
```

## 🧪 tests/ - 测试工具

### `test_openai_api.py`
测试OpenAI兼容API的所有端点

```bash
# 测试默认服务器 (localhost:8000)
python3 tools/tests/test_openai_api.py

# 测试指定服务器
python3 tools/tests/test_openai_api.py http://localhost:8080

# 测试内容
- /v1/models 端点
- /v1/chat/completions 端点
- /v1/completions 端点
- OpenAI Python客户端兼容性
```

### `test_http_api.py`
测试基础HTTP接口

```bash
python3 tools/tests/test_http_api.py [服务器地址]

# 测试内容
- 健康检查
- 服务状态
- 基础生成接口
```

## 🎯 使用统一启动器

推荐使用项目根目录的 `llmservingsim` 脚本作为统一入口：

```bash
# 启动服务器
./llmservingsim server --model "qwen/Qwen3-8B" --hardware A100

# 生成性能模型
./llmservingsim setup-perf

# 测试API
./llmservingsim test-api

# 查看帮助
./llmservingsim help
```

## 📊 工具依赖关系

```
generate_perf_models.py  →  创建基础性能模型
         ↓
extend_perf_models.py    →  添加更多模型支持
         ↓
run_openai_server.sh     →  启动服务器
         ↓
test_openai_api.py       →  测试服务器功能
```

## 🔄 工作流程

1. **初始设置**
   ```bash
   ./llmservingsim setup-perf      # 生成性能模型
   ./llmservingsim extend-models   # 添加模型支持
   ```

2. **启动服务**
   ```bash
   ./llmservingsim server --model "qwen/Qwen3-8B" --hardware A100
   ```

3. **测试验证**
   ```bash
   ./llmservingsim test-api
   ```

## 📝 添加新工具

如果需要添加新的工具脚本：

1. **确定分类**：scripts/, perf_models/, 或 tests/
2. **添加到对应目录**
3. **更新 `llmservingsim` 主脚本**
4. **更新此README文档**

## 🛠️ 维护说明

- 所有脚本都应该是可执行的 (`chmod +x`)
- Python脚本应该有 `#!/usr/bin/env python3` shebang
- Shell脚本应该有 `#!/bin/bash` shebang
- 所有工具都应该有帮助信息 (`--help`)
