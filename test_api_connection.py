#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 OpenAI API 连接和模型可用性
"""

import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_gemini_api():
    """测试 Gemini API 连接"""
    
    # 从环境变量获取配置
    api_key = os.getenv('GEMINI_API_KEY')
    api_base = os.getenv('GEMINI_API_BASE')
    model = os.getenv('LLM_MODEL')
    
    print("=== API 配置信息 ===")
    print(f"API Base: {api_base}")
    print(f"Model: {model}")
    print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")
    print()
    
    if not api_key or not api_base or not model:
        print("❌ 错误: 缺少必要的配置信息")
        return False
    
    # 构建请求
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "你好，你是谁"
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    print("=== 发送 API 请求 ===")
    print(f"URL: {url}")
    print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        print("正在发送请求...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 连接成功!")
            print("=== 响应内容 ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 提取回复内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"\n模型回复: {content}")
            
            return True
        else:
            print("❌ API 请求失败!")
            print(f"状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ 响应解析失败: {e}")
        print(f"原始响应: {response.text}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_model_info():
    """测试获取模型信息"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    api_base = os.getenv('GEMINI_API_BASE')
    
    if not api_key or not api_base:
        print("❌ 缺少 API 配置")
        return False
    
    # 尝试获取模型列表
    url = f"{api_base}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("\n=== 获取模型列表 ===")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ 成功获取模型列表")
            
            if 'data' in models:
                print("可用模型:")
                for model_info in models['data'][:10]:  # 只显示前10个模型
                    print(f"  - {model_info.get('id', 'Unknown')}")
                
                if len(models['data']) > 10:
                    print(f"  ... 还有 {len(models['data']) - 10} 个模型")
            
            return True
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 获取模型列表异常: {e}")
        return False

if __name__ == "__main__":
    print("开始测试 OpenAI API 配置...")
    print("=" * 50)
    
    # 测试模型信息
    test_model_info()
    
    print("\n" + "=" * 50)
    
    # 测试基本对话
    success = test_gemini_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成! API 配置正常工作。")
    else:
        print("⚠️  测试失败! 请检查配置。")