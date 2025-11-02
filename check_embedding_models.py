#!/usr/bin/env python3
"""
检查可用的embedding模型的工具
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json

# 加载环境变量
load_dotenv()

def check_qwen_models():
    """检查Qwen API可用的embedding模型"""
    api_key = os.getenv('QWEN_API_KEY')
    api_base = os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    
    if not api_key:
        print("❌ 错误: 未找到 QWEN_API_KEY 环境变量")
        return False
    
    print(f"🔍 检查 API 端点: {api_base}")
    print(f"🔑 使用 API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
    print()
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # 获取可用模型列表
        models_url = f"{api_base}/models"
        print(f"📡 请求模型列表: {models_url}")
        
        response = requests.get(models_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            models_data = response.json()
            embedding_models = []
            
            # 筛选embedding模型
            if 'data' in models_data:
                for model in models_data['data']:
                    model_id = model.get('id', '')
                    if 'embed' in model_id.lower():
                        embedding_models.append({
                            'id': model_id,
                            'object': model.get('object', ''),
                            'created': model.get('created', ''),
                            'owned_by': model.get('owned_by', '')
                        })
            
            if embedding_models:
                print("✅ 找到以下 embedding 模型:")
                print("-" * 80)
                for i, model in enumerate(embedding_models, 1):
                    print(f"{i}. 模型ID: {model['id']}")
                    print(f"   类型: {model['object']}")
                    print(f"   所有者: {model['owned_by']}")
                    if model['created']:
                        print(f"   创建时间: {model['created']}")
                    print()
            else:
                print("⚠️  未找到专门的 embedding 模型")
                print("可用的所有模型:")
                if 'data' in models_data:
                    for i, model in enumerate(models_data['data'][:10], 1):  # 只显示前10个
                        print(f"{i}. {model.get('id', 'Unknown')}")
                    if len(models_data['data']) > 10:
                        print(f"... 还有 {len(models_data['data']) - 10} 个模型")
                
                # 建议常用的embedding模型
                print("\n💡 常用的embedding模型名称:")
                print("- text-embedding-3-small")
                print("- text-embedding-3-large")
                print("- text-embedding-ada-002")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求错误: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False
    
    return True

def test_embedding_model(model_name="text-embedding-3-small"):
    """测试指定的embedding模型"""
    api_key = os.getenv('QWEN_API_KEY')
    api_base = os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    
    if not api_key:
        print("❌ 错误: 未找到 QWEN_API_KEY 环境变量")
        return False
    
    print(f"\n🧪 测试 embedding 模型: {model_name}")
    print("-" * 50)
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试数据
    test_data = {
        "input": "这是一个测试文本，用于检查embedding模型是否正常工作。",
        "model": model_name
    }
    
    try:
        embeddings_url = f"{api_base}/embeddings"
        response = requests.post(embeddings_url, headers=headers, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                embedding = result['data'][0]['embedding']
                print(f"✅ 模型 {model_name} 测试成功!")
                print(f"📊 向量维度: {len(embedding)}")
                print(f"💰 使用信息: {result.get('usage', {})}")
                return True
            else:
                print(f"❌ 响应格式异常: {result}")
                return False
        else:
            print(f"❌ 测试失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("🔍 Embedding 模型检查工具")
    print("=" * 60)
    print()
    
    # 检查配置
    print("📋 当前配置:")
    print(f"   API Base: {os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')}")
    print(f"   API Key: {'已设置' if os.getenv('QWEN_API_KEY') else '未设置'}")
    print(f"   LLM Model: {os.getenv('LLM_MODEL', 'z-ai/glm-4.6')}")
    print()
    
    # 检查可用模型
    if check_qwen_models():
        print("\n" + "=" * 60)
        
        # 测试当前使用的模型
        current_model = "text-embedding-3-small"  # 从rag_service.py中看到的默认模型
        test_embedding_model(current_model)
        
        print("\n" + "=" * 60)
        print("💡 使用说明:")
        print("1. 如果看到可用的embedding模型列表，说明API连接正常")
        print("2. 可以在 .env 文件中设置 EMBEDDING_MODEL 变量来指定模型")
        print("3. 修改 src/services/rag_service.py 中的 model 参数来使用不同的模型")
        print()
        print("📝 建议的配置更新:")
        print("在 .env 文件中添加:")
        print("EMBEDDING_MODEL=text-embedding-3-small")
        print()
        print("在 config.py 中添加:")
        print("EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')")
        print()
        print("在 rag_service.py 中修改:")
        print("model=Config.EMBEDDING_MODEL")
    else:
        print("\n❌ 无法连接到API服务，请检查配置")
        print("🔧 请检查以下配置项:")
        print("1. QWEN_API_KEY 是否正确设置")
        print("2. QWEN_API_BASE 是否可访问")
        print("3. 网络连接是否正常")

if __name__ == "__main__":
    main()