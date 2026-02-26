# 📚 MM-AttacKG 文档索引

欢迎使用MM-AttacKG！这是一个完整的文档导航页面，帮助你快速找到所需信息。

---

## 🚀 快速导航

### 新手入门（推荐顺序）
1. [README.md](README.md) - **从这里开始** - 项目概览和基本介绍
2. [QUICKSTART.md](QUICKSTART.md) - **快速上手** - 5分钟开始使用
3. [docs/FULL_DEMO.md](docs/FULL_DEMO.md) - **完整演示** - 手把手教程

### 进阶使用
4. [docs/API_INTERFACES.md](docs/API_INTERFACES.md) - **接口文档** - 详细的API说明
5. [docs/PIPELINE.md](docs/PIPELINE.md) - **流水线详解** - 6步流程深入解析
6. [docs/EXAMPLES.md](docs/EXAMPLES.md) - **使用示例** - 更多实际案例

### 项目维护
7. [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
8. [CHANGELOG.md](CHANGELOG.md) - 版本历史
9. [LICENSE](LICENSE) - MIT许可证

---

## 📖 按主题查找

### 🎯 使用指南

#### 基础使用
- **处理单个CTI报告**
  - [QUICKSTART.md#场景1](QUICKSTART.md#场景1-处理单个cti报告)
  - [docs/FULL_DEMO.md#演示1](docs/FULL_DEMO.md#演示1-处理你的第一个cti报告)

- **批量处理**
  - [QUICKSTART.md#场景2](QUICKSTART.md#场景2-批量处理多个cti报告)
  - [docs/FULL_DEMO.md#演示3](docs/FULL_DEMO.md#演示3-批量处理多个cti报告)

- **调试特定步骤**
  - [docs/FULL_DEMO.md#演示2](docs/FULL_DEMO.md#演示2-调试和测试单个步骤)

#### 高级功能
- **使用Python API**
  - [docs/FULL_DEMO.md#演示6](docs/FULL_DEMO.md#演示6-使用python-api)
  - [docs/API_INTERFACES.md](docs/API_INTERFACES.md)

- **性能优化**
  - [QUICKSTART.md#高级用法](QUICKSTART.md#高级用法)
  - [docs/FULL_DEMO.md#演示6](docs/FULL_DEMO.md#演示6-性能测试)

---

### 🔧 技术文档

#### 系统架构
- **流水线架构** - [docs/PIPELINE.md](docs/PIPELINE.md)

#### 接口文档
- **运行接口 (run.py)** - [docs/API_INTERFACES.md#主运行接口](docs/API_INTERFACES.md#主运行接口)
- **核心Pipeline类** - [docs/API_INTERFACES.md#核心类-pipeline](docs/API_INTERFACES.md)

#### 配置管理
- **配置文件** - [config/config.example.yaml](config/config.example.yaml)
- **环境变量** - [.env.example](.env.example)
- **日志配置** - [QUICKSTART.md#查看日志](QUICKSTART.md)

---

### 🛠️ 开发指南

#### 贡献代码
- **贡献指南** - [CONTRIBUTING.md](CONTRIBUTING.md)
- **代码风格** - [CONTRIBUTING.md#代码风格](CONTRIBUTING.md)
- **测试指南** - [CONTRIBUTING.md#测试](CONTRIBUTING.md)

#### 项目维护
- **版本历史** - [CHANGELOG.md](CHANGELOG.md)

---

### ❓ 故障排除

#### 常见问题
- **API密钥配置** - [QUICKSTART.md#q1](QUICKSTART.md#q1-没有api密钥怎么办)
- **处理速度优化** - [QUICKSTART.md#q2](QUICKSTART.md#q2-处理速度很慢)
- **错误恢复** - [QUICKSTART.md#q3](QUICKSTART.md#q3-某一步失败了怎么办)
- **结果验证** - [QUICKSTART.md#q4](QUICKSTART.md#q4-如何验证结果正确性)

#### 错误处理
- **常见错误** - [docs/FULL_DEMO.md#演示7](docs/FULL_DEMO.md#演示7-常见问题解决)
- **详细日志** - [QUICKSTART.md#查看日志](QUICKSTART.md#查看日志)

---

## 📁 文档结构

```
MM-AttacKG/
│
├── README.md                     ⭐ 项目主文档（从这里开始）
├── QUICKSTART.md                 ⭐ 快速开始指南
├── LICENSE                       ⭐ MIT许可证
├── CONTRIBUTING.md               ⭐ 贡献指南
├── CHANGELOG.md                  ⭐ 版本历史
│
├── docs/                         📚 详细文档目录
│   ├── API_INTERFACES.md         ⭐ 接口文档（推荐）
│   ├── FULL_DEMO.md              ⭐ 完整演示（推荐）
│   ├── PIPELINE.md               ⭐ 流水线详解
│   └── EXAMPLES.md               使用示例
│
├── config/                       ⚙️ 配置文件
│   ├── config.example.yaml       配置模板
│   └── config.yaml               （需要创建）
│
└── .env.example                  环境变量模板
```

---

## 🎯 使用场景索引

### 场景1: 我是新手，第一次使用
**阅读顺序**:
1. [README.md](README.md) - 了解项目
2. [QUICKSTART.md](QUICKSTART.md) - 安装配置
3. [docs/FULL_DEMO.md#演示1](docs/FULL_DEMO.md) - 运行第一个示例

**关键命令**:
```bash
# 配置环境
cp config/config.example.yaml config/config.yaml

# 运行第一个CTI
python run.py single --cti-id 00
```

---

### 场景2: 我要处理大量CTI报告
**参考文档**:
- [QUICKSTART.md#场景2](QUICKSTART.md#场景2-批量处理多个cti报告)
- [docs/API_INTERFACES.md#batch命令](docs/API_INTERFACES.md)

**关键命令**:
```bash
# 批量处理所有CTI
python run.py batch

# 处理指定CTI
python run.py batch --cti-ids 00 01 02 03
```

---

### 场景3: 某个步骤出错，需要调试
**参考文档**:
- [docs/FULL_DEMO.md#演示2](docs/FULL_DEMO.md#演示2-调试和测试单个步骤)
- [docs/FULL_DEMO.md#演示7](docs/FULL_DEMO.md#演示7-常见问题解决)

**关键命令**:
```bash
# 只运行步骤1
python run.py single --cti-id 00 --steps 1-1

# 从步骤3重新运行
python run.py single --cti-id 00 --steps 3-6
```

---

### 场景4: 我要自定义处理流程
**参考文档**:
- [docs/API_INTERFACES.md#核心类-pipeline](docs/API_INTERFACES.md)
- [docs/FULL_DEMO.md#演示6](docs/FULL_DEMO.md#演示6-使用python-api)

**示例代码**:
```python
from run import Pipeline

pipeline = Pipeline(cti_id="00")
pipeline.step1_question_generation()
pipeline.step2_answer_generation()
# 自定义后续步骤...
```

---

### 场景5: 我要优化处理性能
**参考文档**:
- [QUICKSTART.md#高级用法](QUICKSTART.md#高级用法)
- [docs/API_INTERFACES.md#性能优化建议](docs/API_INTERFACES.md)

**配置示例**:
```yaml
# config/config.yaml
processing:
  max_workers: 8
  batch_size: 10
```

---

## 🔍 快速搜索

### 按关键词查找

| 关键词 | 相关文档 |
|--------|----------|
| 安装配置 | [QUICKSTART.md](QUICKSTART.md) |
| API密钥 | [QUICKSTART.md#api密钥配置](QUICKSTART.md) |
| 命令行 | [docs/API_INTERFACES.md#命令速查表](docs/API_INTERFACES.md) |
| Python API | [docs/FULL_DEMO.md#演示4](docs/FULL_DEMO.md) |
| 批量处理 | [QUICKSTART.md#场景2](QUICKSTART.md) |
| 错误处理 | [docs/FULL_DEMO.md#演示5](docs/FULL_DEMO.md) |
| 性能优化 | [docs/API_INTERFACES.md#性能优化建议](docs/API_INTERFACES.md) |
| 流水线步骤 | [docs/PIPELINE.md](docs/PIPELINE.md) |

---

## 📞 获取帮助

### 命令行帮助
```bash
# 主程序帮助
python run.py --help

# 子命令帮助
python run.py single --help
python run.py batch --help
```

### 文档内搜索
使用编辑器的搜索功能（Ctrl+F 或 Cmd+F）在文档中搜索关键词。

### 在线支持
- GitHub Issues: [提交问题](https://github.com/yourusername/MM-AttacKG/issues)
- 讨论区: [加入讨论](https://github.com/yourusername/MM-AttacKG/discussions)

---

## 📝 文档维护

### 文档版本
- 最后更新: 2026-02-03
- 文档版本: 1.0.0
- 项目版本: 0.1.0

### 文档贡献
如果你发现文档有错误或需要改进，欢迎：
1. 提交Issue报告问题
2. 提交PR改进文档
3. 参与讨论提供建议

查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

---

## 🎉 开始使用

**推荐的学习路径：**

```
1️⃣ 阅读 README.md（5分钟）
    ↓
2️⃣ 跟随 QUICKSTART.md 配置环境（10分钟）
    ↓
3️⃣ 运行第一个示例（参考 FULL_DEMO.md 演示1）（5分钟）
    ↓
4️⃣ 尝试批量处理（参考 FULL_DEMO.md 演示3）（可选）
    ↓
5️⃣ 深入学习 API 和架构（参考 API_INTERFACES.md 和 PIPELINE.md）
```

**总时间**: 20-30分钟即可上手，1-2小时深入掌握

---

**祝你使用愉快！** 🚀
