# 🎬 完整演示：从零开始使用MM-AttacKG

本文档将带你从零开始，逐步演示如何使用MM-AttacKG的所有功能。

---

## 📝 准备工作

### 1. 环境检查

```bash
# 检查Python版本（需要3.8+）
python --version

# 进入项目目录
cd MM-AttacKG

# 查看项目结构
ls -la
```

### 2. 安装依赖

```bash
# 安装所有依赖包
pip install -r requirements.txt

# 验证安装
python -c "import dashscope, openai, PIL; print('✓ All dependencies installed')"
```

### 3. 配置API密钥

```bash
# 复制配置模板
cp config/config.example.yaml config/config.yaml

# 使用你喜欢的编辑器打开配置文件
vim config/config.yaml  # 或者 nano, code, notepad 等
```

编辑 `config/config.yaml`：
```yaml
api:
  dashscope:
    api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxx"  # 填入你的阿里云DashScope密钥
```

保存并退出。

---

## 🎯 演示1: 处理你的第一个CTI报告

### 步骤1: 查看可用的CTI报告

```bash
# 列出所有CTI报告
ls data/cti_reports/

# 输出示例:
# 00  01  02  03  04  05  06  07  08  09  10  11
```

### 步骤2: 检查CTI报告内容

```bash
# 查看CTI 00的结构
tree data/cti_reports/00 -L 2

# 输出示例:
# data/cti_reports/00/
# ├── original/         # 原始数据
# │   ├── KG.json      # 知识图谱标注
# │   └── outline.json
# ├── picture/           # 包含CTI报告的图片
# │   ├── 001.png
# │   ├── 002.png
# │   └── ...
# └── process/        # 处理结果将保存在这里
```

### 步骤3: 运行完整流水线

```bash
# 处理CTI 00（完整6步）
python run.py single --cti-id 00
```

**运行过程输出示例：**
```
############################################################
# Processing CTI Report: 00
# Steps: 1 to 6
############################################################

============================================================
CTI 00 - Step 1: Question Generation
============================================================
Processing image: 001.png
  Image type: attack_flow
  Generated 5 questions
Processing image: 002.png
  Image type: malware_code
  Generated 7 questions
...
✓ Questions saved to: data/cti_reports/00/process/JSONstep1_Questions.json

============================================================
CTI 00 - Step 2: Answer Generation
============================================================
Answering questions for image 001.png...
  Q1: What attack techniques are shown in this flow?
  A1: The flow shows...
...
✓ Answers saved to: data/cti_reports/00/process/JSONstep2_Answers.json

============================================================
CTI 00 - Step 3: Theme Judging
============================================================
Filtering cybersecurity-relevant Q&A...
  Filtered: 45/60 relevant
✓ Labels saved to: data/cti_reports/00/process/JSONstep3_QLabels.json

============================================================
CTI 00 - Step 4: Answer Marking
============================================================
Scoring answer quality...
  Excellent: 20
  Good: 15
  Poor: 10
✓ Marks saved to: data/cti_reports/00/process/JSONstep4_Mark.json

============================================================
CTI 00 - Step 5: Iteration (Form 2)
============================================================
Refining poor quality answers...
  Refined 10 answers
✓ Iteration results saved to: data/cti_reports/00/process/JSONstep5_Iteration_Form2.json

============================================================
CTI 00 - Step 6: Answer Extraction
============================================================
Extracting final knowledge graph...
  Extracted 35 high-quality answers
✓ Final results saved to: data/cti_reports/00/process/JSONstep6_answerRes.json

############################################################
# ✓ CTI 00 Processing Complete!
############################################################
```

### 步骤4: 查看结果

```bash
# 查看最终结果
cat data/cti_reports/00/process/JSONstep6_answerRes.json

# 或者用jq美化输出
cat data/cti_reports/00/process/JSONstep6_answerRes.json | jq .

# 查看中间结果
ls -lh data/cti_reports/00/process/
```

---

## 🎯 演示2: 调试和测试单个步骤

假设你想测试问题生成功能，或者某一步出错需要重新运行。

### 只运行步骤1（问题生成）

```bash
python run.py single --cti-id 00 --steps 1-1
```

