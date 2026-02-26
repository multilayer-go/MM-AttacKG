# MM-AttacKG

**基于多模态大语言模型的网络威胁情报攻击知识图谱自动构建**

[English README](README.md)

---

## 项目简介

MM-AttacKG 是一个多模态流水线系统，能够从网络威胁情报（CTI）报告中自动构建攻击知识图谱。该系统利用具备文本和视觉能力的大语言模型（LLM），从包含文本和图像（如截图、拓扑图、流程图等）的CTI报告中提取结构化的安全实体、关系以及 MITRE ATT&CK 技术映射。

### 核心特性

- **多模态分析**：同时处理CTI报告中的图像（截图、网络拓扑图、反编译代码等）和文本内容
- **6步流水线**：通过问题生成、答案生成、主题判断、答案评分、迭代优化和最终提取，系统化地实现信息抽取
- **MITRE ATT&CK 映射**：自动将提取的攻击行为映射到 MITRE ATT&CK 战术和技术
- **国产大模型架构**：全面基于阿里云通义千问（DashScope）系列模型，用于主要分析和独立答案评估。系统提供了可扩展的评估接口以支持第三方LLM，但由于服务访问限制，实际仅使用国产模型。
- **稳健执行**：内置重试逻辑、超时处理和指数退避机制，确保API交互的可靠性

---

## 系统架构

```
CTI 报告（图像 + 文本）
        │
        ▼
┌─────────────────────────────────────────────┐
│  Step 1: 问题生成 (Question Generation)      │  为每张图像生成结构化问题
│  Step 2: 答案生成 (Answer Generation)        │  使用多模态LLM回答问题
│  Step 3: 主题判断 (Theme Judging)            │  判断问答对与安全主题的相关性
│  Step 4: 答案评分 (Answer Marking)           │  使用通义千问独立评估答案质量
│  Step 5: 迭代优化 (Iterative Refinement)     │  对低分答案进行改进
│  Step 6: 答案提取 (Answer Extraction)        │  提取最终结构化实体
└─────────────────────────────────────────────┘
        │
        ▼
  攻击知识图谱（JSON）
```

---

## 快速开始

### 1. 环境要求

- Python 3.8+
- DashScope API 密钥（用于通义千问模型）
- DashScope API 密钥（用于通义千问评估模型）

### 2. 安装

```bash
git clone https://github.com/yourusername/MM-AttacKG.git
cd MM-AttacKG
pip install -r requirements.txt
```

### 3. 配置

设置以下环境变量（或创建 `.env` 文件）：

```bash
# 必需：DashScope（通义千问）API
export DASHSCOPE_API_KEY="你的DashScope API密钥"
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 可选
export TEXT_MODEL="qwen2.5-72b-instruct"    # 可选，默认值
export VISION_MODEL="qwen2.5-vl-72b-instruct"  # 可选，默认值

# 可选：评估模型配置（用于Step 4答案评分）
# 默认使用与上方相同的 DashScope API
# export EVAL_API_KEY="你的DashScope API密钥"    # 默认使用 DASHSCOPE_API_KEY
# export EVAL_API_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
# export EVAL_MODEL="qwen2.5-72b-instruct"
```

或者复制并编辑示例配置文件：

```bash
cp config/config.example.yaml config/config.yaml
# 编辑 config.yaml 填入你的 API 密钥
```

### 4. 准备数据

将CTI报告数据放置在 `data/cti_reports/<ID>/` 目录下：

```
data/cti_reports/00/
├── original/
│   ├── KG.json          # 真值知识图谱（用于评估）
│   ├── outline.json     # 报告大纲 / 结构化文本
│   └── In-context.json  # 上下文学习示例
├── picture/             # 报告图像（截图、拓扑图等）
│   ├── image1.png
│   ├── image2.png
│   └── ...
└── process/             # 流水线输出（自动生成）
```

### 5. 运行

```bash
# 处理单个CTI报告
python run.py single --cti-id 00

# 仅运行特定的流水线步骤
python run.py single --cti-id 00 --steps 1-3

# 批量处理所有CTI报告
python run.py batch

# 批量处理指定的报告
python run.py batch --cti-ids 00 01 02
```

---

## 流水线步骤

