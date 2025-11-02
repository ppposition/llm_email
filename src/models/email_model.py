from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64
import re

@dataclass
class EmailAttachment:
    """邮件附件数据模型"""
    filename: str
    content_type: str
    size: int
    content: bytes = field(repr=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size
        }

@dataclass
class Email:
    """邮件数据模型"""
    id: str
    subject: str
    sender: str
    recipients: List[str]
    date: datetime
    body: str
    html_body: Optional[str] = None
    attachments: List[EmailAttachment] = field(default_factory=list)
    importance: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    key_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'subject': self.subject,
            'sender': self.sender,
            'recipients': self.recipients,
            'date': self.date.isoformat(),
            'body': self.body,
            'html_body': self.html_body,
            'attachments': [att.to_dict() for att in self.attachments],
            'importance': self.importance,
            'category': self.category,
            'summary': self.summary,
            'key_info': self.key_info
        }
    
    @classmethod
    def from_mime_message(cls, msg_id: str, mime_msg: MIMEMultipart) -> 'Email':
        """从MIME消息创建Email对象"""
        # 解析发件人
        sender = cls._extract_email_address(mime_msg['From'])
        
        # 解析收件人
        recipients = []
        if 'To' in mime_msg:
            recipients.extend(cls._extract_email_addresses(mime_msg['To']))
        if 'Cc' in mime_msg:
            recipients.extend(cls._extract_email_addresses(mime_msg['Cc']))
        
        # 解析日期
        date_str = mime_msg['Date']
        date = cls._parse_date(date_str)
        
        # 解析主题
        subject = cls._decode_header(mime_msg['Subject'])
        
        # 解析正文
        body, html_body = cls._extract_body(mime_msg)
        
        # 解析附件
        attachments = cls._extract_attachments(mime_msg)
        
        return cls(
            id=msg_id,
            subject=subject,
            sender=sender,
            recipients=recipients,
            date=date,
            body=body,
            html_body=html_body,
            attachments=attachments
        )
    
    @staticmethod
    def _extract_email_address(address_str: str) -> str:
        """从地址字符串中提取邮箱地址"""
        if not address_str:
            return ""
        
        # 使用正则表达式提取邮箱地址
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(email_pattern, address_str)
        return match.group() if match else address_str
    
    @staticmethod
    def _extract_email_addresses(addresses_str: str) -> List[str]:
        """从地址字符串中提取多个邮箱地址"""
        if not addresses_str:
            return []
        
        # 分割地址并提取每个地址
        addresses = addresses_str.split(',')
        return [Email._extract_email_address(addr.strip()) for addr in addresses]
    
    @staticmethod
    def _decode_header(header_str: str) -> str:
        """解码邮件头部"""
        if not header_str:
            return ""
        
        # 简单的头部解码，实际可能需要更复杂的处理
        try:
            from email.header import decode_header
            decoded_parts = decode_header(header_str)
            result = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        result.append(part.decode(encoding))
                    else:
                        result.append(part.decode('utf-8', errors='ignore'))
                else:
                    result.append(str(part))
            return ''.join(result)
        except:
            return header_str
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return datetime.now()
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now()
    
    @staticmethod
    def _extract_body(mime_msg: MIMEMultipart) -> tuple[str, Optional[str]]:
        """提取邮件正文"""
        body = ""
        html_body = None
        
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                # 跳过附件
                if 'attachment' in content_disposition:
                    continue
                
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
                elif content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    html_body = payload.decode(charset, errors='ignore')
        else:
            # 单部分邮件
            payload = mime_msg.get_payload(decode=True)
            charset = mime_msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='ignore')
        
        return body, html_body
    
    @staticmethod
    def _extract_attachments(mime_msg: MIMEMultipart) -> List[EmailAttachment]:
        """提取邮件附件"""
        attachments = []
        
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                content_disposition = str(part.get('Content-Disposition', ''))
                
                if 'attachment' in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = Email._decode_header(filename)
                        content_type = part.get_content_type()
                        content = part.get_payload(decode=True)
                        size = len(content)
                        
                        attachments.append(EmailAttachment(
                            filename=filename,
                            content_type=content_type,
                            size=size,
                            content=content
                        ))
        
        return attachments