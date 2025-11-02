#!/usr/bin/env python3
"""
邮箱连接诊断脚本
用于诊断邮箱连接问题并提供解决方案
"""

import imaplib
import smtplib
import socket
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_dns_resolution(server, port):
    """测试DNS解析"""
    try:
        print(f"测试DNS解析: {server}:{port}")
        ip = socket.gethostbyname(server)
        print(f"✓ DNS解析成功: {server} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"✗ DNS解析失败: {server} - {str(e)}")
        return False

def test_port_connectivity(server, port):
    """测试端口连通性"""
    try:
        print(f"测试端口连通性: {server}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((server, port))
        sock.close()
        
        if result == 0:
            print(f"✓ 端口 {port} 连接成功")
            return True
        else:
            print(f"✗ 端口 {port} 连接失败 (错误代码: {result})")
            return False
    except Exception as e:
        print(f"✗ 端口测试出错: {str(e)}")
        return False

def test_imap_connection(server, port, email, password):
    """测试IMAP连接"""
    try:
        print(f"测试IMAP连接: {email}")
        
        # 创建IMAP连接
        imap = imaplib.IMAP4_SSL(server, port)
        
        # 尝试登录
        try:
            imap.login(email, password)
            print("✓ IMAP登录成功")
            
            # 获取文件夹列表
            status, folders = imap.list()
            if status == 'OK':
                print(f"✓ 找到 {len(folders)} 个文件夹")
            
            imap.logout()
            return True
            
        except imaplib.IMAP4.error as e:
            error_msg = str(e).lower()
            if "authentication failed" in error_msg or "login failed" in error_msg:
                print("✗ IMAP认证失败 - 可能需要使用授权码而不是密码")
                print("  QQ邮箱需要开启IMAP服务并使用授权码")
                print("  请访问: https://mail.qq.com/ -> 设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务")
            else:
                print(f"✗ IMAP登录失败: {str(e)}")
            return False
            
    except Exception as e:
        print(f"✗ IMAP连接出错: {str(e)}")
        return False

def test_smtp_connection(server, port, email, password):
    """测试SMTP连接"""
    try:
        print(f"测试SMTP连接: {email}")
        
        # 创建SMTP连接
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        
        # 尝试登录
        try:
            smtp.login(email, password)
            print("✓ SMTP登录成功")
            smtp.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print("✗ SMTP认证失败 - 可能需要使用授权码而不是密码")
            return False
            
    except Exception as e:
        print(f"✗ SMTP连接出错: {str(e)}")
        return False

def diagnose_qq_email():
    """诊断QQ邮箱配置"""
    print("=== QQ邮箱配置诊断 ===")
    print()
    
    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')
    imap_server = os.getenv('IMAP_SERVER')
    imap_port = int(os.getenv('IMAP_PORT', 993))
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    
    print(f"邮箱地址: {email}")
    print(f"IMAP服务器: {imap_server}:{imap_port}")
    print(f"SMTP服务器: {smtp_server}:{smtp_port}")
    print()
    
    # 检查是否是QQ邮箱
    if email and '@qq.com' in email:
        print("检测到QQ邮箱，使用以下配置:")
        print("IMAP服务器: imap.qq.com")
        print("SMTP服务器: smtp.qq.com")
        print("IMAP端口: 993 (SSL)")
        print("SMTP端口: 587 (TLS)")
        print()
        print("重要提示:")
        print("1. QQ邮箱需要开启IMAP/SMTP服务")
        print("2. 需要使用授权码而不是密码")
        print("3. 请访问 https://mail.qq.com/ 进行设置")
        print()
    
    # 测试DNS解析
    dns_ok = True
    dns_ok &= test_dns_resolution(imap_server, imap_port)
    if smtp_server != smtp_server:  # 避免重复测试相同服务器
        dns_ok &= test_dns_resolution(smtp_server, smtp_port)
    
    if not dns_ok:
        print("\nDNS解析失败，请检查服务器地址是否正确")
        return False
    
    print()
    
    # 测试端口连通性
    port_ok = True
    port_ok &= test_port_connectivity(imap_server, imap_port)
    if smtp_server != imap_server or smtp_port != imap_port:
        port_ok &= test_port_connectivity(smtp_server, smtp_port)
    
    if not port_ok:
        print("\n端口连接失败，请检查:")
        print("1. 服务器地址是否正确")
        print("2. 端口号是否正确")
        print("3. 网络连接是否正常")
        print("4. 防火墙是否阻止连接")
        return False
    
    print()
    
    # 测试IMAP连接
    imap_ok = test_imap_connection(imap_server, imap_port, email, password)
    
    # 测试SMTP连接
    smtp_ok = test_smtp_connection(smtp_server, smtp_port, email, password)
    
    print()
    print("=== 诊断结果 ===")
    print(f"DNS解析: {'✓' if dns_ok else '✗'}")
    print(f"端口连通: {'✓' if port_ok else '✗'}")
    print(f"IMAP连接: {'✓' if imap_ok else '✗'}")
    print(f"SMTP连接: {'✓' if smtp_ok else '✗'}")
    
    if imap_ok and smtp_ok:
        print("\n🎉 邮箱配置完全正常！")
        return True
    else:
        print("\n⚠ 邮箱配置存在问题，请根据上述提示进行修复")
        return False

def main():
    """主函数"""
    print("邮箱连接诊断工具")
    print("=" * 50)
    
    if not os.getenv('EMAIL_ADDRESS'):
        print("错误: 未配置邮箱地址 (EMAIL_ADDRESS)")
        return 1
    
    if not os.getenv('EMAIL_PASSWORD'):
        print("错误: 未配置邮箱密码/授权码 (EMAIL_PASSWORD)")
        return 1
    
    if not os.getenv('IMAP_SERVER'):
        print("错误: 未配置IMAP服务器 (IMAP_SERVER)")
        return 1
    
    # 诊断邮箱连接
    success = diagnose_qq_email()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())