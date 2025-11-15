import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类，用于管理所有配置项"""
    
    # 邮箱配置
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'mail.sjtu.edu.cn')  # 默认为学校邮箱IMAP服务器
    IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
    
    # SMTP配置（用于发送邮件）
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.sjtu.edu.cn')  # 默认为学校邮箱SMTP服务器
    SMTP_PORT = int(os.getenv('SMTP_PORT', 465))  # 默认为学校邮箱SMTP端口
    
    # Qwen API配置 (用于embedding)
    QWEN_API_KEY = os.getenv('QWEN_API_KEY')
    QWEN_API_BASE = os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    
    # Gemini API配置 (用于LLM)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_API_BASE = os.getenv('GEMINI_API_BASE', 'https://ai.prism.uno/v1')
    
    # 模型配置
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-pro')  # 默认模型
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')  # gemini, qwen
    
    # Embedding配置
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'Qwen/Qwen3-Embedding-8B')  # 默认embedding模型
    EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'qwen')  # qwen
    
    # 向量数据库配置
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './vector_db')
    
    # 应用配置
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # 邮件检查间隔（秒）
    EMAIL_CHECK_INTERVAL = int(os.getenv('EMAIL_CHECK_INTERVAL', 300))
    
    # 重要通知提醒配置
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
    NOTIFICATION_SMTP_SERVER = os.getenv('NOTIFICATION_SMTP_SERVER', SMTP_SERVER)  # 默认使用主SMTP服务器
    NOTIFICATION_SMTP_PORT = int(os.getenv('NOTIFICATION_SMTP_PORT', 587))  # 默认为587，支持TLS
    NOTIFICATION_SMTP_USERNAME = os.getenv('NOTIFICATION_SMTP_USERNAME', EMAIL_ADDRESS)  # 默认使用主邮箱
    NOTIFICATION_SMTP_PASSWORD = os.getenv('NOTIFICATION_SMTP_PASSWORD', EMAIL_PASSWORD)  # 默认使用主邮箱密码
    
    @classmethod
    def validate_config(cls):
        """验证必要的配置项是否存在"""
        required_fields = [
            'EMAIL_ADDRESS',
            'EMAIL_PASSWORD',
            'IMAP_SERVER',
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"缺少必要的配置项: {', '.join(missing_fields)}")
        
        return True