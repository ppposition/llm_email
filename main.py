#!/usr/bin/env python3
"""
邮箱管理系统主程序
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from src.services.email_receiver import EmailReceiver
from src.services.email_processor import EmailProcessor
from src.services.rag_service import RAGService
from src.services.notification_service import NotificationService
from src.services.school_email_client import SchoolEmailClient

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailManagementSystem:
    """邮箱管理系统主类"""
    
    def __init__(self):
        """初始化邮箱管理系统"""
        logger.info("初始化邮箱管理系统")
        
        # 验证配置
        try:
            Config.validate_config()
            logger.info("配置验证通过")
        except ValueError as e:
            logger.error(f"配置验证失败: {str(e)}")
            sys.exit(1)
        
        # 初始化服务
        self.email_receiver = EmailReceiver()
        self.email_processor = EmailProcessor()
        self.rag_service = RAGService()
        self.notification_service = NotificationService()
        self.school_email_client = SchoolEmailClient()  # 添加学校邮箱客户端
        
        # 控制变量
        self.running = False
        self.email_check_thread = None
        
        # 创建数据目录
        self._create_data_directories()
        
        logger.info("邮箱管理系统初始化完成")
    
    def _create_data_directories(self):
        """创建必要的数据目录"""
        directories = [
            Config.VECTOR_DB_PATH,
            './logs',
            './data'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {directory}")
    
    def start(self):
        """启动邮箱管理系统"""
        logger.info("启动邮箱管理系统")
        
        # 设置运行标志
        self.running = True
        
        # 启动邮件检查线程
        self.email_check_thread = threading.Thread(target=self._email_check_loop)
        self.email_check_thread.daemon = True
        self.email_check_thread.start()
        
        logger.info("系统启动完成，邮件检查服务已运行")
    
    def stop(self):
        """停止邮箱管理系统"""
        logger.info("停止邮箱管理系统")
        
        # 设置运行标志
        self.running = False
        
        # 等待邮件检查线程结束
        if self.email_check_thread and self.email_check_thread.is_alive():
            self.email_check_thread.join(timeout=5)
        
        # 断开邮件接收器连接
        self.email_receiver.disconnect()
        
        logger.info("邮箱管理系统已停止")
    
    def _email_check_loop(self):
        """邮件检查循环"""
        logger.info("启动邮件检查循环")
        
        while self.running:
            try:
                # 检查新邮件
                self._check_and_process_emails()
                
                # 等待下一次检查
                time.sleep(Config.EMAIL_CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("收到中断信号，停止邮件检查")
                break
            except Exception as e:
                logger.error(f"邮件检查循环出错: {str(e)}")
                # 发送错误通知
                self.notification_service.send_error_notification(
                    f"邮件检查循环出错: {str(e)}",
                    {"time": datetime.now().isoformat()}
                )
                # 等待一段时间后继续
                time.sleep(60)
        
        logger.info("邮件检查循环已停止")
    
    def _check_and_process_emails(self):
        """检查并处理新邮件"""
        try:
            logger.info("检查新邮件")
            
            # 获取新邮件
            new_emails = self.email_receiver.get_new_emails()
            
            if not new_emails:
                logger.info("没有新邮件")
                return
            
            logger.info(f"找到 {len(new_emails)} 封新邮件")
            
            # 处理邮件
            processed_emails = self.email_processor.batch_process_emails(new_emails)
            
            # 添加到RAG系统
            self.rag_service.add_emails_to_vector_store(processed_emails)
            
            # 检查重要邮件并发送通知
            important_emails = [
                email for email in processed_emails 
                if email.importance == 'high'
            ]
            
            if important_emails:
                logger.info(f"发现 {len(important_emails)} 封重要邮件")
                self.notification_service.send_batch_important_email_notification(important_emails)
            
            logger.info(f"邮件处理完成，共处理 {len(processed_emails)} 封邮件")
            
        except Exception as e:
            logger.error(f"检查并处理邮件时出错: {str(e)}")
            # 发送错误通知
            self.notification_service.send_error_notification(
                f"检查并处理邮件时出错: {str(e)}",
                {"time": datetime.now().isoformat()}
            )
    
    
    def test_system(self):
        """测试系统功能"""
        logger.info("开始测试系统功能")
        
        try:
            # 测试邮件接收
            logger.info("测试邮件接收功能")
            if self.email_receiver.connect():
                logger.info("邮件接收功能测试成功")
                self.email_receiver.disconnect()
            else:
                logger.error("邮件接收功能测试失败")
            
            # 测试通知功能
            logger.info("测试通知功能")
            if self.notification_service.test_notification():
                logger.info("通知功能测试成功")
            else:
                logger.warning("通知功能测试失败")
            
            # 测试RAG功能
            logger.info("测试RAG功能")
            stats = self.rag_service.get_email_statistics()
            logger.info(f"RAG统计信息: {stats}")
            
            logger.info("系统功能测试完成")
            
        except Exception as e:
            logger.error(f"测试系统功能时出错: {str(e)}")

def main():
    """主函数"""
    try:
        # 创建邮箱管理系统
        email_system = EmailManagementSystem()
        
        # 测试系统功能
        email_system.test_system()
        
        # 启动系统
        email_system.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止系统")
        if 'email_system' in locals():
            email_system.stop()
    except Exception as e:
        logger.error(f"系统运行时出错: {str(e)}")
        if 'email_system' in locals():
            email_system.notification_service.send_error_notification(
                f"系统运行时出错: {str(e)}",
                {"time": datetime.now().isoformat()}
            )
        sys.exit(1)

if __name__ == "__main__":
    main()