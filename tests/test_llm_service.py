"""
LLM Service のテスト

このモジュールはLLM Serviceの機能をテストします。
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

# テスト対象のモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.services.llm_service import LLMConnector, PromptManager, ResponseParser, ContextManager, LLMService


class TestLLMConnector(unittest.TestCase):
    """LLMConnectorのテストクラス"""
    
    def setUp(self):
        """各テスト前の準備"""
        # 環境変数をモック
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_api_key',
            'OPENAI_API_BASE': 'https://test-api.example.com/v1',
            'OPENAI_MODEL': 'test-model'
        })
        self.env_patcher.start()
        self.connector = LLMConnector()
    
    def tearDown(self):
        """各テスト後の後処理"""
        self.env_patcher.stop()
    
    def test_initialization(self):
        """初期化のテスト"""
        self.assertEqual(self.connector.api_key, 'test_api_key')
        self.assertEqual(self.connector.api_base_url, 'https://test-api.example.com/v1')
        self.assertEqual(self.connector.default_model, 'test-model')
    
    def test_set_api_key(self):
        """APIキー設定のテスト"""
        self.connector.set_api_key('new_api_key')
        self.assertEqual(self.connector.api_key, 'new_api_key')
        self.assertEqual(self.connector.session.headers['Authorization'], 'Bearer new_api_key')
    
    def test_set_api_base_url(self):
        """API基本URL設定のテスト"""
        self.connector.set_api_base_url('https://new-api.example.com/v1')
        self.assertEqual(self.connector.api_base_url, 'https://new-api.example.com/v1')
    
    @patch('requests.Session.post')
    def test_chat_completion(self, mock_post):
        """チャット補完APIのテスト"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'テスト応答'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # テスト実行
        messages = [{'role': 'user', 'content': 'テスト'}]
        response = self.connector.chat_completion(messages)
        
        # 検証
        mock_post.assert_called_once()
        self.assertEqual(response['choices'][0]['message']['content'], 'テスト応答')
        
        # 呼び出し引数の検証
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['model'], 'test-model')
        self.assertEqual(kwargs['json']['messages'], messages)


class TestPromptManager(unittest.TestCase):
    """PromptManagerのテストクラス"""
    
    def setUp(self):
        """各テスト前の準備"""
        # 一時ディレクトリを使用
        self.temp_dir = tempfile.mkdtemp()
        self.prompt_manager = PromptManager(self.temp_dir)
    
    def tearDown(self):
        """各テスト後の後処理"""
        # 一時ディレクトリを削除
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_default_templates(self):
        """デフォルトテンプレートのテスト"""
        # デフォルトテンプレートが作成されていることを確認
        self.assertIn('code_generation', self.prompt_manager.templates)
        self.assertIn('code_review', self.prompt_manager.templates)
        self.assertIn('task_decomposition', self.prompt_manager.templates)
        self.assertIn('error_analysis', self.prompt_manager.templates)
    
    def test_get_template(self):
        """テンプレート取得のテスト"""
        template = self.prompt_manager.get_template('code_generation')
        self.assertIsNotNone(template)
        self.assertIn('{requirements}', template)
        
        # 存在しないテンプレート
        self.assertIsNone(self.prompt_manager.get_template('non_existent'))
    
    def test_format_prompt(self):
        """プロンプトフォーマットのテスト"""
        formatted = self.prompt_manager.format_prompt(
            'code_generation',
            requirements='テスト要件',
            constraints='テスト制約'
        )
        
        self.assertIn('テスト要件', formatted)
        self.assertIn('テスト制約', formatted)
    
    def test_create_chat_messages(self):
        """チャットメッセージ作成のテスト"""
        system_prompt = 'システム指示'
        user_prompt = 'ユーザー指示'
        
        messages = self.prompt_manager.create_chat_messages(system_prompt, user_prompt)
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[0]['content'], system_prompt)
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[1]['content'], user_prompt)
        
        # 過去のメッセージを含む場合
        user_messages = ['過去の質問1', '過去の質問2']
        assistant_messages = ['過去の回答1', '過去の回答2']
        
        messages = self.prompt_manager.create_chat_messages(
            system_prompt, user_prompt, assistant_messages, user_messages
        )
        
        self.assertEqual(len(messages), 6)  # システム + 4つの過去メッセージ + 現在のユーザーメッセージ


