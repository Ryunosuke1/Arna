"""
Code Structure Tools のテスト

このモジュールはCode Structure Toolsの機能をテストします。
"""

import os
import sys
import unittest
import tempfile
import yaml

# テスト対象のモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.tools.code_structure import CodeStructureManager


class TestCodeStructureManager(unittest.TestCase):
    """CodeStructureManagerのテストクラス"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.manager = CodeStructureManager()
        self.test_project_name = "テストプロジェクト"
        self.test_project_desc = "テスト用のプロジェクト"
    
    def test_create_project(self):
        """プロジェクト作成機能のテスト"""
        project = self.manager.create_project(self.test_project_name, self.test_project_desc)
        
        self.assertEqual(project["name"], self.test_project_name)
        self.assertEqual(project["description"], self.test_project_desc)
        self.assertIn("code_structure", project)
        self.assertEqual(len(project["code_structure"]), 0)
    
    def test_add_function(self):
        """関数追加機能のテスト"""
        self.manager.create_project(self.test_project_name, self.test_project_desc)
        
        # トップレベル関数の追加
        func = self.manager.add_function("main", "メイン関数")
        
        self.assertEqual(func["name"], "main")
        self.assertEqual(func["description"], "メイン関数")
        self.assertEqual(len(func["parameters"]), 0)
        self.assertEqual(func["returns"]["description"], "")
        self.assertEqual(func["logic"]["description"], "")
        
        # プロジェクト構造の確認
        self.assertEqual(len(self.manager.project["code_structure"]), 1)
        self.assertIn("function", self.manager.project["code_structure"][0])
        
        # ネストされた関数の追加
        nested_func = self.manager.add_function("helper", "ヘルパー関数", "main")
        
        self.assertEqual(nested_func["name"], "helper")
        self.assertEqual(nested_func["description"], "ヘルパー関数")
        
        # ネストされた構造の確認
        main_func = self.manager.project["code_structure"][0]["function"]
        self.assertEqual(len(main_func["code_structure"]), 1)
        self.assertEqual(main_func["code_structure"][0]["function"]["name"], "helper")
    
    def test_add_parameter(self):
        """パラメータ追加機能のテスト"""
        self.manager.create_project(self.test_project_name, self.test_project_desc)
        self.manager.add_function("process_data", "データ処理関数")
        
        param = self.manager.add_parameter("process_data", "data", "処理するデータ")
        
        self.assertEqual(param["name"], "data")
        self.assertEqual(param["description"], "処理するデータ")
        
        # 関数のパラメータリストの確認
        func = self.manager._find_function("process_data")
        self.assertEqual(len(func["parameters"]), 1)
        self.assertEqual(func["parameters"][0]["name"], "data")
    
    def test_add_return(self):
        """戻り値追加機能のテスト"""
        self.manager.create_project(self.test_project_name, self.test_project_desc)
        self.manager.add_function("calculate", "計算関数")
        
        returns = self.manager.add_return("calculate", "計算結果")
        
        self.assertEqual(returns["description"], "計算結果")
        
        # 関数の戻り値の確認
        func = self.manager._find_function("calculate")
        self.assertEqual(func["returns"]["description"], "計算結果")
    
    def test_add_logic(self):
        """ロジック追加機能のテスト"""
        self.manager.create_project(self.test_project_name, self.test_project_desc)
        self.manager.add_function("validate", "検証関数")
        
        logic = self.manager.add_logic("validate", "入力データの検証を行う")
        
        self.assertEqual(logic["description"], "入力データの検証を行う")
        
        # 関数のロジックの確認
        func = self.manager._find_function("validate")
        self.assertEqual(func["logic"]["description"], "入力データの検証を行う")
    
    def test_show_structure(self):
        """構造表示機能のテスト"""
        self.manager.create_project(self.test_project_name, self.test_project_desc)
        self.manager.add_function("main", "メイン関数")
        self.manager.add_parameter("main", "args", "コマンドライン引数")
        self.manager.add_return("main", "終了コード")
        
        structure = self.manager.show_structure()
        
        self.assertIn(self.test_project_name, structure)
        self.assertIn("メイン関数", structure)
        self.assertIn("args", structure)
        self.assertIn("終了コード", structure)
    
    def test_save_and_load_yaml(self):
        """YAML保存・読み込み機能のテスト"""
        self.manager.create_project(self.test_project_name, self.test_project_desc)
        self.manager.add_function("main", "メイン関数")
        
        # 一時ファイルにYAMLを保存
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp:
            yaml_path = temp.name
        
        try:
            self.manager.save_yaml(yaml_path)
            
            # 新しいマネージャーでYAMLを読み込み
            new_manager = CodeStructureManager()
            loaded_project = new_manager.load_yaml(yaml_path)
            
            # 読み込んだプロジェクトの検証
            self.assertEqual(loaded_project["name"], self.test_project_name)
            self.assertEqual(loaded_project["description"], self.test_project_desc)
            self.assertEqual(len(loaded_project["code_structure"]), 1)
            self.assertEqual(loaded_project["code_structure"][0]["function"]["name"], "main")
        finally:
            # テスト後に一時ファイルを削除
            if os.path.exists(yaml_path):
                os.unlink(yaml_path)
    
    def test_generate_code(self):
        """コード生成機能のテスト"""
        self.manager.create_project(self.test_project_name, self.test_project_desc)
        self.manager.add_function("greet", "挨拶関数")
        self.manager.add_parameter("greet", "name", "名前")
        self.manager.add_return("greet", "挨拶メッセージ")
        self.manager.add_logic("greet", "名前を含む挨拶メッセージを返す")
        
        # 一時ディレクトリにコードを生成
        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.manager.generate_code(temp_dir)
            
            # 生成されたファイルの検証
            self.assertEqual(len(generated_files), 1)
            self.assertTrue(os.path.exists(generated_files[0]))
            
            # ファイル内容の検証
            with open(generated_files[0], 'r') as f:
                content = f.read()
                self.assertIn(self.test_project_name, content)
                self.assertIn("def greet", content)
                self.assertIn("name", content)
                self.assertIn("挨拶メッセージ", content)


if __name__ == '__main__':
    unittest.main()
