# 邮箱管理系统

基于LangChain构建的智能邮箱管理系统，具备自动接收邮件、内容总结、关键信息提取、RAG检索和重要性判别等功能。

## 功能特点

1. **自动接收邮件**：通过IMAP协议自动接收邮件
2. **邮件内容总结**：使用LangChain和OpenAI API总结邮件内容，提取关键信息
3. **RAG检索系统**：基于向量数据库的邮件检索系统，可以从历史邮件中检索和提取信息
4. **重要性判别**：自动判别邮件内容的重要性并进行归类
5. **重要通知提醒**：对重要邮件发送提醒通知

## 系统架构

```
邮箱管理系统/
├── main.py                 # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── .env.example          # 环境变量示例
├── src/
│   ├── models/           # 数据模型
│   │   └── email_model.py
│   ├── services/         # 服务层
│   │   ├── email_receiver.py      # 邮件接收服务
│   │   ├── email_processor.py     # 邮件处理服务
│   │   ├── rag_service.py         # RAG检索服务
│   │   └── notification_service.py # 通知服务
│   ├── api/              # API接口
│   │   └── app.py
│   └── utils/            # 工具函数
└── README.md             # 说明文档
```

## 安装和配置

### 1. 环境要求

- Python 3.8+
- OpenAI API密钥
- 邮箱账户（支持IMAP协议）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写相应的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下配置：

```env
# 邮箱配置
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_email_password
IMAP_SERVER=imap.example.com
IMAP_PORT=993

# Gemini API配置 (用于LLM)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_BASE=https://ai.prism.uno/v1

# Qwen API配置 (用于embedding)
QWEN_API_KEY=your_qwen_api_key
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 向量数据库配置
VECTOR_DB_PATH=./vector_db

# 应用配置
FLASK_SECRET_KEY=your_flask_secret_key
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 邮件检查间隔（秒）
EMAIL_CHECK_INTERVAL=300

# 重要通知提醒配置
NOTIFICATION_EMAIL=notification@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
```

### 4. 常见邮箱配置

#### Gmail
```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password  # 需要使用应用专用密码
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

#### Outlook
```env
EMAIL_ADDRESS=your_email@outlook.com
EMAIL_PASSWORD=your_password
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

#### QQ邮箱
```env
EMAIL_ADDRESS=your_email@qq.com
EMAIL_PASSWORD=your_authorization_code  # 需要使用授权码
IMAP_SERVER=imap.qq.com
IMAP_PORT=993
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
```

## 使用方法

### 1. 测试配置

在启动系统之前，建议先运行配置测试脚本：

```bash
python test_config.py
```

这个脚本会测试：
- 配置文件是否正确
- 邮件连接是否正常
- LLM连接是否正常
- RAG服务是否正常
- 通知服务是否正常

### 2. 启动系统

```bash
python main.py
```

系统启动后，会自动：
- 连接到邮件服务器
- 开始检查新邮件
- 启动Web API服务（默认端口5000）

### 2. Web API接口

系统提供以下API接口：

#### 健康检查
```
GET /health
```

#### 获取邮件列表
```
GET /api/emails?limit=10&offset=0&importance=high&category=work
```

#### 获取邮件详情
```
GET /api/emails/{email_id}
```

#### 搜索邮件
```
POST /api/search
Content-Type: application/json

{
  "query": "搜索关键词",
  "k": 5
}
```

#### 问答系统
```
POST /api/ask
Content-Type: application/json

{
  "question": "我的问题"
}
```

#### 获取统计信息
```
GET /api/statistics
```

#### 测试通知功能
```
POST /api/system/test-notification
```

#### 重建向量数据库
```
POST /api/system/rebuild-index
```

### 3. 邮件重要性分类

系统将邮件分为以下重要性级别：

- **high**（重要）：学校老师通知、工作重要事项、紧急事务等
- **medium**（次重要）：社区通知、一般工作邮件等
- **low**（不重要）：广告、软件更新、推广邮件等

邮件类别包括：

- **work**：工作相关
- **education**：教育相关
- **community**：社区相关
- **advertisement**：广告推广
- **notification**：系统通知
- **personal**：个人邮件
- **other**：其他

## 高级功能

### 1. 自定义邮件处理规则

您可以通过修改 `src/services/email_processor.py` 中的提示模板来自定义邮件处理规则：

```python
# 修改邮件总结模板
self.summary_prompt = PromptTemplate(
    input_variables=["email_content"],
    template="""
自定义的邮件总结提示模板...
"""
)
```

### 2. 扩展通知渠道

目前系统支持邮件通知，您可以通过修改 `src/services/notification_service.py` 来添加其他通知渠道，如：

- 短信通知
- 微信通知
- 钉钉通知
- Slack通知

### 3. 数据持久化

系统使用FAISS作为向量数据库，数据存储在 `VECTOR_DB_PATH` 指定的目录中。您可以：

- 定期备份向量数据库
- 迁移向量数据库到其他存储系统
- 实现多用户隔离的向量数据库

## 故障排除

### 1. 邮件连接问题

如果无法连接到邮件服务器，请检查：

- 邮箱地址和密码是否正确
- IMAP服务器地址和端口是否正确
- 是否需要使用应用专用密码或授权码
- 邮箱是否开启了IMAP服务

### 2. OpenAI API问题

如果OpenAI API调用失败，请检查：

- API密钥是否正确
- API基础URL是否正确
- 网络连接是否正常
- API配额是否充足

### 3. LangChain弃用警告

如果您遇到LangChain的弃用警告，系统已经使用了最新的语法来替代已弃用的API：

- 使用 `prompt | llm` 替代 `LLMChain`
- 使用 `.invoke()` 方法替代 `.run()` 方法
- 使用 `from langchain_community.vectorstores import FAISS` 替代 `from langchain.vectorstores import FAISS`

如果您想使用最新版本的依赖，可以运行：

```bash
pip install --upgrade langchain langchain-openai langchain-community
```

### 4. 通知功能问题

如果通知功能不工作，请检查：

- SMTP服务器配置是否正确
- 发件人邮箱和密码是否正确
- 收件人邮箱地址是否正确
- 是否需要开启SMTP服务

## 开发指南

### 1. 添加新的邮件处理器

要添加新的邮件处理器，请：

1. 在 `src/services/` 目录下创建新的处理器文件
2. 继承基础处理器类或实现处理器接口
3. 在 `main.py` 中注册新的处理器

### 2. 扩展API接口

要添加新的API接口，请：

1. 在 `src/api/app.py` 中添加新的路由
2. 实现相应的业务逻辑
3. 添加必要的错误处理

### 3. 自定义向量数据库

要使用其他向量数据库，请：

1. 修改 `src/services/rag_service.py` 中的向量数据库实现
2. 替换FAISS为您选择的向量数据库
3. 更新相关的初始化和查询逻辑

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue
- 发送邮件至项目维护者