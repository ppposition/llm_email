import imaplib
import email
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import time
import re

from config import Config
from src.models.email_model import Email

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailReceiver:
    """邮件接收服务类"""
    
    def __init__(self):
        """初始化邮件接收服务"""
        self.imap_server = Config.IMAP_SERVER
        self.imap_port = Config.IMAP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.connection = None
        self.last_check_time = None
        
    def connect(self) -> bool:
        """连接到IMAP服务器"""
        try:
            # 创建IMAP连接
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # 登录邮箱
            self.connection.login(self.email_address, self.email_password)
            
            logger.info(f"成功连接到邮件服务器: {self.imap_server}")
            return True
        except Exception as e:
            logger.error(f"连接邮件服务器失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开与IMAP服务器的连接"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("已断开与邮件服务器的连接")
            except Exception as e:
                logger.error(f"断开连接时出错: {str(e)}")
            finally:
                self.connection = None
    
    def _ensure_connection(self) -> bool:
        """确保连接有效"""
        if not self.connection:
            return self.connect()
        
        try:
            # 尝试执行一个简单的命令来检查连接是否仍然有效
            self.connection.noop()
            return True
        except:
            # 连接已断开，尝试重新连接
            return self.connect()
    
    def get_email_folders(self) -> List[str]:
        """获取所有邮件文件夹"""
        if not self._ensure_connection():
            return []
        
        try:
            status, folder_list = self.connection.list()
            if status != 'OK':
                logger.error("获取邮件文件夹失败")
                return []
            
            folders = []
            for folder_data in folder_list:
                # 解析文件夹名称
                folder_bytes = folder_data
                if isinstance(folder_data, tuple):
                    folder_bytes = folder_data[1]
                
                folder_str = folder_bytes.decode('utf-8')
                # 提取文件夹名称（去除引号和标记）
                folder_match = re.search(r'"([^"]+)"$', folder_str)
                if folder_match:
                    folders.append(folder_match.group(1))
            
            return folders
        except Exception as e:
            logger.error(f"获取邮件文件夹时出错: {str(e)}")
            return []
    
    def select_folder(self, folder_name: str = 'INBOX') -> bool:
        """选择邮件文件夹"""
        if not self._ensure_connection():
            return False
        
        try:
            status, _ = self.connection.select(f'"{folder_name}"')
            if status != 'OK':
                logger.error(f"选择文件夹失败: {folder_name}")
                return False
            
            logger.info(f"已选择文件夹: {folder_name}")
            return True
        except Exception as e:
            logger.error(f"选择文件夹时出错: {str(e)}")
            return False
    
    def get_new_emails(self, folder_name: str = 'INBOX', since: Optional[datetime] = None) -> List[Email]:
        """获取新邮件"""
        if not self._ensure_connection():
            return []
        
        if not self.select_folder(folder_name):
            return []
        
        try:
            # 构建搜索条件
            search_criteria = []
            if since:
                # 格式化日期为IMAP要求的格式
                date_str = since.strftime('%d-%b-%Y')
                search_criteria.append(f'SINCE "{date_str}"')
            
            # 如果没有指定时间，获取所有未读邮件
            if not search_criteria:
                search_criteria.append('UNSEEN')
            
            search_str = ' '.join(search_criteria)
            
            # 搜索邮件
            status, email_ids = self.connection.search(None, search_str)
            if status != 'OK':
                logger.error("搜索邮件失败")
                return []
            
            # 解析邮件ID
            email_id_list = email_ids[0].split()
            if not email_id_list:
                logger.info("没有找到新邮件")
                return []
            
            logger.info(f"找到 {len(email_id_list)} 封新邮件")
            
            # 获取邮件内容
            emails = []
            for email_id in email_id_list:
                try:
                    email_obj = self._fetch_email(email_id.decode('utf-8'))
                    if email_obj:
                        emails.append(email_obj)
                except Exception as e:
                    logger.error(f"获取邮件 {email_id} 时出错: {str(e)}")
                    continue
            
            # 更新最后检查时间
            self.last_check_time = datetime.now()
            
            return emails
        except Exception as e:
            logger.error(f"获取新邮件时出错: {str(e)}")
            return []
    
    def _fetch_email(self, email_id: str) -> Optional[Email]:
        """获取单封邮件"""
        try:
            # 获取邮件
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')
            if status != 'OK':
                logger.error(f"获取邮件 {email_id} 失败")
                return None
            
            # 解析邮件
            raw_email = msg_data[0][1]
            mime_msg = email.message_from_bytes(raw_email)
            
            # 创建Email对象
            email_obj = Email.from_mime_message(email_id, mime_msg)
            
            # 标记为已读
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            
            return email_obj
        except Exception as e:
            logger.error(f"解析邮件 {email_id} 时出错: {str(e)}")
            return None
    
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