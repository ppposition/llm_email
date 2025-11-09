#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ邮箱系统使用示例
展示如何使用整合后的QQ邮箱收发系统
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.qq_email_client import QQEmailClient
from src.services.email_receiver import EmailReceiver
from src.services.email_processor import EmailProcessor
from src.services.notification_service import NotificationService
from src.services.rag_service import RAGService
from main import EmailManagementSystem

def send_email_example():
    """发送邮件示例"""
    print("=== 发送邮件示例 ===")
    
    # 创建QQ邮箱客户端
    client = QQEmailClient()
    
    # 检查配置
    if not client.qq_email or not client.auth_code:
        print("错误：请先在.env文件中配置您的QQ邮箱和授权码！")
        return False
    
    # 发件人和收件人
    to_email = "recipient@example.com"  # 替换为实际的收件人邮箱
    
    # 发送纯文本邮件
    subject = f"测试邮件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    content = f"""
    这是一封测试邮件。
    
    发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    发送者: {client.qq_email}
    
    此邮件由Python程序自动发送。
    """
    
    print(f"正在发送邮件到: {to_email}")
    success = client.send_email([to_email], subject, content)
    print(f"发送结果: {'成功' if success else '失败'}")
    
    return success

def receive_email_example():
    """接收邮件示例"""
    print("\n=== 接收邮件示例 ===")
    
    # 创建邮件接收器
    receiver = EmailReceiver()
    
    # 连接到邮箱
    if not receiver.connect():
        print("连接邮箱失败")
        return []
    
    try:
        # 接收最新的5封邮件
        print("正在接收最新邮件...")
        emails = receiver.get_new_emails(limit=5)
        
        if not emails:
            print("没有找到新邮件")
            return []
        
        print(f"找到 {len(emails)} 封邮件:")
        
        for i, email in enumerate(emails, 1):
            print(f"\n--- 邮件 {i} ---")
            print(f"主题: {email.subject}")
            print(f"发件人: {email.sender}")
            print(f"收件人: {', '.join(email.recipients)}")
            print(f"日期: {email.date}")
            
            # 显示正文预览
            body_preview = email.body[:100] + "..." if len(email.body) > 100 else email.body
            print(f"正文预览: {body_preview}")
            
            # 显示附件信息
            if email.attachments:
                print(f"附件: {[att.filename for att in email.attachments]}")
        
        return emails
        
    finally:
        # 断开连接
        receiver.disconnect()

def process_email_example():
    """处理邮件示例"""
    print("\n=== 处理邮件示例 ===")
    
    # 创建邮件处理器
    processor = EmailProcessor()
    
    # 创建邮件接收器
    receiver = EmailReceiver()
    
    # 连接到邮箱
    if not receiver.connect():
        print("连接邮箱失败")
        return
    
    try:
        # 接收最新的3封邮件
        print("正在接收邮件进行处理...")
        emails = receiver.get_new_emails(limit=3)
        
        if not emails:
            print("没有找到邮件进行处理")
            return
        
        print(f"正在处理 {len(emails)} 封邮件...")
        
        # 处理邮件
        processed_emails = processor.batch_process_emails(emails)
        
        # 显示处理结果
        for i, email in enumerate(processed_emails, 1):
            print(f"\n--- 处理结果 {i} ---")
            print(f"主题: {email.subject}")
            print(f"重要性: {email.importance}")
            print(f"类别: {email.category}")
            
            if email.summary:
                print(f"总结: {email.summary}")
            
            if email.key_info:
                if email.key_info.get('key_points'):
                    print(f"关键要点: {'; '.join(email.key_info['key_points'])}")
                if email.key_info.get('action_items'):
                    print(f"行动项: {'; '.join(email.key_info['action_items'])}")
        
    finally:
        # 断开连接
        receiver.disconnect()

def notification_example():
    """通知服务示例"""
    print("\n=== 通知服务示例 ===")
    
    # 创建通知服务
    notification_service = NotificationService()
    
    # 检查通知功能是否启用
    if not notification_service.is_notification_enabled():
        print("通知功能未启用，请检查配置")
        return
    
    # 测试通知功能
    print("正在测试通知功能...")
    success = notification_service.test_notification()
    print(f"通知功能测试: {'成功' if success else '失败'}")
    
    # 发送系统通知
    print("正在发送系统通知...")
    success = notification_service.send_system_notification(
        "测试系统通知",
        "这是一条测试系统通知，用于验证通知功能是否正常工作。"
    )
    print(f"系统通知发送: {'成功' if success else '失败'}")

def rag_service_example():
    """RAG服务示例"""
    print("\n=== RAG服务示例 ===")
    
    # 创建RAG服务
    rag_service = RAGService()
    
    # 获取邮件统计信息
    print("正在获取邮件统计信息...")
    stats = rag_service.get_email_statistics()
    print(f"邮件统计: {stats}")
    
    # 搜索邮件（如果有数据）
    print("正在搜索邮件...")
    results = rag_service.search_emails("测试", k=3)
    print(f"搜索结果: {results}")

def full_system_example():
    """完整系统示例"""
    print("\n=== 完整系统示例 ===")
    
    # 创建邮箱管理系统
    try:
        email_system = EmailManagementSystem()
        
        # 测试系统功能
        print("正在测试系统功能...")
        email_system.test_system()
        
        # 启动系统（这会启动Web API和邮件检查循环）
        print("正在启动邮箱管理系统...")
        print("Web API将在 http://localhost:5000 启动")
        print("按 Ctrl+C 停止系统")
        
        # 注意：这里会阻塞，直到用户中断
        # email_system.start()
        
        print("系统启动示例完成（实际启动已注释）")
        
    except Exception as e:
        print(f"系统启动失败: {str(e)}")

def interactive_mode():
    """交互模式"""
    print("\n=== 交互模式 ===")
    print("1. 发送邮件")
    print("2. 接收邮件")
    print("3. 处理邮件")
    print("4. 测试通知功能")
    print("5. RAG服务示例")
    print("6. 完整系统示例")
    print("7. 退出")
    
    while True:
        choice = input("\n请选择操作 (1-7): ").strip()
        
        if choice == "1":
            send_email_example()
        elif choice == "2":
            receive_email_example()
        elif choice == "3":
            process_email_example()
        elif choice == "4":
            notification_example()
        elif choice == "5":
            rag_service_example()
        elif choice == "6":
            full_system_example()
        elif choice == "7":
            print("退出程序")
            break
        else:
            print("无效选择，请重新输入")

def main():
    """主函数"""
    print("QQ邮箱系统示例程序")
    print("=" * 50)
    
    # 检查配置
    try:
        from config import Config
        if not Config.EMAIL_ADDRESS or not Config.EMAIL_PASSWORD:
            print("警告：请先在.env文件中配置您的QQ邮箱和授权码！")
            print()
    except ImportError:
        print("错误：找不到config.py配置文件！")
        return
    
    # 运行示例
    try:
        mode = input("选择模式 (1-自动示例, 2-交互模式): ").strip()
        
        if mode == "1":
            # 自动运行示例
            send_email_example()
            receive_email_example()
            process_email_example()
            notification_example()
            rag_service_example()
            full_system_example()
        elif mode == "2":
            # 交互模式
            interactive_mode()
        else:
            print("无效选择，运行自动示例")
            send_email_example()
            receive_email_example()
            process_email_example()
            notification_example()
            rag_service_example()
            full_system_example()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    main()