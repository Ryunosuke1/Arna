#!/usr/bin/env python3
"""
Arna - Code Structure Manager

このモジュールはCode Structure Toolsの中核となるコンポーネントを提供します。
プロジェクト構造、関数定義、パラメータ、戻り値、ロジックの管理と、
YAMLシリアライズ/デシリアライズ、コード生成機能を実装しています。
"""

import os
import yaml
from typing import Dict, List, Optional, Any, Union
from jinja2 import Environment, FileSystemLoader


class ParameterDefinition:
    """パラメータ定義を管理するクラス"""
    
    def __init__(self, name: str, description: str):
        """
        パラメータ定義を初期化します。
        
        Args:
            name: パラメータ名
            description: パラメータの説明
        """
        self.name = name
        self.description = description
    
    def to_dict(self) -> Dict[str, str]:
        """
        パラメータ定義を辞書形式に変換します。
        
        Returns:
            パラメータ定義の辞書表現
        """
        return {
            "name": self.name,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ParameterDefinition':
        """
        辞書からパラメータ定義を生成します。
        
        Args:
            data: パラメータ定義の辞書表現
            
        Returns:
            生成されたParameterDefinitionインスタンス
        """
        return cls(
            name=data.get("name", ""),
            description=data.get("description", "")
        )


class ReturnDefinition:
    """戻り値定義を管理するクラス"""
    
    def __init__(self, description: str):
        """
        戻り値定義を初期化します。
        
        Args:
            description: 戻り値の説明
        """
        self.description = description
    
    def to_dict(self) -> Dict[str, str]:
        """
        戻り値定義を辞書形式に変換します。
        
        Returns:
            戻り値定義の辞書表現
        """
        return {
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ReturnDefinition':
        """
        辞書から戻り値定義を生成します。
        
        Args:
            data: 戻り値定義の辞書表現
            
        Returns:
            生成されたReturnDefinitionインスタンス
        """
        return cls(
            description=data.get("description", "")
        )


class LogicDefinition:
    """関数ロジック定義を管理するクラス"""
    
    def __init__(self, description: str):
        """
        ロジック定義を初期化します。
        
        Args:
            description: ロジックの説明
        """
        self.description = description
    
    def to_dict(self) -> Dict[str, str]:
        """
        ロジック定義を辞書形式に変換します。
        
        Returns:
            ロジック定義の辞書表現
        """
        return {
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'LogicDefinition':
        """
        辞書からロジック定義を生成します。
        
        Args:
            data: ロジック定義の辞書表現
            
        Returns:
            生成されたLogicDefinitionインスタンス
        """
        return cls(
            description=data.get("description", "")
        )


class FunctionDefinition:
    """関数定義を管理するクラス"""
    
    def __init__(self, name: str, description: str):
        """
        関数定義を初期化します。
        
        Args:
            name: 関数名
            description: 関数の説明
        """
        self.name = name
        self.description = description
        self.parameters: List[ParameterDefinition] = []
        self.returns: Optional[ReturnDefinition] = None
        self.logic: Optional[LogicDefinition] = None
        self.code_structure: List['FunctionDefinition'] = []
    
    def add_parameter(self, name: str, description: str) -> ParameterDefinition:
        """
        関数にパラメータを追加します。
        
        Args:
            name: パラメータ名
            description: パラメータの説明
            
        Returns:
            追加されたParameterDefinitionインスタンス
        """
        param = ParameterDefinition(name, description)
        self.parameters.append(param)
        return param
    
    def set_return(self, description: str) -> ReturnDefinition:
        """
        関数の戻り値を設定します。
        
        Args:
            description: 戻り値の説明
            
        Returns:
            設定されたReturnDefinitionインスタンス
        """
        self.returns = ReturnDefinition(description)
        return self.returns
    
    def set_logic(self, description: str) -> LogicDefinition:
        """
        関数のロジックを設定します。
        
        Args:
            description: ロジックの説明
            
        Returns:
            設定されたLogicDefinitionインスタンス
        """
        self.logic = LogicDefinition(description)
        return self.logic
    
    def add_function(self, name: str, description: str) -> 'FunctionDefinition':
        """
        ネストされた関数を追加します。
        
        Args:
            name: 関数名
            description: 関数の説明
            
        Returns:
            追加されたFunctionDefinitionインスタンス
        """
        func = FunctionDefinition(name, description)
        self.code_structure.append(func)
        return func
    
    def to_dict(self) -> Dict[str, Any]:
        """
        関数定義を辞書形式に変換します。
        
        Returns:
            関数定義の辞書表現
        """
        result = {
            "name": self.name,
            "description": self.description,
        }
        
        if self.parameters:
            result["parameters"] = [p.to_dict() for p in self.parameters]
        
        if self.returns:
            result["returns"] = self.returns.to_dict()
        
        if self.logic:
            result["logic"] = self.logic.to_dict()
        
        if self.code_structure:
            result["code_structure"] = [
                {"function": f.to_dict()} for f in self.code_structure
            ]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionDefinition':
        """
        辞書から関数定義を生成します。
        
        Args:
            data: 関数定義の辞書表現
            
        Returns:
            生成されたFunctionDefinitionインスタンス
        """
        func = cls(
            name=data.get("name", ""),
            description=data.get("description", "")
        )
        
        # パラメータの読み込み
        for param_data in data.get("parameters", []):
            param = ParameterDefinition.from_dict(param_data)
            func.parameters.append(param)
        
        # 戻り値の読み込み
        if "returns" in data:
            func.returns = ReturnDefinition.from_dict(data["returns"])
        
        # ロジックの読み込み
        if "logic" in data:
            func.logic = LogicDefinition.from_dict(data["logic"])
        
        # ネストされた関数の読み込み
        for item in data.get("code_structure", []):
            if "function" in item:
                nested_func = FunctionDefinition.from_dict(item["function"])
                func.code_structure.append(nested_func)
        
        return func


class ProjectStructure:
    """プロジェクト全体の構造を管理するクラス"""
    
    def __init__(self, name: str, description: str):
        """
        プロジェクト構造を初期化します。
        
        Args:
            name: プロジェクト名
            description: プロジェクトの説明
        """
        self.name = name
        self.description = description
        self.code_structure: List[FunctionDefinition] = []
    
    def add_function(self, name: str, description: str) -> FunctionDefinition:
        """
        プロジェクトにトップレベルの関数を追加します。
        
        Args:
            name: 関数名
            description: 関数の説明
            
        Returns:
            追加されたFunctionDefinitionインスタンス
        """
        func = FunctionDefinition(name, description)
        self.code_structure.append(func)
        return func
    
    def find_function(self, path: str) -> Optional[FunctionDefinition]:
        """
        パスで指定された関数を検索します。
        
        Args:
            path: 関数へのパス (例: "main/process_data")
            
        Returns:
            見つかった関数定義、見つからない場合はNone
        """
        if not path:
            return None
        
        path_parts = path.split('/')
        current_level = self.code_structure
        
        # 最初の部分を検索
        found = None
        for func in current_level:
            if func.name == path_parts[0]:
                found = func
                break
        
        if not found or len(path_parts) == 1:
            return found
        
        # 残りのパスを再帰的に検索
        for part in path_parts[1:]:
            found = None
            for func in current_level:
                if func.name == part:
                    found = func
                    current_level = func.code_structure
                    break
            
            if not found:
                return None
        
        return found
    
    def to_dict(self) -> Dict[str, Any]:
        """
        プロジェクト構造を辞書形式に変換します。
        
        Returns:
            プロジェクト構造の辞書表現
        """
        return {
            "name": self.name,
            "description": self.description,
            "code_structure": [
                {"function": f.to_dict()} for f in self.code_structure
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectStructure':
        """
        辞書からプロジェクト構造を生成します。
        
        Args:
            data: プロジェクト構造の辞書表現
            
        Returns:
            生成されたProjectStructureインスタンス
        """
        project = cls(
            name=data.get("name", ""),
            description=data.get("description", "")
        )
        
        for item in data.get("code_structure", []):
            if "function" in item:
                func = FunctionDefinition.from_dict(item["function"])
                project.code_structure.append(func)
        
        return project


class YAMLSerializer:
    """構造データのYAML形式シリアライズ/デシリアライズを行うクラス"""
    
    @staticmethod
    def save_yaml(project: ProjectStructure, file_path: str) -> None:
        """
        プロジェクト構造をYAMLファイルに保存します。
        
        Args:
            project: 保存するプロジェクト構造
            file_path: 保存先のファイルパス
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(project.to_dict(), f, default_flow_style=False, sort_keys=False)
    
    @staticmethod
    def load_yaml(file_path: str) -> ProjectStructure:
        """
        YAMLファイルからプロジェクト構造を読み込みます。
        
        Args:
            file_path: 読み込むファイルパス
            
        Returns:
            読み込まれたプロジェクト構造
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return ProjectStructure.from_dict(data)


class CodeGenerator:
    """構造データからコードを生成するクラス"""
    
    def __init__(self, template_dir: str):
        """
        コードジェネレータを初期化します。
        
        Args:
            template_dir: テンプレートディレクトリのパス
        """
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate_module(self, project: ProjectStructure, output_path: str) -> None:
        """
        プロジェクト構造からPythonモジュールを生成します。
        
        Args:
            project: コード生成元のプロジェクト構造
            output_path: 出力先のファイルパス
        """
        template = self.env.get_template('module_template.py.j2')
        
        # テンプレートにデータを渡してレンダリング
        code = template.render(
            project_name=project.name,
            project_description=project.description,
            functions=project.code_structure
        )
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 生成したコードをファイルに書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)


class CodeStructureManager:
    """Code Structure Toolsの主要機能を提供するクラス"""
    
    def __init__(self, template_dir: str = None):
        """
        CodeStructureManagerを初期化します。
        
        Args:
            template_dir: テンプレートディレクトリのパス（省略時はデフォルトパス）
        """
        self.current_project: Optional[ProjectStructure] = None
        
        if template_dir is None:
            # デフォルトのテンプレートディレクトリを設定
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            template_dir = os.path.join(base_dir, 'templates')
        
        self.code_generator = CodeGenerator(template_dir)
    
    def create_project(self, name: str, description: str) -> ProjectStructure:
        """
        新しいプロジェクト構造を作成します。
        
        Args:
            name: プロジェクト名
            description: プロジェクトの説明
            
        Returns:
            作成されたプロジェクト構造
        """
        self.current_project = ProjectStructure(name, description)
        return self.current_project
    
    def add_function(self, name: str, description: str, parent_path: str = None) -> FunctionDefinition:
        """
        関数定義を追加します。
        
        Args:
            name: 関数名
            description: 関数の説明
            parent_path: 親関数へのパス（省略時はトップレベル）
            
        Returns:
            追加された関数定義
            
        Raises:
            ValueError: プロジェクトが作成されていない場合
            ValueError: 親関数が見つからない場合
        """
        if not self.current_project:
            raise ValueError("プロジェクトが作成されていません。create_project()を先に呼び出してください。")
        
        if parent_path:
            parent = self.current_project.find_function(parent_path)
            if not parent:
                raise ValueError(f"親関数 '{parent_path}' が見つかりません。")
            return parent.add_function(name, description)
        else:
            return self.current_project.add_function(name, description)
    
    def add_parameter(self, function_path: str, name: str, description: str) -> ParameterDefinition:
        """
        関数にパラメータを追加します。
        
        Args:
            function_path: 関数へのパス
            name: パラメータ名
            description: パラメータの説明
            
        Returns:
            追加されたパラメータ定義
            
        Raises:
            ValueError: プロジェクトが作成されていない場合
            ValueError: 関数が見つからない場合
        """
        if not self.current_project:
            raise ValueError("プロジェクトが作成されていません。create_project()を先に呼び出してください。")
        
        function = self.current_project.find_function(function_path)
        if not function:
            raise ValueError(f"関数 '{function_path}' が見つかりません。")
        
        return function.add_parameter(name, description)
    
    def add_return(self, function_path: str, description: str) -> ReturnDefinition:
        """
        関数に戻り値の説明を追加します。
        
        Args:
            function_path: 関数へのパス
            description: 戻り値の説明
            
        Returns:
            設定された戻り値定義
            
        Raises:
            ValueError: プロジェクトが作成されていない場合
            ValueError: 関数が見つからない場合
        """
        if not self.current_project:
            raise ValueError("プロジェクトが作成されていません。create_project()を先に呼び出してください。")
        
        function = self.current_project.find_function(function_path)
        if not function:
            raise ValueError(f"関数 '{function_path}' が見つかりません。")
        
        return function.set_return(description)
    
    def add_logic(self, function_path: str, description: str) -> LogicDefinition:
        """
        関数にロジックの説明を追加します。
        
        Args:
            function_path: 関数へのパス
            description: ロジックの説明
            
        Returns:
            設定されたロジック定義
            
        Raises:
            ValueError: プロジェクトが作成されていない場合
            ValueError: 関数が見つからない場合
        """
        if not self.current_project:
            raise ValueError("プロジェクトが作成されていません。create_project()を先に呼び出してください。")
        
        function = self.current_project.find_function(function_path)
        if not function:
            raise ValueError(f"関数 '{function_path}' が見つかりません。")
        
        return function.set_logic(description)
    
    def show_structure(self) -> str:
        """
        現在のコード構造を文字列形式で表示します。
        
        Returns:
            コード構造の文字列表現
            
        Raises:
            ValueError: プロジェクトが作成されていない場合
        """
        if not self.current_project:
            raise ValueError("プロジェクトが作成されていません。create_project()を先に呼び出してください。")
        
        def format_function(func: FunctionDefinition, indent: in<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>