class TestResponseParser(unittest.TestCase):
    """ResponseParserのテストクラス"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.parser = ResponseParser()
    
    def test_extract_code(self):
        """コード抽出のテスト"""
        text = """
        以下のコードを使用してください：
        
        ```python
        def hello():
            print("Hello, world!")
        ```
        
        また、HTMLも使えます：
        
        ```html
        <div>Hello</div>
        ```
        """
        
        code_blocks = self.parser.extract_code(text)
        
        self.assertEqual(len(code_blocks), 2)
        self.assertEqual(code_blocks[0]['language'], 'python')
        self.assertEqual(code_blocks[0]['code'], 'def hello():\n    print("Hello, world!")')
        self.assertEqual(code_blocks[1]['language'], 'html')
        self.assertEqual(code_blocks[1]['code'], '<div>Hello</div>')
    
    def test_extract_json(self):
        """JSON抽出のテスト"""
        text = """
        以下のJSONを使用してください：
        
        ```json
        {
            "name": "テスト",
            "value": 123
        }
        ```
        """
        
        json_data = self.parser.extract_json(text)
        
        self.assertIsNotNone(json_data)
        self.assertEqual(json_data['name'], 'テスト')
        self.assertEqual(json_data['value'], 123)
    
    def test_extract_list(self):
        """リスト抽出のテスト"""
        text = """
        以下の手順に従ってください：
        
        - 最初のステップ
        - 2番目のステップ
          詳細な説明
        - 最後のステップ
        
        以上です。
        """
        
        items = self.parser.extract_list(text)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], '最初のステップ')
        self.assertEqual(items[1], '2番目のステップ\n  詳細な説明')
        self.assertEqual(items[2], '最後のステップ')


class TestContextManager(unittest.TestCase):
    """ContextManagerのテストクラス"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.context_manager = ContextManager(max_context_length=5)
    
    def test_add_message(self):
        """メッセージ追加のテスト"""
        self.context_manager.add_message('system', 'システム指示')
        self.context_manager.add_message('user', 'ユーザー指示')
        
        messages = self.context_manager.get_conversation_messages()
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[0]['content'], 'システム指示')
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[1]['content'], 'ユーザー指示')
    
    def test_max_context_length(self):
        """最大コンテキスト長のテスト"""
        # システムメッセージ
        self.context_manager.add_message('system', 'システム指示')
        
        # 最大長を超えるメッセージを追加
        for i in range(6):
            self.context_manager.add_message('user', f'メッセージ{i}')
        
        messages = self.context_manager.get_conversation_messages()
        
        # システムメッセージ + 最新の4つのメッセージ = 5
        self.assertEqual(len(messages), 5)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['content'], 'メッセージ2')
        self.assertEqual(messages[4]['content'], 'メッセージ5')
    
    def test_clear_conversation(self):
        """会話クリアのテスト"""
        self.context_manager.add_message('system', 'システム指示')
        self.context_manager.add_message('user', 'ユーザー指示')
        
        # システムメッセージを保持してクリア
        self.context_manager.clear_conversation(keep_system=True)
        
        messages = self.context_manager.get_conversation_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['role'], 'system')
        
        # 完全にクリア
        self.context_manager.clear_conversation(keep_system=False)
        
        messages = self.context_manager.get_conversation_messages()
        self.assertEqual(len(messages), 0)
    
    def test_save_and_load_conversation(self):
        """会話の保存と読み込みのテスト"""
        self.context_manager.add_message('system', 'システム指示')
        self.context_manager.add_message('user', 'ユーザー指示')
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            file_path = temp.name
        
        try:
            self.context_manager.save_conversation(file_path)
            
            # 新しいコンテキストマネージャーで読み込み
            new_context = ContextManager()
            new_context.load_conversation(file_path)
            
            messages = new_context.get_conversation_messages()
            
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]['role'], 'system')
            self.assertEqual(messages[0]['content'], 'システム指示')
        finally:
            # テスト後に一時ファイルを削除
            if os.path.exists(file_path):
                os.unlink(file_path)


class TestLLMService(unittest.TestCase):
    """LLMServiceのテストクラス"""
    
    def setUp(self):
        """各テスト前の準備"""
        # LLMConnectorをモック
        self.connector_patcher = patch('src.services.llm_service.LLMConnector')
        self.mock_connector_class = self.connector_patcher.start()
        self.mock_connector = self.mock_connector_class.return_value
        
        # モックレスポンスの設定
        self.mock_connector.chat_completion.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'テスト応答'
                    }
                }
            ]
        }
        
        self.llm_service = LLMService()
    
    def tearDown(self):
        """各テスト後の後処理"""
        self.connector_patcher.stop()
    
    def test_generate_code(self):
        """コード生成のテスト"""
        # ResponseParserをモック
        with patch.object(self.llm_service.response_parser, 'extract_code') as mock_extract:
            mock_extract.return_value = [
                {'language': 'python', 'code': 'def test(): pass'}
            ]
            
            result = self.llm_service.generate_code('テスト要件', '制約')
            
            # 検証
            self.mock_connector.chat_completion.assert_called_once()
            mock_extract.assert_called_once_with('テスト応答')
            self.assertEqual(result, [{'language': 'python', 'code': 'def test(): pass'}])
    
    def test_review_code(self):
        """コードレビューのテスト"""
        result = self.llm_service.review_code('def test(): pass')
        
        # 検証
        self.mock_connector.chat_completion.assert_called_once()
        self.assertEqual(result, 'テスト応答')
    
    def test_decompose_task(self):
        """タスク分解のテスト"""
        # ResponseParserをモック
        with patch.object(self.llm_service.response_parser, 'extract_list') as mock_extract:
            mock_extract.return_value = ['サブタスク1', 'サブタスク2']
            
            result = self.llm_service.decompose_task('テストタスク')
            
            # 検証
            self.mock_connector.chat_completion.assert_called_once()
            mock_extract.assert_called_once_with('テスト応答')
            self.assertEqual(result, ['サブタスク1', 'サブタスク2'])
    
    def test_analyze_error(self):
        """エラー分析のテスト"""
        result = self.llm_service.analyze_error('テストエラー')
        
        # 検証
        self.mock_connector.chat_completion.assert_called_once()
        self.assertEqual(result, 'テスト応答')
    
    def test_chat(self):
        """チャットのテスト"""
        result = self.llm_service.chat('こんにちは')
        
        # 検証
        self.mock_connector.chat_completion.assert_called_once()
        self.assertEqual(result, 'テスト応答')
        
        # システムプロンプト付き
        self.mock_connector.chat_completion.reset_mock()
        result = self.llm_service.chat('こんにちは', 'システム指示')
        
        self.mock_connector.chat_completion.assert_called_once()
        self.assertEqual(result, 'テスト応答')


if __name__ == '__main__':
    unittest.main()
