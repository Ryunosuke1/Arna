"""
UI コンポーネントのテスト

このモジュールはKivyベースのUIコンポーネントの機能をテストします。
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# テスト対象のモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Kivyのウィンドウを表示せずにテストするための設定
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

# Kivyのウィンドウを表示せずにテストするためのモック
from kivy.core.window import Window
Window.size = (800, 600)

# テスト対象のモジュールをインポート
from src.ui.main_app import ProjectView, CodeEditor, OutputConsole, ManusAgentUI, ManusAgentApp


class TestProjectView(unittest.TestCase):
    """ProjectViewクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.project_view = ProjectView()
    
    def test_initialization(self):
        """初期化のテスト"""
        self.assertEqual(self.project_view.orientation, 'vertical')
        self.assertIsNotNone(self.project_view.code_structure_manager)
        self.assertEqual(self.project_view.project_info.text, "プロジェクト: なし")
    
    def test_update_project_view(self):
        """プロジェクトビュー更新のテスト"""
        project_data = {"name": "テストプロジェクト", "description": "テスト用"}
        self.project_view.update_project_view(project_data)
        
        self.assertEqual(self.project_view.project_info.text, "プロジェクト: テストプロジェクト")


class TestCodeEditor(unittest.TestCase):
    """CodeEditorクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.code_editor = CodeEditor()
    
    def test_initialization(self):
        """初期化のテスト"""
        self.assertEqual(self.code_editor.orientation, 'vertical')
        self.assertEqual(self.code_editor.file_label.text, "ファイル: なし")
        self.assertIsNone(self.code_editor.current_file)
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='test code')
    @patch('os.path.exists', return_value=True)
    def test_load_file(self, mock_exists, mock_open):
        """ファイル読み込みのテスト"""
        self.code_editor.load_file('/test/path/file.py')
        
        mock_exists.assert_called_once_with('/test/path/file.py')
        mock_open.assert_called_once_with('/test/path/file.py', 'r')
        self.assertEqual(self.code_editor.code_input.text, 'test code')
        self.assertEqual(self.code_editor.current_file, '/test/path/file.py')
        self.assertEqual(self.code_editor.file_label.text, "ファイル: file.py")
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('kivymd.toast.toast')
    def test_save_file(self, mock_toast, mock_open):
        """ファイル保存のテスト"""
        # 現在のファイルを設定
        self.code_editor.current_file = '/test/path/file.py'
        self.code_editor.code_input.text = 'updated code'
        
        # 保存を実行
        self.code_editor.save_file()
        
        mock_open.assert_called_once_with('/test/path/file.py', 'w')
        mock_open().write.assert_called_once_with('updated code')
        mock_toast.assert_called_once()


class TestOutputConsole(unittest.TestCase):
    """OutputConsoleクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.output_console = OutputConsole()
    
    def test_initialization(self):
        """初期化のテスト"""
        self.assertEqual(self.output_console.orientation, 'vertical')
        self.assertEqual(self.output_console.console_output.text, "")
    
    def test_append_output(self):
        """出力追加のテスト"""
        self.output_console.append_output("テスト出力1")
        self.assertEqual(self.output_console.console_output.text, "テスト出力1\n")
        
        self.output_console.append_output("テスト出力2")
        self.assertEqual(self.output_console.console_output.text, "テスト出力1\nテスト出力2\n")
    
    def test_clear_console(self):
        """コンソールクリアのテスト"""
        self.output_console.console_output.text = "テスト出力\n"
        self.output_console.clear_console()
        self.assertEqual(self.output_console.console_output.text, "")


class TestManusAgentUI(unittest.TestCase):
    """ManusAgentUIクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        # AgentManagerとCodeStructureManagerをモック
        with patch('src.ui.main_app.AgentManager'), \
             patch('src.ui.main_app.CodeStructureManager'):
            self.ui = ManusAgentUI()
    
    def test_initialization(self):
        """初期化のテスト"""
        self.assertEqual(self.ui.orientation, 'vertical')
        self.assertIsNotNone(self.ui.agent_manager)
        self.assertIsNotNone(self.ui.code_structure_manager)
        self.assertIsNotNone(self.ui.toolbar)
        self.assertIsNotNone(self.ui.project_view)
        self.assertIsNotNone(self.ui.code_editor)
        self.assertIsNotNone(self.ui.output_console)
        self.assertIsNotNone(self.ui.file_manager)
    
    @patch('kivymd.toast.toast')
    def test_show_settings(self, mock_toast):
        """設定表示のテスト"""
        self.ui.show_settings()
        mock_toast.assert_called_once()
    
    @patch('kivymd.toast.toast')
    def test_show_help(self, mock_toast):
        """ヘルプ表示のテスト"""
        self.ui.show_help()
        mock_toast.assert_called_once()
    
    @patch('src.ui.main_app.CodeStructureManager.create_project')
    def test_create_new_project(self, mock_create_project):
        """新規プロジェクト作成のテスト"""
        # モックの戻り値を設定
        mock_create_project.return_value = {"name": "サンプルプロジェクト"}
        
        # ProjectViewのupdate_project_viewをモック
        self.ui.project_view.update_project_view = MagicMock()
        
        # OutputConsoleのappend_outputをモック
        self.ui.output_console.append_output = MagicMock()
        
        # テスト実行
        self.ui.create_new_project(None)
        
        # 検証
        mock_create_project.assert_called_once_with("サンプルプロジェクト", "サンプルプロジェクトの説明")
        self.ui.project_view.update_project_view.assert_called_once()
        self.ui.output_console.append_output.assert_called_once()
    
    @patch('os.makedirs')
    @patch('src.ui.main_app.CodeStructureManager.generate_code')
    def test_generate_code(self, mock_generate_code, mock_makedirs):
        """コード生成のテスト"""
        # モックの戻り値を設定
        mock_generate_code.return_value = ["/path/to/generated/file.py"]
        
        # OutputConsoleのappend_outputをモック
        self.ui.output_console.append_output = MagicMock()
        
        # CodeEditorのload_fileをモック
        self.ui.code_editor.load_file = MagicMock()
        
        # テスト実行
        self.ui.generate_code(None)
        
        # 検証
        mock_makedirs.assert_called_once()
        mock_generate_code.assert_called_once()
        self.ui.output_console.append_output.assert_called()
        self.ui.code_editor.load_file.assert_called_once_with("/path/to/generated/file.py")


class TestManusAgentApp(unittest.TestCase):
    """ManusAgentAppクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.app = ManusAgentApp()
    
    def test_build(self):
        """ビルドメソッドのテスト"""
        # ManusAgentUIの初期化をモック
        with patch('src.ui.main_app.ManusAgentUI') as mock_ui:
            mock_ui_instance = MagicMock()
            mock_ui.return_value = mock_ui_instance
            
            result = self.app.build()
            
            self.assertEqual(result, mock_ui_instance)
            self.assertEqual(self.app.theme_cls.primary_palette, "Blue")
            self.assertEqual(self.app.theme_cls.accent_palette, "Amber")
            self.assertEqual(self.app.theme_cls.theme_style, "Light")


if __name__ == '__main__':
    unittest.main()
