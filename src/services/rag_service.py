import os
import logging
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from config import Config
from src.models.email_model import Email

logger = logging.getLogger(__name__)

class RAGService:
    """RAG检索服务类，用于从历史邮件中检索和提取信息"""
    
    def __init__(self):
        """初始化RAG服务"""
        self.vector_db_path = Config.VECTOR_DB_PATH
        
        # 根据配置选择embedding提供商
        self.embeddings = self._init_embeddings()
        
        # 根据配置选择LLM提供商
        self.llm = self._init_llm()
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # 向量数据库
        self.vector_store = None
        self.qa_chain = None
        
        # 确保向量数据库目录存在
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # 加载或初始化向量数据库
        self._load_or_init_vector_store()
        
        # 初始化QA链
        self._init_qa_chain()
    
    def _init_embeddings(self):
        """根据配置初始化embedding模型"""
        provider = Config.EMBEDDING_PROVIDER.lower()
        
        if provider == 'qwen':
            if not Config.QWEN_API_KEY:
                raise ValueError("使用Qwen embedding时必须设置QWEN_API_KEY")
            
            logger.info(f"使用Qwen embedding模型: {Config.EMBEDDING_MODEL}")
            return OpenAIEmbeddings(
                openai_api_key=Config.QWEN_API_KEY,
                openai_api_base=Config.QWEN_API_BASE,
                model=Config.EMBEDDING_MODEL
            )
        else:
            raise ValueError(f"不支持的embedding提供商: {provider}，请使用 'qwen'")
    
    def _init_llm(self):
        """根据配置初始化LLM模型"""
        provider = Config.LLM_PROVIDER.lower()
        
        if provider == 'gemini':
            if not Config.GEMINI_API_KEY:
                raise ValueError("使用Gemini LLM时必须设置GEMINI_API_KEY")
            
            logger.info(f"使用Gemini LLM模型: {Config.LLM_MODEL}")
            return ChatOpenAI(
                openai_api_key=Config.GEMINI_API_KEY,
                openai_api_base=Config.GEMINI_API_BASE,
                temperature=0.1,
                model_name=Config.LLM_MODEL
            )
        elif provider == 'qwen':
            if not Config.QWEN_API_KEY:
                raise ValueError("使用Qwen LLM时必须设置QWEN_API_KEY")
            
            logger.info(f"使用Qwen LLM模型: {Config.LLM_MODEL}")
            return ChatOpenAI(
                openai_api_key=Config.QWEN_API_KEY,
                openai_api_base=Config.QWEN_API_BASE,
                temperature=0.1,
                model_name=Config.LLM_MODEL
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}，请使用 'gemini' 或 'qwen'")
    
    def _load_or_init_vector_store(self):
        """加载或初始化向量数据库"""
        try:
            index_path = Path(self.vector_db_path) / "index.faiss"
            
            if index_path.exists():
                # 加载现有的向量数据库
                logger.info("加载现有向量数据库")
                self.vector_store = FAISS.load_local(
                    self.vector_db_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                # 初始化新的向量数据库
                logger.info("初始化新的向量数据库")
                self.vector_store = FAISS.from_texts(
                    ["初始化文档"],
                    self.embeddings
                )
                # 保存初始向量数据库
                self.vector_store.save_local(self.vector_db_path)
        except Exception as e:
            logger.error(f"加载或初始化向量数据库时出错: {str(e)}")
            # 创建一个新的向量数据库
            self.vector_store = FAISS.from_texts(
                ["初始化文档"],
                self.embeddings
            )
    
    def _init_qa_chain(self):
        """初始化QA链"""
        try:
            # 自定义提示模板
            template = """使用以下上下文来回答问题。如果你不知道答案，就说你不知道，不要试图编造答案。
上下文信息：
{context}

问题：{question}

请基于提供的邮件上下文信息回答问题。如果上下文中没有相关信息，请明确说明。答案应该简洁明了，直接针对问题。
回答："""
            
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )
            
            # 使用新的LCEL语法创建检索QA链
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # 创建QA链
            self.qa_chain = {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough()
            } | prompt | self.llm | StrOutputParser()
            
            logger.info("QA链初始化完成")
        except Exception as e:
            logger.error(f"初始化QA链时出错: {str(e)}")
    
    def _format_docs(self, docs):
        """格式化文档用于提示"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def add_email_to_vector_store(self, email: Email) -> bool:
        """将邮件添加到向量数据库"""
        try:
            logger.info(f"添加邮件到向量数据库: {email.subject}")
            
            # 准备文档内容
            doc_content = self._prepare_email_document(email)
            
            # 创建文档
            doc = Document(
                page_content=doc_content['content'],
                metadata=doc_content['metadata']
            )
            
            # 分割文档
            docs = self.text_splitter.split_documents([doc])
            
            # 添加到向量数据库
            self.vector_store.add_documents(docs)
            
            # 保存向量数据库
            self.vector_store.save_local(self.vector_db_path)
            
            logger.info(f"邮件已成功添加到向量数据库: {email.subject}")
            return True
            
        except Exception as e:
            logger.error(f"添加邮件到向量数据库时出错: {str(e)}")
            return False
    
    def add_emails_to_vector_store(self, emails: List[Email]) -> int:
        """批量添加邮件到向量数据库"""
        try:
            logger.info(f"批量添加 {len(emails)} 封邮件到向量数据库")
            
            success_count = 0
            all_docs = []
            
            for email in emails:
                try:
                    # 准备文档内容
                    doc_content = self._prepare_email_document(email)
                    
                    # 创建文档
                    doc = Document(
                        page_content=doc_content['content'],
                        metadata=doc_content['metadata']
                    )
                    
                    # 分割文档
                    docs = self.text_splitter.split_documents([doc])
                    all_docs.extend(docs)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"处理邮件时出错: {email.subject}, 错误: {str(e)}")
                    continue
            
            # 批量添加到向量数据库
            if all_docs:
                self.vector_store.add_documents(all_docs)
                # 保存向量数据库
                self.vector_store.save_local(self.vector_db_path)
            
            logger.info(f"成功添加 {success_count} 封邮件到向量数据库")
            return success_count
            
        except Exception as e:
            logger.error(f"批量添加邮件到向量数据库时出错: {str(e)}")
            return 0
    
    def _prepare_email_document(self, email: Email) -> Dict[str, Any]:
        """准备邮件文档内容"""
        # 构建文档内容
        content = f"主题: {email.subject}\n"
        content += f"发件人: {email.sender}\n"
        content += f"日期: {email.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"重要性: {email.importance or '未知'}\n"
        content += f"类别: {email.category or '未知'}\n\n"
        
        # 添加邮件总结（如果有）
        if email.summary:
            content += f"总结: {email.summary}\n\n"
        
        # 添加关键信息（如果有）
        if email.key_info:
            content += "关键信息:\n"
            if email.key_info.get('key_points'):
                content += f"关键要点: {'; '.join(email.key_info['key_points'])}\n"
            if email.key_info.get('action_items'):
                content += f"行动项: {'; '.join(email.key_info['action_items'])}\n"
            if email.key_info.get('important_dates'):
                content += f"重要日期: {'; '.join(email.key_info['important_dates'])}\n"
            if email.key_info.get('contacts'):
                content += f"联系人: {'; '.join(email.key_info['contacts'])}\n"
            content += "\n"
        
        # 添加邮件正文
        content += f"正文: {email.body}"
        
        # 构建元数据
        metadata = {
            'email_id': email.id,
            'subject': email.subject,
            'sender': email.sender,
            'date': email.date.isoformat(),
            'importance': email.importance,
            'category': email.category,
            'recipients': ', '.join(email.recipients)
        }
        
        return {
            'content': content,
            'metadata': metadata
        }
    
    def search_emails(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """搜索相关邮件"""
        try:
            logger.info(f"搜索邮件，查询: {query}")
            
            # 使用相似性搜索
            docs = self.vector_store.similarity_search_with_score(query, k=k)
            
            # 格式化结果
            results = []
            for doc, score in docs:
                result = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score)
                }
                results.append(result)
            
            logger.info(f"找到 {len(results)} 条相关邮件")
            return results
            
        except Exception as e:
            logger.error(f"搜索邮件时出错: {str(e)}")
            return []
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """基于邮件内容回答问题"""
        try:
            logger.info(f"回答问题: {question}")
            
            # 首先获取相关文档
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            # 使用invoke方法获取相关文档
            source_docs = retriever.invoke(question)
            
            # 使用QA链回答问题
            answer = self.qa_chain.invoke(question)
            
            # 格式化源文档信息
            formatted_source_docs = []
            for doc in source_docs:
                formatted_source_docs.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata
                })
            
            # 构建响应
            response = {
                'answer': answer,
                'source_documents': formatted_source_docs
            }
            
            logger.info(f"问题回答完成")
            return response
            
        except Exception as e:
            logger.error(f"回答问题时出错: {str(e)}")
            return {
                'answer': f"回答问题时出错: {str(e)}",
                'source_documents': []
            }
    
    def get_email_statistics(self) -> Dict[str, Any]:
        """获取邮件统计信息"""
        try:
            # 这里可以实现更复杂的统计逻辑
            # 目前返回基本统计信息
            
            # 获取向量数据库中的文档数量
            doc_count = len(self.vector_store.docstore._dict)
            
            # 返回基本统计信息
            stats = {
                'total_emails': doc_count,
                'vector_db_path': self.vector_db_path,
                'last_updated': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取邮件统计信息时出错: {str(e)}")
            return {
                'total_emails': 0,
                'error': str(e)
            }
    
    def rebuild_vector_store(self, emails: List[Email]) -> bool:
        """重建向量数据库"""
        try:
            logger.info("开始重建向量数据库")
            
            # 创建新的向量数据库
            new_vector_store = FAISS.from_texts(
                ["初始化文档"],
                self.embeddings
            )
            
            # 添加所有邮件
            success_count = 0
            all_docs = []
            
            for email in emails:
                try:
                    # 准备文档内容
                    doc_content = self._prepare_email_document(email)
                    
                    # 创建文档
                    doc = Document(
                        page_content=doc_content['content'],
                        metadata=doc_content['metadata']
                    )
                    
                    # 分割文档
                    docs = self.text_splitter.split_documents([doc])
                    all_docs.extend(docs)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"处理邮件时出错: {email.subject}, 错误: {str(e)}")
                    continue
            
            # 批量添加到新向量数据库
            if all_docs:
                new_vector_store.add_documents(all_docs)
            
            # 替换现有向量数据库
            self.vector_store = new_vector_store
            
            # 保存向量数据库
            self.vector_store.save_local(self.vector_db_path)
            
            # 重新初始化QA链
            self._init_qa_chain()
            
            logger.info(f"向量数据库重建完成，成功添加 {success_count} 封邮件")
            return True
            
        except Exception as e:
            logger.error(f"重建向量数据库时出错: {str(e)}")
            return False