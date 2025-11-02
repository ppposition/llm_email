from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def create_app(email_system=None):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # 在实际应用中应该使用更安全的密钥
    
    # 启用CORS
    CORS(app)
    
    # 如果没有传入邮件系统实例，创建一个模拟对象
    if email_system is None:
        email_system = MockEmailSystem()
    
    # 健康检查路由
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'service': 'email-management-system'
        })
    
    # 邮件相关路由
    @app.route('/api/emails', methods=['GET'])
    def get_emails():
        """获取邮件列表"""
        try:
            # 获取查询参数
            limit = request.args.get('limit', 10, type=int)
            offset = request.args.get('offset', 0, type=int)
            importance = request.args.get('importance')
            category = request.args.get('category')
            
            # 这里应该从数据库中获取邮件列表
            # 由于我们没有实现数据库，返回模拟数据
            emails = email_system.get_emails(limit, offset, importance, category)
            
            return jsonify({
                'success': True,
                'data': emails,
                'total': len(emails)
            })
        except Exception as e:
            logger.error(f"获取邮件列表时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/emails/<email_id>', methods=['GET'])
    def get_email(email_id):
        """获取单封邮件详情"""
        try:
            email = email_system.get_email_by_id(email_id)
            
            if email:
                return jsonify({
                    'success': True,
                    'data': email
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '邮件不存在'
                }), 404
        except Exception as e:
            logger.error(f"获取邮件详情时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # RAG相关路由
    @app.route('/api/search', methods=['POST'])
    def search_emails():
        """搜索邮件"""
        try:
            data = request.get_json()
            query = data.get('query', '')
            k = data.get('k', 5)
            
            if not query:
                return jsonify({
                    'success': False,
                    'error': '查询内容不能为空'
                }), 400
            
            # 搜索邮件
            results = email_system.search_emails(query, k)
            
            return jsonify({
                'success': True,
                'data': results
            })
        except Exception as e:
            logger.error(f"搜索邮件时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/ask', methods=['POST'])
    def ask_question():
        """基于邮件内容回答问题"""
        try:
            data = request.get_json()
            question = data.get('question', '')
            
            if not question:
                return jsonify({
                    'success': False,
                    'error': '问题不能为空'
                }), 400
            
            # 回答问题
            result = email_system.ask_question(question)
            
            return jsonify({
                'success': True,
                'data': result
            })
        except Exception as e:
            logger.error(f"回答问题时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # 统计相关路由
    @app.route('/api/statistics', methods=['GET'])
    def get_statistics():
        """获取邮件统计信息"""
        try:
            stats = email_system.get_email_statistics()
            
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            logger.error(f"获取统计信息时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # 系统管理路由
    @app.route('/api/system/test-notification', methods=['POST'])
    def test_notification():
        """测试通知功能"""
        try:
            success = email_system.test_notification()
            
            return jsonify({
                'success': True,
                'data': {
                    'notification_test': success
                }
            })
        except Exception as e:
            logger.error(f"测试通知功能时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/system/rebuild-index', methods=['POST'])
    def rebuild_index():
        """重建向量数据库索引"""
        try:
            success = email_system.rebuild_vector_store()
            
            return jsonify({
                'success': True,
                'data': {
                    'rebuild_success': success
                }
            })
        except Exception as e:
            logger.error(f"重建索引时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '接口不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500
    
    return app

class MockEmailSystem:
    """模拟邮件系统类，用于API测试"""
    
    def get_emails(self, limit=10, offset=0, importance=None, category=None):
        """获取邮件列表（模拟数据）"""
        # 这里返回模拟数据
        mock_emails = [
            {
                'id': '1',
                'subject': '测试邮件1',
                'sender': 'test1@example.com',
                'recipients': ['user@example.com'],
                'date': datetime.now().isoformat(),
                'body': '这是一封测试邮件的内容。',
                'importance': 'high',
                'category': 'work',
                'summary': '这是一封测试邮件的总结。'
            },
            {
                'id': '2',
                'subject': '测试邮件2',
                'sender': 'test2@example.com',
                'recipients': ['user@example.com'],
                'date': datetime.now().isoformat(),
                'body': '这是另一封测试邮件的内容。',
                'importance': 'medium',
                'category': 'personal',
                'summary': '这是另一封测试邮件的总结。'
            }
        ]
        
        # 应用过滤条件
        if importance:
            mock_emails = [e for e in mock_emails if e.get('importance') == importance]
        
        if category:
            mock_emails = [e for e in mock_emails if e.get('category') == category]
        
        # 应用分页
        start = offset
        end = start + limit
        return mock_emails[start:end]
    
    def get_email_by_id(self, email_id):
        """根据ID获取邮件（模拟数据）"""
        mock_emails = {
            '1': {
                'id': '1',
                'subject': '测试邮件1',
                'sender': 'test1@example.com',
                'recipients': ['user@example.com'],
                'date': datetime.now().isoformat(),
                'body': '这是一封测试邮件的内容。',
                'html_body': '<p>这是一封测试邮件的内容。</p>',
                'importance': 'high',
                'category': 'work',
                'summary': '这是一封测试邮件的总结。',
                'key_info': {
                    'key_points': ['这是一个关键点'],
                    'action_items': ['这是一个行动项'],
                    'important_dates': ['2023-01-01'],
                    'contacts': ['test1@example.com']
                }
            },
            '2': {
                'id': '2',
                'subject': '测试邮件2',
                'sender': 'test2@example.com',
                'recipients': ['user@example.com'],
                'date': datetime.now().isoformat(),
                'body': '这是另一封测试邮件的内容。',
                'html_body': '<p>这是另一封测试邮件的内容。</p>',
                'importance': 'medium',
                'category': 'personal',
                'summary': '这是另一封测试邮件的总结。',
                'key_info': {
                    'key_points': ['这是另一个关键点'],
                    'action_items': [],
                    'important_dates': [],
                    'contacts': ['test2@example.com']
                }
            }
        }
        
        return mock_emails.get(email_id)
    
    def search_emails(self, query, k=5):
        """搜索邮件（模拟数据）"""
        # 这里返回模拟数据
        return [
            {
                'content': f'搜索结果: {query}',
                'metadata': {
                    'email_id': '1',
                    'subject': '测试邮件1',
                    'sender': 'test1@example.com'
                },
                'score': 0.9
            }
        ]
    
    def ask_question(self, question):
        """回答问题（模拟数据）"""
        # 这里返回模拟数据
        return {
            'answer': f'这是对问题 "{question}" 的模拟回答。',
            'source_documents': [
                {
                    'content': '这是源文档的内容。',
                    'metadata': {
                        'email_id': '1',
                        'subject': '测试邮件1'
                    }
                }
            ]
        }
    
    def get_email_statistics(self):
        """获取邮件统计信息（模拟数据）"""
        # 这里返回模拟数据
        return {
            'total_emails': 100,
            'by_importance': {
                'high': 20,
                'medium': 50,
                'low': 30
            },
            'by_category': {
                'work': 40,
                'personal': 30,
                'advertisement': 20,
                'other': 10
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def test_notification(self):
        """测试通知功能（模拟数据）"""
        # 这里返回模拟数据
        return True
    
    def rebuild_vector_store(self):
        """重建向量数据库（模拟数据）"""
        # 这里返回模拟数据
        return True