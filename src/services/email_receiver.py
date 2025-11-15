from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import time

from config import Config
from src.models.email_model import Email
from src.services.school_email_client import SchoolEmailClient

logger = logging.getLogger(__name__)

class EmailReceiver:
    """邮件接收服务类"""
    
    def __init__(self):
        """初始化邮件接收服务"""
        self.school_email_client = SchoolEmailClient()
        self.last_check_time = None
        
    def connect(self) -> bool:
        """连接到IMAP服务器"""
        return self.school_email_client.connect_imap()
    
    def disconnect(self):
        """断开与IMAP服务器的连接"""
        self.school_email_client.disconnect_imap()
    
    def _ensure_connection(self) -> bool:
        """确保连接有效"""
        return self.school_email_client._ensure_imap_connection()
    
    def get_email_folders(self) -> List[str]:
        """获取所有邮件文件夹"""
        return self.school_email_client.get_folders()
    
    def select_folder(self, folder_name: str = 'INBOX') -> bool:
        """选择邮件文件夹"""
        # 学校邮箱客户端内部处理文件夹选择
        return True
    
    def get_new_emails(self, folder_name: str = 'INBOX', since: Optional[datetime] = None) -> List[Email]:
        """获取新邮件"""
        emails = self.school_email_client.get_new_emails(folder_name, since)
        
        # 更新最后检查时间
        if emails:
            self.last_check_time = datetime.now()
        
        return emails
    
    def check_emails_continuously(self, callback=None, folder_name: str = 'INBOX', interval: int = None):
        """持续检查新邮件"""
        if interval is None:
            interval = Config.EMAIL_CHECK_INTERVAL
        
        logger.info(f"开始持续检查新邮件，间隔: {interval} 秒")
        
        try:
            while True:
                # 获取新邮件
                since_time = self.last_check_time if self.last_check_time else datetime.now() - timedelta(minutes=interval//60)
                new_emails = self.get_new_emails(folder_name, since_time)
                
                if new_emails and callback:
                    # 如果有回调函数，处理新邮件
                    for email_obj in new_emails:
                        try:
                            callback(email_obj)
                        except Exception as e:
                            logger.error(f"处理邮件时出错: {str(e)}")
                            continue
                
                # 等待下一次检查
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("停止检查新邮件")
        except Exception as e:
            logger.error(f"检查新邮件时出错: {str(e)}")
        finally:
            self.disconnect()