| 步骤 | 名称 | 说明 | 使用模型 |
|------|------|------|----------|
| 1 | 问题生成 | 基于报告大纲和MITRE框架，为每张图像生成结构化问题 | Qwen（文本） |
| 2 | 答案生成 | 使用多模态LLM结合图像和文本上下文回答问题 | Qwen（视觉） |
| 3 | 主题判断 | 将每个问答对分类到预定义的安全主题 | Qwen（视觉） |
| 4 | 答案评分 | 使用独立LLM评估答案质量 | Qwen（文本） |
| 5 | 迭代优化 | 对低分项重新生成答案并附带改进建议 | Qwen（视觉） |
| 6 | 答案提取 | 从优化后的答案中提取最终结构化实体和攻击知识 | Qwen（文本） |

---

## 图像类别

流水线可识别和处理CTI报告中常见的6种图像类型：

| 类别 | 说明 |
|------|------|
| `code_screenshot` | 代码、脚本或命令行输出的截图 |
| `network_diagram` | 网络拓扑图和通信流程图 |
| `decompiled_code` | 恶意软件分析中的反编译或反汇编代码 |
| `attack_flow` | 攻击流程图和杀伤链图 |
| `system_screenshot` | 系统界面截图、配置面板 |
| `data_table` | 表格、图表和统计数据可视化 |

---

## 项目结构

```
MM-AttacKG/
├── run.py                          # 主命令行入口
├── config/
│   └── config.example.yaml         # 配置文件示例
├── data/
│   ├── cti_reports/                # CTI报告数据
│   │   ├── 00/ ... 11/            # 各报告文件夹
│   └── resources/                  # 共享资源
│       ├── entity_types.json       # 实体类型定义
│       ├── mitre_framework.json    # MITRE ATT&CK 框架
│       └── mitre_tactics_techniques.json
├── src/
│   ├── pipeline/                   # 6步流水线模块
│   │   ├── step1_question_generation.py
│   │   ├── step2_answer_generation.py
│   │   ├── step3_theme_judging.py
│   │   ├── step4_marking.py
│   │   ├── step5_iteration_form1.py
│   │   ├── step5_iteration_form2.py
│   │   └── step6_extraction.py
│   ├── utils/                      # 工具模块
│   │   ├── api_connector.py        # LLM API 接口
│   │   ├── config_loader.py        # 配置加载器
│   │   └── logger.py               # 日志工具
│   ├── run_single_cti.py           # 单CTI处理器
│   └── run_all_cti.py              # 批处理器
├── docs/                           # 文档
├── requirements.txt
├── setup.py
└── LICENSE
```

---

## 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DASHSCOPE_API_KEY` | 是 | — | DashScope API 密钥（通义千问） |
| `DASHSCOPE_BASE_URL` | 否 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | DashScope API 基础 URL |
| `TEXT_MODEL` | 否 | `qwen2.5-72b-instruct` | 文本 LLM 模型名称 |
| `VISION_MODEL` | 否 | `qwen2.5-vl-72b-instruct` | 视觉 LLM 模型名称 |
| `EVAL_API_KEY` | 否 | 与 `DASHSCOPE_API_KEY` 相同 | 用于 Step 4 评估模型的 API 密钥 |
| `EVAL_API_URL` | 否 | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` | 评估 API 端点 |
| `EVAL_MODEL` | 否 | `qwen2.5-72b-instruct` | 评估模型名称 |

---

## 输出格式

流水线为每个步骤生成一个 JSON 文件。最终输出（`JSONstep6_answerRes.json`）包含结构化的攻击知识：

```json
[
  {
    "image": "image1.png",
    "category": "network_diagram",
    "entities": [
      {
        "entity": "C2 Server",
        "type": "infrastructure",
        "attributes": { ... }
      }
    ],
    "tactics": ["Command and Control"],
    "techniques": ["T1071 - Application Layer Protocol"]
  }
]
```

---

## 许可证

本项目采用 MIT 许可证 — 详见 [LICENSE](LICENSE) 文件。

---

## 致谢

- [MITRE ATT&CK](https://attack.mitre.org/) 威胁情报框架
- [阿里云 DashScope](https://dashscope.aliyun.com/) 通义千问模型 API
