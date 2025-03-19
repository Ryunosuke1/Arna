"""
Code Structure Tools Module

このモジュールはYAMLベースのコード構造定義と管理を行うためのツールを提供します。
プロジェクト作成、関数定義追加、パラメータ追加、戻り値定義、ロジック記述などの機能を含みます。
"""

import os
import yaml
from typing import Dict, List, Optional, Any, Union
import jinja2


class CodeStructureManager:
    """
    コード構造を管理するクラス
    YAMLベースのコード構造定義と操作を行います
    """

    def __init__(self):
        """
        CodeStructureManagerの初期化
        """
        self.project = None
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)) + "/../templates"),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def create_project(self, name: str, description: str) -> Dict[str, Any]:
        """
        新しいプロジェクト構造を作成します

        Args:
            name: プロジェクト名
            description: プロジェクトの説明

        Returns:
            作成されたプロジェクト構造
        """
        self.project = {
            "name": name,
            "description": description,
            "code_structure": []
        }
        return self.project

    def add_function(self, name: str, description: str, parent_path: Optional[str] = None) -> Dict[str, Any]:
        """
        関数定義を追加します

        Args:
            name: 関数名
            description: 関数の説明
            parent_path: 親関数のパス (オプション)

        Returns:
            追加された関数定義
        """
        if self.project is None:
            raise ValueError("プロジェクトが作成されていません。先にcreate_projectを呼び出してください。")

        function_def = {
            "name": name,
            "description": description,
            "parameters": [],
            "returns": {"description": ""},
            "logic": {"description": ""},
            "code_structure": []
        }

        # 親パスが指定されていない場合はトップレベルに追加
        if parent_path is None:
            self.project["code_structure"].append({"function": function_def})
            return function_def

        # 親パスが指定されている場合は該当する場所に追加
        parent_parts = parent_path.split('.')
        current = self.project["code_structure"]

        for i, part in enumerate(parent_parts):
            for item in current:
                if "function" in item and item["function"]["name"] == part:
                    if i == len(parent_parts) - 1:  # 最後の要素に到達
                        item["function"]["code_structure"].append({"function": function_def})
                        return function_def
                    else:
                        current = item["function"]["code_structure"]
                        break
            else:
                raise ValueError(f"親パス '{parent_path}' が見つかりません")

        return function_def

    def add_parameter(self, function_path: str, name: str, description: str) -> Dict[str, str]:
        """
        関数にパラメータを追加します

        Args:
            function_path: 関数のパス
            name: パラメータ名
            description: パラメータの説明

        Returns:
            追加されたパラメータ定義
        """
        if self.project is None:
            raise ValueError("プロジェクトが作成されていません。先にcreate_projectを呼び出してください。")

        function = self._find_function(function_path)
        if function is None:
            raise ValueError(f"関数 '{function_path}' が見つかりません")

        parameter = {
            "name": name,
            "description": description
        }
        function["parameters"].append(parameter)
        return parameter

    def add_return(self, function_path: str, description: str) -> Dict[str, str]:
        """
        関数に戻り値の説明を追加します

        Args:
            function_path: 関数のパス
            description: 戻り値の説明

        Returns:
            更新された戻り値定義
        """
        if self.project is None:
            raise ValueError("プロジェクトが作成されていません。先にcreate_projectを呼び出してください。")

        function = self._find_function(function_path)
        if function is None:
            raise ValueError(f"関数 '{function_path}' が見つかりません")

        function["returns"]["description"] = description
        return function["returns"]

    def add_logic(self, function_path: str, description: str) -> Dict[str, str]:
        """
        関数にロジックの説明を追加します

        Args:
            function_path: 関数のパス
            description: ロジックの説明

        Returns:
            更新されたロジック定義
        """
        if self.project is None:
            raise ValueError("プロジェクトが作成されていません。先にcreate_projectを呼び出してください。")

        function = self._find_function(function_path)
        if function is None:
            raise ValueError(f"関数 '{function_path}' が見つかりません")

        function["logic"]["description"] = description
        return function["logic"]

    def show_structure(self) -> str:
        """
        現在のコード構造を表示します

        Returns:
            コード構造の文字列表現
        """
        if self.project is None:
            return "プロジェクトが作成されていません。"

        result = [f"プロジェクト: {self.project['name']}"]
        result.append(f"説明: {self.project['description']}")
        result.append("コード構造:")
        
        self._append_structure(self.project["code_structure"], result, indent=1)
        
        return "\n".join(result)

    def _append_structure(self, structure: List[Dict[str, Any]], result: List[str], indent: int = 0):
        """
        コード構造を再帰的に文字列リストに追加します

        Args:
            structure: コード構造
            result: 結果を格納するリスト
            indent: インデントレベル
        """
        for item in structure:
            if "function" in item:
                func = item["function"]
                result.append(f"{'  ' * indent}関数: {func['name']}")
                result.append(f"{'  ' * (indent+1)}説明: {func['description']}")
                
                if func["parameters"]:
                    result.append(f"{'  ' * (indent+1)}パラメータ:")
                    for param in func["parameters"]:
                        result.append(f"{'  ' * (indent+2)}{param['name']}: {param['description']}")
                
                if func["returns"]["description"]:
                    result.append(f"{'  ' * (indent+1)}戻り値: {func['returns']['description']}")
                
                if func["logic"]["description"]:
                    result.append(f"{'  ' * (indent+1)}ロジック: {func['logic']['description']}")
                
                if func["code_structure"]:
                    result.append(f"{'  ' * (indent+1)}内部構造:")
                    self._append_structure(func["code_structure"], result, indent=indent+2)

    def show_summary(self) -> str:
        """
        プロジェクトの要約を表示します

        Returns:
            プロジェクト要約の文字列表現
        """
        if self.project is None:
            return "プロジェクトが作成されていません。"

        result = [f"プロジェクト要約: {self.project['name']}"]
        result.append(f"説明: {self.project['description']}")
        
        function_count = self._count_functions(self.project["code_structure"])
        result.append(f"関数数: {function_count}")
        
        return "\n".join(result)

    def _count_functions(self, structure: List[Dict[str, Any]]) -> int:
        """
        コード構造内の関数数を再帰的にカウントします

        Args:
            structure: コード構造

        Returns:
            関数の総数
        """
        count = 0
        for item in structure:
            if "function" in item:
                count += 1
                count += self._count_functions(item["function"]["code_structure"])
        return count

    def save_yaml(self, file_path: str) -> None:
        """
        コード構造をYAMLファイルに保存します

        Args:
            file_path: 保存先ファイルパス
        """
        if self.project is None:
            raise ValueError("プロジェクトが作成されていません。先にcreate_projectを呼び出してください。")

        with open(file_path, 'w') as f:
            yaml.dump(self.project, f, default_flow_style=False, sort_keys=False)

    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        YAMLファイルからコード構造を読み込みます

        Args:
            file_path: 読み込むファイルパス

        Returns:
            読み込まれたプロジェクト構造
        """
        with open(file_path, 'r') as f:
            self.project = yaml.safe_load(f)
        return self.project

    def generate_code(self, output_path: str) -> List[str]:
        """
        コード構造からPythonコードを生成します

        Args:
            output_path: 出力先ディレクトリパス

        Returns:
            生成されたファイルパスのリスト
        """
        if self.project is None:
            raise ValueError("プロジェクトが作成されていません。先にcreate_projectを呼び出してください。")

        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_path, exist_ok=True)

        # メインファイルの生成
        main_file_path = os.path.join(output_path, f"{self.project['name'].lower().replace(' ', '_')}.py")
        
        # テンプレートがない場合は作成
        self._ensure_templates_exist()
        
        # テンプレートからコード生成
        template = self.template_env.get_template("module_template.py.j2")
        code = template.render(project=self.project)
        
        with open(main_file_path, 'w') as f:
            f.write(code)
        
        return [main_file_path]

    def _ensure_templates_exist(self):
        """
        テンプレートディレクトリとテンプレートファイルが存在することを確認します
        存在しない場合は作成します
        """
        template_dir = os.path.dirname(os.path.abspath(__file__)) + "/../templates"
        os.makedirs(template_dir, exist_ok=True)
        
        module_template_path = os.path.join(template_dir, "module_template.py.j2")
        if not os.path.exists(module_template_path):
            with open(module_template_path, 'w') as f:
                f.write("""'''
{{ project.name }}

{{ project.description }}
'''

