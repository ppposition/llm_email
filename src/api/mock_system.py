from datetime import datetime
from typing import Dict, Any, List

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
    
    def send_email(self, to_emails, subject, content, content_type="plain", attachments=None):
        """发送邮件（模拟数据）"""
        # 这里返回模拟数据
        return True
    
    def get_email_folders(self):
        """获取邮件文件夹列表（模拟数据）"""
        # 这里返回模拟数据
        return ['INBOX', 'Sent', 'Drafts', 'Spam', 'Trash']