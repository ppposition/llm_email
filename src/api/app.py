from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from typing import Dict, Any, List
from .mock_system import MockEmailSystem

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
    
    # 邮件发送路由
    @app.route('/api/emails/send', methods=['POST'])
    def send_email():
        """发送邮件"""
        try:
            data = request.get_json()
            to_emails = data.get('to_emails', [])
            subject = data.get('subject', '')
            content = data.get('content', '')
            content_type = data.get('content_type', 'plain')
            attachments = data.get('attachments', [])
            
            if not to_emails or not subject or not content:
                return jsonify({
                    'success': False,
                    'error': '收件人、主题和内容不能为空'
                }), 400
            
            # 发送邮件
            success = email_system.qq_email_client.send_email(
                to_emails=to_emails,
                subject=subject,
                content=content,
                content_type=content_type,
                attachments=attachments
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'send_success': success
                }
            })
        except Exception as e:
            logger.error(f"发送邮件时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # 邮件文件夹路由
    @app.route('/api/emails/folders', methods=['GET'])
    def get_email_folders():
        """获取邮件文件夹列表"""
        try:
            folders = email_system.qq_email_client.get_folders()
            
            return jsonify({
                'success': True,
                'data': folders
            })
        except Exception as e:
            logger.error(f"获取邮件文件夹时出错: {str(e)}")
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