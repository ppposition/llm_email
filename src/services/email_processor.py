import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import HumanMessage

from config import Config
from src.models.email_model import Email

logger = logging.getLogger(__name__)

class EmailProcessor:
    """邮件处理服务类，用于总结邮件内容、提取关键信息、判别重要性等"""
    
    def __init__(self):
        """初始化邮件处理器"""
        # 根据配置选择LLM提供商
        provider = Config.LLM_PROVIDER.lower()
        
        if provider == 'gemini':
            if not Config.GEMINI_API_KEY:
                raise ValueError("使用Gemini LLM时必须设置GEMINI_API_KEY")
            
            self.llm = ChatOpenAI(
                openai_api_key=Config.GEMINI_API_KEY,
                openai_api_base=Config.GEMINI_API_BASE,
                temperature=0.1,
                model_name=Config.LLM_MODEL
            )
        elif provider == 'qwen':
            if not Config.QWEN_API_KEY:
                raise ValueError("使用Qwen LLM时必须设置QWEN_API_KEY")
            
            self.llm = ChatOpenAI(
                openai_api_key=Config.QWEN_API_KEY,
                openai_api_base=Config.QWEN_API_BASE,
                temperature=0.1,
                model_name=Config.LLM_MODEL
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}，请使用 'gemini' 或 'qwen'")
        
        # 文本分割器，用于处理长邮件
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
        )
        
        # 初始化提示模板
        self._init_prompt_templates()
    
    def _init_prompt_templates(self):
        """初始化各种提示模板"""
        # 邮件总结模板
        self.summary_prompt = PromptTemplate(
            input_variables=["email_content"],
            template="""
请对以下邮件内容进行总结，提取关键信息，并以JSON格式返回结果。JSON应包含以下字段：
- summary: 邮件内容的简短总结（100-200字）
- key_points: 邮件中的关键要点列表
- action_items: 需要采取的行动项列表（如果有）
- important_dates: 重要日期列表（如果有）
- contacts: 相关联系人列表（如果有）

邮件内容：
{email_content}

请返回有效的JSON格式结果：
"""
        )
        
        # 邮件重要性判别模板
        self.importance_prompt = PromptTemplate(
            input_variables=["email_content", "sender", "subject"],
            template="""
请根据以下邮件信息，判别邮件的重要性和类别，并以JSON格式返回结果。

邮件主题：{subject}
发件人：{sender}
邮件内容：{email_content}

请根据以下标准判别：
1. 重要性级别（importance）：
   - "high": 重要（如学校老师通知、工作重要事项、紧急事务等）
   - "medium": 次重要（如社区通知、一般工作邮件等）
   - "low": 不重要（如广告、软件更新、推广邮件等）

2. 邮件类别（category）：
   - "work": 工作相关
   - "education": 教育相关
   - "community": 社区相关
   - "advertisement": 广告推广
   - "notification": 系统通知
   - "personal": 个人邮件
   - "other": 其他

请返回有效的JSON格式结果，包含importance和category字段：
"""
        )
        
        # 创建可运行的链（使用新的LCEL语法）
        self.summary_chain = self.summary_prompt | self.llm
        self.importance_chain = self.importance_prompt | self.llm
    
    def process_email(self, email: Email) -> Email:
        """处理邮件，包括总结、提取关键信息、判别重要性等"""
        try:
            logger.info(f"开始处理邮件: {email.subject}")
            
            # 准备邮件内容
            email_content = self._prepare_email_content(email)
            
            # 总结邮件内容并提取关键信息
            summary_result = self._summarize_email(email_content)
            if summary_result:
                email.summary = summary_result.get('summary', '')
                email.key_info = {
                    'key_points': summary_result.get('key_points', []),
                    'action_items': summary_result.get('action_items', []),
                    'important_dates': summary_result.get('important_dates', []),
                    'contacts': summary_result.get('contacts', [])
                }
            
            # 判别邮件重要性和类别
            importance_result = self._classify_importance(email_content, email.sender, email.subject)
            if importance_result:
                email.importance = importance_result.get('importance', 'medium')
                email.category = importance_result.get('category', 'other')
            
            logger.info(f"邮件处理完成: {email.subject}")
            return email
            
        except Exception as e:
            logger.error(f"处理邮件时出错: {str(e)}")
            return email
    
    def _prepare_email_content(self, email: Email) -> str:
        """准备邮件内容，去除不必要的格式和噪音"""
        # 合并主题和正文
        content = f"主题: {email.subject}\n\n"
        
        # 添加发件人和收件人信息
        content += f"发件人: {email.sender}\n"
        content += f"收件人: {', '.join(email.recipients)}\n"
        content += f"日期: {email.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 添加正文内容
        if email.html_body:
            # 如果有HTML正文，尝试提取纯文本
            content += self._extract_text_from_html(email.html_body)
        else:
            content += email.body
        
        # 清理内容
        content = self._clean_content(content)
        
        return content
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """从HTML内容中提取纯文本"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取文本
            text = soup.get_text(separator='\n')
            
            # 清理文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"从HTML提取文本时出错: {str(e)}")
            return html_content
    
    def _clean_content(self, content: str) -> str:
        """清理邮件内容，移除不必要的噪音"""
        # 移除多余的换行和空格
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'\s+', ' ', content)
        
        # 移除常见的邮件签名模式
        signature_patterns = [
            r'--\s*\n.*?(?=\n\n|$)',  # 标准签名
            r'Best regards,.*?(?=\n\n|$)',  # 英文祝福语
            r'此致.*?(?=\n\n|$)',  # 中文祝福语
            r'发自我的.*?(?=\n\n|$)',  # 移动设备签名
        ]
        
        for pattern in signature_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 移除转发信息
        forward_patterns = [
            r'-----Original Message-----.*?(?=\n\n|$)',
            r'----- 转发的邮件 -----.*?(?=\n\n|$)',
            r'From:.*?(?=\n\n|$)',
        ]
        
        for pattern in forward_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def _summarize_email(self, email_content: str) -> Optional[Dict[str, Any]]:
        """总结邮件内容并提取关键信息"""
        try:
            # 如果邮件内容太长，进行分割
            if len(email_content) > 4000:
                chunks = self.text_splitter.split_text(email_content)
                # 只处理前几个chunk，避免token过多
                email_content = '\n\n'.join(chunks[:3])
            
            # 调用LLM进行总结
            result = self.summary_chain.invoke({"email_content": email_content})
            
            # 提取消息内容
            if hasattr(result, 'content'):
                result_text = result.content
            else:
                result_text = str(result)
            
            # 解析JSON结果
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # 如果返回的不是有效JSON，尝试提取JSON部分
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        logger.error("无法解析总结结果为JSON")
                        return None
                
                logger.error("总结结果中未找到有效JSON")
                return None
                
        except Exception as e:
            logger.error(f"总结邮件时出错: {str(e)}")
            return None
    
    def _classify_importance(self, email_content: str, sender: str, subject: str) -> Optional[Dict[str, str]]:
        """判别邮件的重要性和类别"""
        try:
            # 如果邮件内容太长，进行截断
            if len(email_content) > 2000:
                email_content = email_content[:2000] + "..."
            
            # 调用LLM进行分类
            result = self.importance_chain.invoke({
                "email_content": email_content,
                "sender": sender,
                "subject": subject
            })
            
            # 提取消息内容
            if hasattr(result, 'content'):
                result_text = result.content
            else:
                result_text = str(result)
            
            # 解析JSON结果
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # 如果返回的不是有效JSON，尝试提取JSON部分
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        logger.error("无法解析分类结果为JSON")
                        return None
                
                logger.error("分类结果中未找到有效JSON")
                return None
                
        except Exception as e:
            logger.error(f"判别邮件重要性时出错: {str(e)}")
            return None
    
    def batch_process_emails(self, emails: List[Email]) -> List[Email]:
        """批量处理邮件"""
        processed_emails = []
        
        for email in emails:
            try:
                processed_email = self.process_email(email)
                processed_emails.append(processed_email)
            except Exception as e:
                logger.error(f"批量处理邮件时出错: {str(e)}")
                processed_emails.append(email)  # 添加未处理的邮件
        
        return processed_emails