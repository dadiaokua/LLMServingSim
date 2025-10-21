# LLMServingSim 项目结构

## 📁 整理后的项目结构

```
LLMServingSim/
├── 🚀 llmservingsim              # 主启动脚本（统一入口）
├── 📄 main.py                    # 核心仿真程序
├── 📄 run.sh                     # 原始启动脚本
│
├── 📂 inference_serving/         # 核心推理服务模块
│   ├── scheduler.py              # 请求调度器
│   ├── request.py                # 请求和批次管理
│   ├── memory_model.py           # 内存模型
│   ├── http_server.py            # OpenAI兼容HTTP服务器
│   ├── request_api.py            # 请求API接口
│   ├── control.py                # 仿真控制器
│   ├── generate_trace.py         # 执行轨迹生成
│   ├── generate_graph.py         # 执行图生成
│   ├── config_generator.py       # 配置生成器
│   ├── utils.py                  # 工具函数
│   └── pim.py                    # PIM相关功能
│
├── 📂 tools/                     # 🆕 工具目录（新整理）
│   ├── 📂 scripts/               # 启动和运行脚本
│   │   ├── run_openai_server.sh  # OpenAI服务器启动脚本
│   │   ├── run_idle.sh           # 空闲模式启动脚本
│   │   └── demo_curl_response.sh # curl示例脚本
│   │
│   ├── 📂 perf_models/           # 性能模型工具
│   │   ├── generate_perf_models.py  # 生成硬件性能模型
│   │   └── extend_perf_models.py    # 扩展模型支持
│   │
│   ├── 📂 tests/                 # 测试工具
│   │   ├── test_openai_api.py    # OpenAI API测试
│   │   └── test_http_api.py      # HTTP接口测试
│   │
│   └── 📄 README.md              # 工具目录说明
│
├── 📂 model_configs/             # 模型配置文件
│   ├── meta-llama/
│   │   └── Llama-3.1-8B-Instruct.json
│   ├── facebook/
│   │   └── opt-6.7b.json
│   └── qwen/
│       └── Qwen3-8B.json
│
├── 📂 perf_model/                # 性能模型数据（🆕 扩展支持）
│   ├── RTX3090.csv               # 原始基准数据
│   ├── A100.csv                  # 🆕 A100性能数据
│   ├── H100.csv                  # 🆕 H100性能数据
│   ├── V100.csv                  # 🆕 V100性能数据
│   ├── RTX4090.csv               # 🆕 RTX4090性能数据
│   ├── A6000.csv                 # 🆕 A6000性能数据
│   ├── A40.csv                   # 🆕 A40性能数据
│   ├── RTX4080.csv               # 🆕 RTX4080性能数据
│   ├── L40.csv                   # 🆕 L40性能数据
│   ├── A10.csv                   # 🆕 A10性能数据
│   └── T4.csv                    # 🆕 T4性能数据
│
├── 📂 astra-sim/                 # ASTRA-Sim仿真器
├── 📂 dataset/                   # 数据集文件
├── 📂 examples/                  # 示例配置
├── 📂 output/                    # 输出结果
├── 📂 llm-profile/               # 性能分析工具
├── 📂 trace_test/                # 轨迹测试
│
├── 📄 PROJECT_STRUCTURE.md       # 🆕 项目结构说明（本文档）
├── 📄 API_SUMMARY.md             # 🆕 API功能总结
├── 📄 OPENAI_API.md              # 🆕 OpenAI API使用指南
├── 📄 README.md                  # 项目主文档
├── 📄 LICENSE                    # 许可证
├── 📄 requirements.txt           # Python依赖
└── 📄 environment.yml            # Conda环境配置
```

## 🎯 主要改进

### ✅ **文件整理**
- 将所有工具脚本移动到 `tools/` 目录
- 按功能分类：scripts, perf_models, tests
- 创建统一的 `llmservingsim` 启动器

### ✅ **性能模型扩展**
- 支持11种硬件类型
- 支持3种模型架构
- 总计33种配置组合

### ✅ **OpenAI兼容性**
- 完整的OpenAI API支持
- 兼容现有OpenAI客户端
- 支持chat/completions和completions端点

## 🚀 使用方式

### **统一启动器（推荐）**
```bash
# 查看所有可用命令
./llmservingsim help

# 启动OpenAI服务器
./llmservingsim server --model "qwen/Qwen3-8B" --hardware A100

# 生成性能模型
./llmservingsim setup-perf

# 测试API
./llmservingsim test-api
```

### **直接调用工具**
```bash
# 启动服务器
tools/scripts/run_openai_server.sh --model "qwen/Qwen3-8B" --hardware A100

# 生成性能模型
python3 tools/perf_models/generate_perf_models.py

# 测试API
python3 tools/tests/test_openai_api.py
```

## 📊 支持矩阵

### **模型支持**
- ✅ qwen/Qwen3-8B
- ✅ meta-llama/Llama-3.1-8B-Instruct
- ✅ facebook/opt-6.7b

### **硬件支持**
- ✅ H100 (3.5x) - 最快
- ✅ A100 (2.2x) - 数据中心标准
- ✅ L40 (1.8x) - 专业级
- ✅ RTX4090 (1.6x) - 消费级旗舰
- ✅ A6000 (1.4x) - 专业级
- ✅ A40 (1.3x) - 数据中心
- ✅ RTX4080 (1.2x) - 消费级高端
- ✅ RTX3090 (1.0x) - 基准
- ✅ A10 (0.9x) - 专业级中端
- ✅ V100 (0.8x) - 数据中心经典
- ✅ T4 (0.4x) - 推理专用

## 🔄 工作流程

1. **初始化**: `./llmservingsim setup-perf`
2. **启动服务**: `./llmservingsim server`
3. **测试验证**: `./llmservingsim test-api`
4. **仿真分析**: `./llmservingsim simulate`

现在项目结构更加清晰和易于维护！🎉