输出：
```
============================================================
CTI 00 - Step 1: Question Generation
============================================================
Processing 15 images...
✓ Generated 75 questions total
✓ Questions saved to: data/cti_reports/00/process/JSONstep1_Questions.json
```

### 运行步骤1-3（前三步）

```bash
python run.py single --cti-id 00 --steps 1-3
```

### 从步骤5重新开始（假设前4步已完成）

```bash
python run.py single --cti-id 00 --steps 5-6
```

---

## 🎯 演示3: 批量处理多个CTI报告

### 处理前3个CTI报告

```bash
python run.py batch --cti-ids 00 01 02
```

输出：
```
############################################################
# Batch Processing 3 CTI Reports
# CTI IDs: 00, 01, 02
############################################################

# 会依次处理每个CTI...
```

### 处理所有CTI报告

```bash
# 这会处理所有12个CTI报告（00-11）
python run.py batch
```

**注意**: 这可能需要较长时间，建议先测试单个CTI。

### 批量处理（只运行前5步）

```bash
# 只运行问题生成到迭代优化
python run.py batch --steps 1-5
```

---

## 🎯 演示4: 使用Python API

除了命令行接口，你也可以在Python代码中使用：

```python
# demo.py
from run import Pipeline

# 创建流水线
pipeline = Pipeline(cti_id="00")

# 运行特定步骤
pipeline.step1_question_generation()
pipeline.step2_answer_generation()
pipeline.step3_theme_judging()

# 或者运行所有步骤
pipeline.run_steps(start_step=1, end_step=6)

# 访问结果文件路径
print(f"Results at: {pipeline.files['step6_output']}")
```

运行：
```bash
python demo.py
```

---

## 🎯 演示5: 常见问题解决

### 问题1: API调用失败

```bash
# 错误信息
❌ Error: Failed to call API: 401 Unauthorized
```

**解决方法**:
```bash
# 检查API密钥
cat config/config.yaml | grep api_key

# 重新配置
vim config/config.yaml
```

### 问题2: 步骤3失败（输入文件不存在）

```bash
# 错误信息
❌ Error: Input file not found: JSONstep2_Answers.json
```

**解决方法**:
```bash
# 从步骤1重新运行
python run.py single --cti-id 00 --steps 1-6

# 或者检查文件是否存在
ls -l data/cti_reports/00/process/
```

### 问题3: 内存不足

```bash
# 错误信息
MemoryError: Unable to allocate array
```

**解决方法**:
```bash
# 减少并发数（编辑配置文件）
vim config/config.yaml

# 修改为：
processing:
  max_workers: 2
  batch_size: 3
```

### 问题4: 查看详细日志

```bash
# 查看日志文件
tail -f logs/mm_attackg.log

# 或者在运行时启用详细输出
python run.py single --cti-id 00 --verbose
```

---

## 🎯 演示6: 性能测试

### 测试单个CTI的处理时间

```bash
# Linux/Mac
time python run.py single --cti-id 00

# Windows PowerShell
Measure-Command { python run.py single --cti-id 00 }
```

### 测试不同并发配置

```python
# benchmark.py
import time
from run import Pipeline

configs = [
    {'max_workers': 2},
    {'max_workers': 4},
    {'max_workers': 8}
]

for config in configs:
    start = time.time()
    pipeline = Pipeline("00")
    pipeline.run_steps()
    elapsed = time.time() - start
    print(f"Workers: {config['max_workers']}, Time: {elapsed:.2f}s")
```

---

## 📊 总结

你已经学会了：

✅ **基础操作**
- 配置环境和API密钥
- 处理单个CTI报告
- 查看处理结果

✅ **高级功能**
- 批量处理多个CTI
- 分步骤调试
- 使用Python API

✅ **性能优化**
- 性能测试和调优

## 🔗 下一步

- 📖 阅读 [流水线详解](PIPELINE.md) 了解每个步骤的细节
- 📖 查看 [API接口文档](API_INTERFACES.md) 了解完整API
- 📖 浏览 [使用示例](EXAMPLES.md) 查看更多实际案例
- 🔧 修改 [配置文件](../config/config.example.yaml) 自定义行为

---

**祝你使用愉快！有问题欢迎提Issue。** 🎉
