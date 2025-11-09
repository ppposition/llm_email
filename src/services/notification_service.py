import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from config import Config
from src.models.email_model import Email
from src.services.qq_email_client import QQEmailClient

logger = logging.getLogger(__name__)

class NotificationService:
    """通知服务类，用于发送重要邮件提醒"""
    
    def __init__(self):
        """初始化通知服务"""
        # 使用通知专用的SMTP配置
        self.smtp_server = Config.NOTIFICATION_SMTP_SERVER
        self.smtp_port = Config.NOTIFICATION_SMTP_PORT
        self.smtp_username = Config.NOTIFICATION_SMTP_USERNAME
        self.smtp_password = Config.NOTIFICATION_SMTP_PASSWORD
        self.notification_email = Config.NOTIFICATION_EMAIL
        
        # 创建QQ邮箱客户端用于发送通知
        self.qq_email_client = QQEmailClient(
            qq_email=self.smtp_username,
            auth_code=self.smtp_password
        )
        
        # 验证通知配置
        self._validate_notification_config()
    
    def _validate_notification_config(self):
        """验证通知配置"""
        required_fields = [
            'NOTIFICATION_EMAIL',
            'NOTIFICATION_SMTP_SERVER',
            'NOTIFICATION_SMTP_USERNAME',
            'NOTIFICATION_SMTP_PASSWORD'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(Config, field):
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"缺少通知配置项: {', '.join(missing_fields)}")
            logger.warning("通知功能将不可用")
    
    def is_notification_enabled(self) -> bool:
        """检查通知功能是否启用"""
        return all([
            self.notification_email,
            self.smtp_server,
            self.smtp_username,
            self.smtp_password
        ])
    
    def send_important_email_notification(self, email: Email) -> bool:
        """发送重要邮件通知"""
        if not self.is_notification_enabled():
            logger.warning("通知功能未启用，无法发送通知")
            return False
        
        try:
            logger.info(f"发送重要邮件通知: {email.subject}")
            
            # 创建邮件内容
            subject = f"重要邮件提醒: {email.subject}"
            body = self._create_notification_body(email)
            
            # 发送邮件
            success = self._send_email(
                to_email=self.notification_email,
                subject=subject,
                body=body
            )
            
            if success:
                logger.info(f"重要邮件通知发送成功: {email.subject}")
            else:
                logger.error(f"重要邮件通知发送失败: {email.subject}")
            
            return success
            
        except Exception as e:
            logger.error(f"发送重要邮件通知时出错: {str(e)}")
            return False
    
    def send_batch_important_email_notification(self, emails: List[Email]) -> int:
        """批量发送重要邮件通知"""
        if not self.is_notification_enabled():
            logger.warning("通知功能未启用，无法发送通知")
            return 0
        
        try:
            logger.info(f"批量发送 {len(emails)} 封重要邮件通知")
            
            success_count = 0
            
            # 如果有多封重要邮件，合并为一封通知邮件
            if len(emails) > 1:
                subject = f"重要邮件提醒: 共 {len(emails)} 封重要邮件"
                body = self._create_batch_notification_body(emails)
                
                success = self._send_email(
                    to_email=self.notification_email,
                    subject=subject,
                    body=body
                )
                
                if success:
                    success_count = len(emails)
                    logger.info(f"批量重要邮件通知发送成功，共 {success_count} 封")
                else:
                    logger.error("批量重要邮件通知发送失败")
            else:
                # 只有一封邮件，单独发送
                for email in emails:
                    if self.send_important_email_notification(email):
                        success_count += 1
            
            return success_count
            
        except Exception as e:
            logger.error(f"批量发送重要邮件通知时出错: {str(e)}")
            return 0
    
    def _create_notification_body(self, email: Email) -> str:
        """创建单封邮件的通知内容"""
        body = f"""
您收到了一封重要邮件，详情如下：

主题: {email.subject}
发件人: {email.sender}
收件人: {', '.join(email.recipients)}
日期: {email.date.strftime('%Y-%m-%d %H:%M:%S')}
重要性: {email.importance}
类别: {email.category}

"""
        
        # 添加邮件总结（如果有）
        if email.summary:
            body += f"邮件总结:\n{email.summary}\n\n"
        
        # 添加关键信息（如果有）
        if email.key_info:
            body += "关键信息:\n"
            if email.key_info.get('key_points'):
                body += f"关键要点: {'; '.join(email.key_info['key_points'])}\n"
            if email.key_info.get('action_items'):
                body += f"行动项: {'; '.join(email.key_info['action_items'])}\n"
            if email.key_info.get('important_dates'):
                body += f"重要日期: {'; '.join(email.key_info['important_dates'])}\n"
            if email.key_info.get('contacts'):
                body += f"联系人: {'; '.join(email.key_info['contacts'])}\n"
            body += "\n"
        
        # 添加邮件正文预览
        body += "邮件正文预览:\n"
        preview_length = 500  # 预览长度
        if len(email.body) > preview_length:
            body += email.body[:preview_length] + "..."
        else:
            body += email.body
        
        body += "\n\n---\n此邮件由邮箱管理系统自动发送"
        
        return body
    
    def _create_batch_notification_body(self, emails: List[Email]) -> str:
        """创建批量邮件的通知内容"""
        body = f"""
您收到了 {len(emails)} 封重要邮件，详情如下：

"""
        
        # 添加每封邮件的摘要信息
        for i, email in enumerate(emails, 1):
            body += f"{i}. 主题: {email.subject}\n"
            body += f"   发件人: {email.sender}\n"
            body += f"   日期: {email.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            body += f"   重要性: {email.importance}\n"
            body += f"   类别: {email.category}\n"
            
            # 添加邮件总结（如果有）
            if email.summary:
                body += f"   总结: {email.summary[:100]}...\n"
            
            body += "\n"
        
        body += "---\n此邮件由邮箱管理系统自动发送"
        
        return body
    
    def _send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """发送邮件"""
        try:
            # 使用QQ邮箱客户端发送邮件
            content_type = "html" if is_html else "plain"
            return self.qq_email_client.send_email(
                to_emails=to_email,
                subject=subject,
                content=body,
                content_type=content_type
            )
            
        except Exception as e:
            logger.error(f"发送邮件时出错: {str(e)}")
            return False
    
    def send_system_notification(self, subject: str, message: str) -> bool:
        """发送系统通知"""
        if not self.is_notification_enabled():
            logger.warning("通知功能未启用，无法发送系统通知")
            return False
        
        try:
            logger.info(f"发送系统通知: {subject}")
            
            # 创建邮件内容
            body = f"""
系统通知:

{message}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
此邮件由邮箱管理系统自动发送
"""
            
            # 发送邮件
            success = self._send_email(
                to_email=self.notification_email,
                subject=f"系统通知: {subject}",
                body=body
            )
            
            if success:
                logger.info(f"系统通知发送成功: {subject}")
            else:
                logger.error(f"系统通知发送失败: {subject}")
            
            return success
            
        except Exception as e:
            logger.error(f"发送系统通知时出错: {str(e)}")
            return False
    
    def send_error_notification(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """发送错误通知"""
        if not self.is_notification_enabled():
            logger.warning("通知功能未启用，无法发送错误通知")
            return False
        
        try:
            logger.info("发送错误通知")
            
            # 创建邮件内容
            body = f"""
系统错误通知:

错误信息: {error_message}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 添加上下文信息（如果有）
            if context:
                body += "\n上下文信息:\n"
                try:
                    body += json.dumps(context, indent=2, ensure_ascii=False)
                except:
                    body += str(context)
            
            body += "\n---\n此邮件由邮箱管理系统自动发送"
            
            # 发送邮件
            success = self._send_email(
                to_email=self.notification_email,
                subject="系统错误通知",
                body=body
            )
            
            if success:
                logger.info("错误通知发送成功")
            else:
                logger.error("错误通知发送失败")
            
            return success
            
        except Exception as e:
            logger.error(f"发送错误通知时出错: {str(e)}")
            return False
    
    def test_notification(self) -> bool:
        """测试通知功能"""
        if not self.is_notification_enabled():
            logger.warning("通知功能未启用，无法测试")
            return False
        
        try:
            logger.info("测试通知功能")
            
            # 创建测试邮件内容
            body = """
这是一封测试邮件，用于验证邮箱管理系统的通知功能是否正常工作。

如果您收到此邮件，说明通知功能配置正确。

时间: {}

---
此邮件由邮箱管理系统自动发送
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 发送测试邮件
            success = self._send_email(
                to_email=self.notification_email,
                subject="邮箱管理系统通知功能测试",
                body=body
            )
            
            if success:
                logger.info("通知功能测试成功")
            else:
                logger.error("通知功能测试失败")
            
            return success
            
        except Exception as e:
            logger.error(f"测试通知功能时出错: {str(e)}")
            return False