{% for item in project.code_structure %}
{% if 'function' in item %}
def {{ item.function.name }}({% for param in item.function.parameters %}{{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %}):
    '''
    {{ item.function.description }}
    
    {% if item.function.parameters %}
    Args:
        {% for param in item.function.parameters %}
        {{ param.name }}: {{ param.description }}
        {% endfor %}
    {% endif %}
    {% if item.function.returns.description %}
    Returns:
        {{ item.function.returns.description }}
    {% endif %}
    '''
    # {{ item.function.logic.description }}
    pass

{% endif %}
{% endfor %}

if __name__ == "__main__":
    # Main execution
    pass
""")

    def _find_function(self, function_path: str) -> Optional[Dict[str, Any]]:
        """
        関数パスから関数定義を検索します

        Args:
            function_path: 関数のパス (例: "main.sub_func")

        Returns:
            関数定義、見つからない場合はNone
        """
        if self.project is None:
            return None

        parts = function_path.split('.')
        current = self.project["code_structure"]

        for i, part in enumerate(parts):
            for item in current:
                if "function" in item and item["function"]["name"] == part:
                    if i == len(parts) - 1:  # 最後の要素に到達
                        return item["function"]
                    else:
                        current = item["function"]["code_structure"]
                        break
            else:
                return None

        return None


# コマンドラインインターフェース用の関数
def create_project(name, description):
    """プロジェクトを作成する"""
    manager = CodeStructureManager()
    return manager.create_project(name, description)

def add_function(name, description, parent_path=None):
    """関数を追加する"""
    manager = CodeStructureManager()
    return manager.add_function(name, description, parent_path)

def add_parameter(function_path, name, description):
    """パラメータを追加する"""
    manager = CodeStructureManager()
    return manager.add_parameter(function_path, name, description)

def add_return(function_path, description):
    """戻り値の説明を追加する"""
    manager = CodeStructureManager()
    return manager.add_return(function_path, description)

def add_logic(function_path, description):
    """ロジックの説明を追加する"""
    manager = CodeStructureManager()
    return manager.add_logic(function_path, description)

def show_structure():
    """コード構造を表示する"""
    manager = CodeStructureManager()
    return manager.show_structure()

def show_summary():
    """プロジェクト要約を表示する"""
    manager = CodeStructureManager()
    return manager.show_summary()

def save_yaml(file_path):
    """YAMLファイルに保存する"""
    manager = CodeStructureManager()
    return manager.save_yaml(file_path)

def load_yaml(file_path):
    """YAMLファイルから読み込む"""
    manager = CodeStructureManager()
    return manager.load_yaml(file_path)

def generate_code(output_path):
    """コードを生成する"""
    manager = CodeStructureManager()
    return manager.generate_code(output_path)
