#!/usr/bin/env python3
"""
配置测试脚本
用于验证邮箱管理系统的配置是否正确
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from src.services.email_receiver import EmailReceiver
from src.services.email_processor import EmailProcessor
from src.services.rag_service import RAGService
from src.services.notification_service import NotificationService

def test_config():
    """测试配置是否正确"""
    print("=== 配置测试 ===")
    
    try:
        # 验证配置
        Config.validate_config()
        print("✓ 配置验证通过")
    except ValueError as e:
        print(f"✗ 配置验证失败: {str(e)}")
        return False
    
    # 显示当前配置
    print(f"✓ 邮箱地址: {Config.EMAIL_ADDRESS}")
    print(f"✓ IMAP服务器: {Config.IMAP_SERVER}:{Config.IMAP_PORT}")
    print(f"✓ LLM提供商: {Config.LLM_PROVIDER}")
    print(f"✓ Embedding提供商: {Config.EMBEDDING_PROVIDER}")
    print(f"✓ 使用的模型: {Config.LLM_MODEL}")
    print(f"✓ 向量数据库路径: {Config.VECTOR_DB_PATH}")
    print(f"✓ 邮件检查间隔: {Config.EMAIL_CHECK_INTERVAL}秒")
    
    if Config.NOTIFICATION_EMAIL:
        print(f"✓ 通知邮箱: {Config.NOTIFICATION_EMAIL}")
        print(f"✓ SMTP服务器: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
    else:
        print("⚠ 通知功能未配置")
    
    return True

def test_email_connection():
    """测试邮件连接"""
    print("\n=== 邮件连接测试 ===")
    
    try:
        receiver = EmailReceiver()
        if receiver.connect():
            print("✓ 邮件连接成功")
            
            # 获取文件夹列表
            folders = receiver.get_email_folders()
            print(f"✓ 找到 {len(folders)} 个文件夹: {', '.join(folders[:5])}")
            
            receiver.disconnect()
            return True
        else:
            print("✗ 邮件连接失败")
            return False
    except Exception as e:
        print(f"✗ 邮件连接测试出错: {str(e)}")
        return False

def test_llm_connection():
    """测试LLM连接"""
    print("\n=== LLM连接测试 ===")
    
    try:
        processor = EmailProcessor()
        print("✓ LLM初始化成功")
        print(f"✓ 使用模型: {Config.LLM_MODEL}")
        
        # 简单测试
        test_content = "这是一封测试邮件，内容是关于明天下午3点的会议。"
        result = processor._summarize_email(test_content)
        
        if result:
            print("✓ LLM调用测试成功")
            print(f"✓ 测试结果: {result.get('summary', '无总结')[:50]}...")
        else:
            print("⚠ LLM调用测试失败，但初始化成功")
        
        return True
    except Exception as e:
        print(f"✗ LLM连接测试出错: {str(e)}")
        return False

def test_rag_service():
    """测试RAG服务"""
    print("\n=== RAG服务测试 ===")
    
    try:
        rag_service = RAGService()
        print("✓ RAG服务初始化成功")
        
        # 获取统计信息
        stats = rag_service.get_email_statistics()
        print(f"✓ 当前邮件数量: {stats.get('total_emails', 0)}")
        
        return True
    except Exception as e:
        print(f"✗ RAG服务测试出错: {str(e)}")
        return False

def test_notification_service():
    """测试通知服务"""
    print("\n=== 通知服务测试 ===")
    
    try:
        notification_service = NotificationService()
        
        if notification_service.is_notification_enabled():
            print("✓ 通知服务已启用")
            
            # 询问用户是否要发送测试通知
            response = input("是否要发送测试通知邮件？(y/n): ").lower().strip()
            if response == 'y':
                success = notification_service.test_notification()
                if success:
                    print("✓ 测试通知发送成功")
                else:
                    print("✗ 测试通知发送失败")
            
            return True
        else:
            print("⚠ 通知服务未启用")
            return True
    except Exception as e:
        print(f"✗ 通知服务测试出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("邮箱管理系统配置测试")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 运行测试
    tests = [
        ("配置测试", test_config),
        ("邮件连接测试", test_email_connection),
        ("LLM连接测试", test_llm_connection),
        ("RAG服务测试", test_rag_service),
        ("通知服务测试", test_notification_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print(f"\n用户中断了 {test_name}")
            break
        except Exception as e:
            print(f"✗ {test_name} 出现未知错误: {str(e)}")
            results.append((test_name, False))
    
    # 显示测试结果汇总
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！系统配置正确。")
        return 0
    else:
        print("⚠ 部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())