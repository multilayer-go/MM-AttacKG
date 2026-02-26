# 🚀 快速开始指南

## 📋 前置要求

### 1. 环境配置
```bash
# Python 3.8+
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. API密钥配置
```bash
# 方式1: 使用配置文件
cp config/config.example.yaml config/config.yaml
# 编辑 config/config.yaml，填入你的API密钥

# 方式2: 使用环境变量
cp .env.example .env
# 编辑 .env 文件
```

**需要的API密钥：**
- **DASHSCOPE_API_KEY** - 阿里云灵积（用于Qwen多模态模型及答案评估）

---

## 🎯 使用场景

### 场景1: 处理单个CTI报告
```bash
# 处理CTI报告 00（完整6步流程）
python run.py single --cti-id 00

# 只运行前3步（问题生成、答案生成、主题判断）
python run.py single --cti-id 00 --steps 1-3

# 运行特定步骤范围
python run.py single --cti-id 05 --steps 4-6
```

**输出位置：** `data/cti_reports/00/process/JSONstep6_answerRes.json`

---

### 场景2: 批量处理多个CTI报告
```bash
# 处理所有CTI报告（00-11）
python run.py batch

# 只处理指定的几个CTI
python run.py batch --cti-ids 00 01 02

# 批量处理（只运行步骤1-5）
python run.py batch --steps 1-5
```

---

## 📂 数据目录结构

```
data/cti_reports/
├── 00/                          # CTI报告00
│   ├── original/                # 原始数据
│   │   ├── KG.json             # 知识图谱标注
│   │   ├── In-context.json     # 上下文示例
│   │   └── outline.json        # 大纲信息
│   ├── picture/                 # 图片文件
│   │   ├── 001.png
│   │   ├── 002.png
│   │   └── ...
│   └── process/                 # 处理结果
│       ├── JSONstep1_Questions.json
│       ├── JSONstep2_Answers.json
│       ├── JSONstep3_QLabels.json
│       ├── JSONstep4_Mark.json
│       ├── JSONstep5_Iteration_Form2.json
│       └── JSONstep6_answerRes.json  # 最终结果
├── 01/
├── 02/
└── ...
```

---

## 🔍 流水线步骤说明

### Step 1: 问题生成
- **功能**: 对图片进行分类并生成相关问题
- **输入**: `data/cti_reports/{id}/picture/`
- **输出**: `JSONstep1_Questions.json`

### Step 2: 答案生成
- **功能**: 使用多模态LLM回答问题
- **输入**: `JSONstep1_Questions.json`
- **输出**: `JSONstep2_Answers.json`

### Step 3: 主题判断
- **功能**: 判断问答是否与网络安全相关
- **输入**: `JSONstep2_Answers.json`
- **输出**: `JSONstep3_QLabels.json`

### Step 4: 答案评分
- **功能**: 使用通义千问对答案质量进行评分
- **输入**: `JSONstep3_QLabels.json`
- **输出**: `JSONstep4_Mark.json`

### Step 5: 迭代优化
- **功能**: 根据评分迭代改进答案
- **输入**: `JSONstep4_Mark.json`
- **输出**: `JSONstep5_Iteration_Form2.json`

### Step 6: 答案提取
- **功能**: 从答案中提取结构化信息构建知识图谱
- **输入**: `JSONstep5_Iteration_Form2.json` + `KG.json`
- **输出**: `JSONstep6_answerRes.json`

---

## ⚙️ 高级用法

### 自定义配置
```bash
# 编辑配置文件
vim config/config.yaml

# 配置项包括：
# - API密钥
# - 模型参数
# - 重试次数
# - 线程/进程数
# - 日志级别
```

### 查看日志
```bash
# 日志文件位置
logs/mm_attackg.log

# 实时查看日志
tail -f logs/mm_attackg.log
```

### 使用Python模块
```python
from src.pipeline.step1_question_generation import process_all_images_in_folder
from src.pipeline.step2_answer_generation import process_answers_from_questions

# 自定义处理流程
picture_folder = "data/cti_reports/00/picture"
output_file = "data/cti_reports/00/process/questions.json"

process_all_images_in_folder(picture_folder, output_file)
```

---

## ❓ 常见问题

### Q1: 没有API密钥怎么办？
**A:** 你需要：
- 阿里云账号 → 开通灵积服务 → 获取DASHSCOPE_API_KEY

### Q2: 处理速度很慢？
**A:** 可以调整配置：
```yaml
# config/config.yaml
processing:
  max_workers: 8        # 增加并发数
  batch_size: 10        # 增加批处理大小
```

### Q3: 某一步失败了怎么办？
**A:** 可以从失败的步骤重新开始：
```bash
# 假设步骤3失败，从步骤3重新运行
python run.py single --cti-id 00 --steps 3-6
```

### Q4: 如何验证结果正确性？
**A:** 查看最终输出文件并对比知识图谱：
```bash
# 查看最终结果
cat data/cti_reports/00/process/JSONstep6_answerRes.json

# 对比原始标注
cat data/cti_reports/00/original/KG.json
```

---

## 📞 获取帮助

```bash
# 查看主程序帮助
python run.py --help
python run.py single --help
python run.py batch --help
```

---

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [docs/PIPELINE.md](docs/PIPELINE.md) - 流水线详细说明
- [docs/EXAMPLES.md](docs/EXAMPLES.md) - 更多使用示例

---

## ⚡ 快速验证

运行以下命令快速验证系统是否正常：

```bash
# 1. 检查依赖
pip install -r requirements.txt

# 2. 配置API密钥（编辑文件）
cp config/config.example.yaml config/config.yaml

# 3. 测试单个CTI（只运行步骤1）
python run.py single --cti-id 00 --steps 1-1

# 4. 如果步骤1成功，运行完整流程
python run.py single --cti-id 00
```

---

**祝你使用愉快！🎉**
