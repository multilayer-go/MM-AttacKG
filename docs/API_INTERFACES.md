# 🎯 MM-AttacKG 运行接口文档

## 📑 目录
1. [主运行接口 (run.py)](#主运行接口)
2. [使用示例](#使用示例)
3. [接口对比](#接口对比)

---

## 主运行接口

### 文件: `run.py`

**功能**: 提供统一的命令行接口来运行整个知识图谱构建流程

### 三种运行模式

#### 1️⃣ Single - 处理单个CTI报告
```bash
# 基本用法
python run.py single --cti-id 00

# 指定步骤范围
python run.py single --cti-id 00 --steps 1-3
```

#### 2️⃣ Batch - 批量处理CTI报告
```bash
# 处理所有CTI
python run.py batch

# 处理指定的CTI
python run.py batch --cti-ids 00 01 02

# 指定步骤范围
python run.py batch --cti-ids 00 01 --steps 1-5
```

### 核心类: Pipeline

```python
from run import Pipeline

# 创建流水线实例
pipeline = Pipeline(cti_id="00")

# 运行特定步骤
pipeline.step1_question_generation()
pipeline.step2_answer_generation()
# ... 其他步骤

# 或运行步骤范围
pipeline.run_steps(start_step=1, end_step=6)
```

---

## 使用示例

### 场景1: 新手入门 - 处理第一个CTI

```bash
# Step 1: 配置API密钥
cp config/config.example.yaml config/config.yaml
# 编辑 config/config.yaml，填入API密钥

# Step 2: 测试处理单个CTI
python run.py single --cti-id 00

# Step 3: 查看结果
cat data/cti_reports/00/process/JSONstep6_answerRes.json
```

### 场景2: 开发调试 - 测试某个步骤

```bash
# 只运行步骤1（问题生成）
python run.py single --cti-id 00 --steps 1-1

# 运行步骤1-3（问题生成、答案生成、主题判断）
python run.py single --cti-id 00 --steps 1-3

# 从步骤5重新运行
python run.py single --cti-id 00 --steps 5-6
```

---

### 场景3: 批量处理 - 处理多个CTI

```bash
# 处理前3个CTI
python run.py batch --cti-ids 00 01 02

# 处理所有CTI的前5步
python run.py batch --steps 1-5

# 处理所有CTI
python run.py batch
```

---

## 输出文件说明

### run.py 输出

```
data/cti_reports/{cti_id}/process/
├── JSONstep1_Questions.json      # 步骤1: 问题
├── JSONstep2_Answers.json        # 步骤2: 答案
├── JSONstep3_QLabels.json        # 步骤3: 标签
├── JSONstep4_Mark.json           # 步骤4: 评分
├── JSONstep5_Iteration_Form2.json # 步骤5: 迭代
└── JSONstep6_answerRes.json      # 步骤6: 最终结果 ⭐
```

---

## 依赖关系

```
run.py
├── src/pipeline/step1_question_generation.py
├── src/pipeline/step2_answer_generation.py
├── src/pipeline/step3_theme_judging.py
├── src/pipeline/step4_marking.py
├── src/pipeline/step5_iteration_form1.py
├── src/pipeline/step5_iteration_form2.py
└── src/pipeline/step6_extraction.py
```

---

## 命令速查表

### 快速命令

```bash
# 处理单个CTI
python run.py single --cti-id 00

# 批量处理
python run.py batch
```

### 帮助命令

```bash
# 主接口帮助
python run.py --help
python run.py single --help
python run.py batch --help
```

---

## 配置文件

### config/config.yaml

```yaml
# API配置
api:
  dashscope_key: "your-dashscope-api-key"

# 模型配置
model:
  qwen_model: "qwen-vl-max"
  eval_model: "qwen2.5-72b-instruct"

# 处理配置
processing:
  max_workers: 4
  batch_size: 5
  retry_times: 3
```

---

## 常见错误处理

### 错误1: API密钥未配置
```
❌ Error: DASHSCOPE_API_KEY not found
```
**解决**: 编辑 `config/config.yaml` 或设置环境变量

### 错误2: CTI目录不存在
```
❌ Error: CTI directory not found: data/cti_reports/00
```
**解决**: 检查CTI ID是否正确，目录是否存在

### 错误3: 步骤依赖文件缺失
```
❌ Error: Input file not found: JSONstep2_Answers.json
```
**解决**: 先运行前置步骤，或从步骤1重新运行

---

## 性能优化建议

### 1. 并发处理
```yaml
# config/config.yaml
processing:
  max_workers: 8  # 根据CPU核心数调整
```

### 2. 批量大小
```yaml
processing:
  batch_size: 10  # 增加批处理大小
```

### 3. 分步执行
```bash
# 分阶段执行，避免长时间运行
python run.py batch --steps 1-3
python run.py batch --steps 4-6
```

---

## 📚 相关文档

- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [README.md](README.md) - 项目主文档
- [docs/PIPELINE.md](docs/PIPELINE.md) - 流水线详细说明
- [docs/EXAMPLES.md](docs/EXAMPLES.md) - 更多使用示例

---

**最后更新**: 2026-02-03  
**版本**: 1.0.0
