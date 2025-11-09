# QQ邮箱收发系统

这是一个基于原有邮箱管理系统改造的QQ邮箱收发系统，整合了SMTP发送和IMAP接收功能，并保留了原有的邮件处理、RAG搜索和通知功能。

## 功能特点

- **邮件发送**：支持SMTP发送纯文本和HTML邮件，支持附件
- **邮件接收**：支持IMAP接收邮件，自动解析邮件内容
- **邮件处理**：使用LLM对邮件进行总结、分类和重要性判别
- **RAG搜索**：基于向量数据库的邮件内容搜索和问答
- **通知服务**：重要邮件自动通知功能
- **Web API**：提供RESTful API接口
- **模块化设计**：各功能模块独立，易于维护和扩展

## 系统架构

```
邮箱管理系统
├── QQ邮箱客户端 (src/services/qq_email_client.py)
│   ├── SMTP邮件发送
│   └── IMAP邮件接收
├── 邮件接收服务 (src/services/email_receiver.py)
├── 邮件处理服务 (src/services/email_processor.py)
├── RAG服务 (src/services/rag_service.py)
├── 通知服务 (src/services/notification_service.py)
├── Web API (src/api/app.py)
└── 主程序 (main.py)
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置QQ邮箱

1. 登录QQ邮箱网页版
2. 点击设置 -> 账户
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"IMAP/SMTP服务"
5. 按照提示发送短信获取授权码
6. 复制`.env.example`为`.env`并填入配置信息

### 3. 环境变量配置

编辑`.env`文件，配置以下参数：

```env
# QQ邮箱配置
EMAIL_ADDRESS=your_qq@qq.com
EMAIL_PASSWORD=your_qq_auth_code  # QQ邮箱授权码，不是QQ密码
IMAP_SERVER=imap.qq.com
IMAP_PORT=993

# SMTP配置（用于发送邮件）
SMTP_SERVER=smtp.qq.com
SMTP_PORT=465

# 重要通知提醒配置
NOTIFICATION_EMAIL=notification@example.com
NOTIFICATION_SMTP_SERVER=smtp.qq.com
NOTIFICATION_SMTP_PORT=587
NOTIFICATION_SMTP_USERNAME=your_notification_smtp_username
NOTIFICATION_SMTP_PASSWORD=your_notification_smtp_password

# LLM配置
LLM_PROVIDER=gemini  # 或 qwen
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_BASE=https://ai.prism.uno/v1
LLM_MODEL=gemini-2.5-pro

# Embedding配置
EMBEDDING_PROVIDER=qwen
QWEN_API_KEY=your_qwen_api_key
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-8B

# 其他配置
VECTOR_DB_PATH=./vector_db
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
EMAIL_CHECK_INTERVAL=300
```

## 使用方法

### 1. 运行完整系统

```bash
python main.py
```

这将启动：
- 邮件检查循环（定期检查新邮件）
- Web API服务（http://localhost:5000）
- 邮件处理和RAG服务

### 2. 运行示例程序

```bash
python qq_email_system_example.py
```

提供交互式界面，可以测试各种功能：
- 发送邮件
- 接收邮件
- 处理邮件
- 测试通知功能
- RAG服务示例

### 3. 直接使用QQ邮箱客户端

```python
from src.services.qq_email_client import QQEmailClient

# 创建客户端
client = QQEmailClient()

# 发送邮件
client.send_email(
    to_emails="recipient@example.com",
    subject="测试邮件",
    content="这是一封测试邮件"
)

# 接收邮件
emails = client.receive_emails(limit=10, unread_only=True)
for email in emails:
    print(f"主题: {email.subject}")
    print(f"发件人: {email.sender}")
```

## API接口

系统提供以下RESTful API接口：

### 邮件相关

- `GET /api/emails` - 获取邮件列表
- `GET /api/emails/<email_id>` - 获取单封邮件详情
- `POST /api/emails/send` - 发送邮件
- `GET /api/emails/folders` - 获取邮件文件夹列表

### 搜索和问答

- `POST /api/search` - 搜索邮件
- `POST /api/ask` - 基于邮件内容回答问题

### 统计和系统管理

- `GET /api/statistics` - 获取邮件统计信息
- `POST /api/system/test-notification` - 测试通知功能
- `POST /api/system/rebuild-index` - 重建向量数据库索引

### 健康检查

- `GET /health` - 健康检查

## 示例API调用

### 发送邮件

```bash
curl -X POST http://localhost:5000/api/emails/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_emails": ["recipient@example.com"],
    "subject": "测试邮件",
    "content": "这是一封测试邮件",
    "content_type": "plain"
  }'
```

### 搜索邮件

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "重要会议",
    "k": 5
  }'
```

## 注意事项

1. **授权码安全**：QQ邮箱授权码是敏感信息，请妥善保管，不要提交到版本控制系统
2. **API限制**：注意QQ邮箱的发送频率限制，避免被识别为垃圾邮件
3. **LLM配置**：确保正确配置LLM API密钥，否则邮件处理功能将无法正常工作
4. **向量数据库**：首次使用时，系统会自动创建向量数据库索引

## 故障排除

### 常见问题

1. **连接失败**：检查邮箱地址和授权码是否正确
2. **发送失败**：检查SMTP服务器配置和网络连接
3. **处理失败**：检查LLM API配置和密钥
4. **通知失败**：检查通知邮箱配置

### 日志查看

系统日志保存在`email_system.log`文件中，可以通过查看日志排查问题：

```bash
tail -f email_system.log
```

## 扩展开发

### 添加新的邮件处理器

```python
from src.services.email_processor import EmailProcessor

class CustomEmailProcessor(EmailProcessor):
    def process_email(self, email):
        # 自定义处理逻辑
        processed_email = super().process_email(email)
        # 添加额外处理
        return processed_email
```

### 添加新的通知渠道

```python
from src.services.notification_service import NotificationService

class CustomNotificationService(NotificationService):
    def send_custom_notification(self, message):
        # 自定义通知逻辑
        pass
```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。