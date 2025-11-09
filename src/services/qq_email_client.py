#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ邮箱收发客户端
支持SMTP发送邮件和IMAP接收邮件功能
整合到现有邮箱管理系统中
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import decode_header
import os
import logging
from datetime import datetime
import time
from typing import List, Optional, Dict, Any, Union

from config import Config
from src.models.email_model import Email, EmailAttachment

# 设置日志
logger = logging.getLogger(__name__)


class QQEmailClient:
    """QQ邮箱客户端类，整合发送和接收功能"""
    
    def __init__(self, qq_email=None, auth_code=None):
        """
        初始化QQ邮箱客户端
        
        Args:
            qq_email (str): QQ邮箱地址，如果为None则使用配置文件中的值
            auth_code (str): QQ邮箱授权码（不是QQ密码），如果为None则使用配置文件中的值
        """
        # 使用传入的参数或配置文件中的值
        self.qq_email = qq_email or getattr(Config, 'EMAIL_ADDRESS', None)
        self.auth_code = auth_code or getattr(Config, 'EMAIL_PASSWORD', None)
        
        # QQ邮箱服务器配置
        self.smtp_server = getattr(Config, 'SMTP_SERVER', 'smtp.qq.com')
        self.smtp_port = getattr(Config, 'SMTP_PORT', 465)
        self.imap_server = getattr(Config, 'IMAP_SERVER', 'imap.qq.com')
        self.imap_port = getattr(Config, 'IMAP_PORT', 993)
        
        # 连接对象
        self.imap_connection = None
        
        logger.info(f"初始化QQ邮箱客户端: {self.qq_email}")
    
    def send_email(self, to_emails: Union[str, List[str]], subject: str, content: str, 
                   content_type: str = "plain", attachments: Optional[List[str]] = None) -> bool:
        """
        发送邮件
        
        Args:
            to_emails (list or str): 收件人邮箱列表
            subject (str): 邮件主题
            content (str): 邮件内容
            content_type (str): 内容类型，"plain"或"html"
            attachments (list): 附件文件路径列表
            
        Returns:
            bool: 发送是否成功
        """
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = self.qq_email
        msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
        msg['Subject'] = subject
        
        # 添加邮件正文
        if content_type == "html":
            msg.attach(MIMEText(content, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 添加附件
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        part = MIMEApplication(f.read())
                        part.add_header(
                            'Content-Disposition',
                            'attachment',
                            filename=os.path.basename(file_path)
                        )
                        msg.attach(part)
                    logger.info(f"已添加附件: {file_path}")
                else:
                    logger.warning(f"附件文件不存在: {file_path}")
        
        # 连接SMTP服务器并发送邮件
        logger.info("正在连接SMTP服务器...")
        server = None
        try:
            # 根据端口选择正确的连接方式
            if self.smtp_port == 465:
                # 465端口使用SSL直接连接
                logger.info(f"使用SSL连接到 {self.smtp_server}:{self.smtp_port}")
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            elif self.smtp_port == 587:
                # 587端口使用STARTTLS
                logger.info(f"使用STARTTLS连接到 {self.smtp_server}:{self.smtp_port}")
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                # 其他端口默认使用SSL
                logger.info(f"使用SSL连接到 {self.smtp_server}:{self.smtp_port}")
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            # 登录邮箱
            try:
                server.login(self.qq_email, self.auth_code)
                logger.info("邮箱登录成功")
            except Exception as login_error:
                logger.error(f"邮箱登录失败: {str(login_error)}")
                raise Exception(f"邮箱登录失败: {str(login_error)}")
            
            # 发送邮件
            try:
                # 使用sendmail方法，更可靠
                text = msg.as_string()
                if isinstance(to_emails, list):
                    result = server.sendmail(self.qq_email, to_emails, text)
                else:
                    result = server.sendmail(self.qq_email, [to_emails], text)
                
                # 检查sendmail的返回结果
                if result:  # 如果有返回值，表示有失败的收件人
                    logger.warning(f"部分收件人发送失败: {result}")
                else:
                    logger.info(f"邮件发送成功! 收件人: {to_emails}")
                
                return True
                
            except smtplib.SMTPRecipientsRefused as e:
                logger.error(f"收件人被拒绝: {str(e)}")
                raise Exception(f"收件人被拒绝: {str(e)}")
            except smtplib.SMTPSenderRefused as e:
                logger.error(f"发件人被拒绝: {str(e)}")
                raise Exception(f"发件人被拒绝: {str(e)}")
            except smtplib.SMTPDataError as e:
                logger.error(f"邮件数据错误: {str(e)}")
                raise Exception(f"邮件数据错误: {str(e)}")
            except smtplib.SMTPException as e:
                logger.error(f"SMTP错误: {str(e)}")
                raise Exception(f"SMTP错误: {str(e)}")
            
        except smtplib.SMTPResponseException as e:
            # 特殊处理QQ邮箱的连接关闭异常
            if e.smtp_code == -1 and e.smtp_error == b'\x00\x00\x00':
                logger.info("邮件发送成功! (QQ邮箱连接关闭异常，但邮件已成功发送)")
                logger.info(f"收件人: {to_emails}")
                return True
            else:
                logger.error(f"SMTP响应异常: {e.smtp_code}, {e.smtp_error}")
                logger.error(f"发送邮件失败: {str(e)}")
                import traceback
                logger.error(f"详细错误信息: {traceback.format_exc()}")
                return False
                
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False
            
        finally:
            # 确保连接被关闭
            if server:
                try:
                    server.quit()
                except:
                    try:
                        server.close()
                    except:
                        pass
    
    def connect_imap(self) -> bool:
        """连接到IMAP服务器"""
        try:
            # 创建IMAP连接
            self.imap_connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # 登录邮箱
            self.imap_connection.login(self.qq_email, self.auth_code)
            
            logger.info(f"成功连接到IMAP服务器: {self.imap_server}")
            return True
        except Exception as e:
            logger.error(f"连接IMAP服务器失败: {str(e)}")
            return False
    
    def disconnect_imap(self):
        """断开与IMAP服务器的连接"""
        if self.imap_connection:
            try:
                self.imap_connection.close()
                self.imap_connection.logout()
                logger.info("已断开与IMAP服务器的连接")
            except Exception as e:
                logger.error(f"断开IMAP连接时出错: {str(e)}")
            finally:
                self.imap_connection = None
    
    def _ensure_imap_connection(self) -> bool:
        """确保IMAP连接有效"""
        if not self.imap_connection:
            return self.connect_imap()
        
        try:
            # 尝试执行一个简单的命令来检查连接是否仍然有效
            self.imap_connection.noop()
            return True
        except:
            # 连接已断开，尝试重新连接
            return self.connect_imap()
    
    def receive_emails(self, folder: str = 'INBOX', limit: int = 10, unread_only: bool = False) -> List[Email]:
        """
        接收邮件
        
        Args:
            folder (str): 邮箱文件夹
            limit (int): 获取邮件数量限制
            unread_only (bool): 是否只获取未读邮件
            
        Returns:
            list: 邮件列表
        """
        emails = []
        try:
            if not self._ensure_imap_connection():
                return emails
            
            # 选择文件夹
            status, _ = self.imap_connection.select(f'"{folder}"')
            if status != 'OK':
                logger.error(f"选择文件夹失败: {folder}")
                return emails
            
            # 搜索邮件
            search_criteria = "UNSEEN" if unread_only else "ALL"
            status, message_ids = self.imap_connection.search(None, search_criteria)
            
            if status != 'OK':
                logger.error("搜索邮件失败")
                return emails
            
            # 获取邮件ID列表
            email_id_list = message_ids[0].split()
            
            # 限制邮件数量
            if limit > 0:
                email_id_list = email_id_list[-limit:]
            
            logger.info(f"找到 {len(email_id_list)} 封邮件")
            
            # 获取邮件内容
            for email_id in reversed(email_id_list):  # 从最新邮件开始
                try:
                    status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        # 解析邮件信息
                        email_obj = self._parse_email_to_model(email_id.decode('utf-8'), email_message)
                        emails.append(email_obj)
                        
                        # 如果是未读邮件，标记为已读
                        if unread_only:
                            self.imap_connection.store(email_id, '+FLAGS', '\\Seen')
                    
                    # 添加延迟避免请求过快
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(f"获取邮件 {email_id} 时出错: {str(e)}")
                    continue
            
            logger.info(f"成功获取 {len(emails)} 封邮件")
            return emails
            
        except Exception as e:
            logger.error(f"接收邮件失败: {str(e)}")
            return emails
    
    def _parse_email_to_model(self, email_id: str, email_message) -> Email:
        """
        解析邮件内容为Email模型对象
        
        Args:
            email_id (str): 邮件ID
            email_message: 邮件对象
            
        Returns:
            Email: 解析后的邮件对象
        """
        # 使用Email模型的from_mime_message方法
        return Email.from_mime_message(email_id, email_message)
    
    def get_folders(self) -> List[str]:
        """
        获取邮箱文件夹列表
        
        Returns:
            list: 文件夹列表
        """
        folders = []
        try:
            if not self._ensure_imap_connection():
                return folders
            
            status, folder_list = self.imap_connection.list()
            
            if status == 'OK':
                for folder in folder_list:
                    folder_name = folder.decode('utf-8').split('"/"')[-1].strip(' "')
                    folders.append(folder_name)
            
            logger.info(f"获取到 {len(folders)} 个文件夹")
            return folders
            
        except Exception as e:
            logger.error(f"获取文件夹列表失败: {str(e)}")
            return folders
    
    def get_new_emails(self, folder_name: str = 'INBOX', since: Optional[datetime] = None) -> List[Email]:
        """
        获取新邮件（兼容现有系统接口）
        
        Args:
            folder_name (str): 邮箱文件夹
            since (datetime): 获取此时间之后的邮件
            
        Returns:
            List[Email]: 邮件列表
        """
        if since:
            # 计算时间差，转换为天数
            days_diff = (datetime.now() - since).days
            if days_diff < 1:
                days_diff = 1
            
            # 使用搜索条件获取指定时间后的邮件
            try:
                if not self._ensure_imap_connection():
                    return []
                
                # 选择文件夹
                status, _ = self.imap_connection.select(f'"{folder_name}"')
                if status != 'OK':
                    logger.error(f"选择文件夹失败: {folder_name}")
                    return []
                
                # 搜索指定时间后的邮件
                date_str = since.strftime('%d-%b-%Y')
                status, message_ids = self.imap_connection.search(None, f'(SINCE "{date_str}")')
                
                if status != 'OK':
                    logger.error("搜索邮件失败")
                    return []
                
                # 获取邮件ID列表
                email_id_list = message_ids[0].split()
                
                logger.info(f"找到 {len(email_id_list)} 封新邮件")
                
                # 获取邮件内容
                emails = []
                for email_id in reversed(email_id_list):  # 从最新邮件开始
                    try:
                        status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
                        
                        if status == 'OK':
                            raw_email = msg_data[0][1]
                            email_message = email.message_from_bytes(raw_email)
                            
                            # 解析邮件信息
                            email_obj = self._parse_email_to_model(email_id.decode('utf-8'), email_message)
                            emails.append(email_obj)
                        
                        # 添加延迟避免请求过快
                        time.sleep(0.1)
                    except Exception as e:
                        logger.error(f"获取邮件 {email_id} 时出错: {str(e)}")
                        continue
                
                logger.info(f"成功获取 {len(emails)} 封新邮件")
                return emails
                
            except Exception as e:
                logger.error(f"获取新邮件时出错: {str(e)}")
                return []
        else:
            # 如果没有指定时间，获取未读邮件
            return self.receive_emails(folder=folder_name, limit=10, unread_only=True)