from typing import Dict, Optional, Union
import yaml
from pathlib import Path

class CodeStructureTools:
    def __init__(self):
        self.current_structure: Dict = {
            "name": "",
            "description": "",
            "code_structure": []
        }
    
    async def create_project(self, name: str, description: str) -> None:
        """プロジェクトの基本構造を作成"""
        self.current_structure = {
            "name": name,
            "description": description,
            "code_structure": []
        }
    
    async def add_function(self, name: str, description: str, parent_path: str = "") -> None:
        """関数構造を追加"""
        function_def = {
            "function": {
                "name": name,
                "description": description,
                "code_structure": []
            }
        }
        
        if not parent_path:
            self.current_structure["code_structure"].append(function_def)
        else:
            parent = self._get_node_by_path(parent_path)
            if parent and "code_structure" in parent:
                parent["code_structure"].append(function_def)
    
    async def add_parameter(self, function_path: str, name: str, description: str) -> None:
        """関数のパラメータを追加"""
        function = self._get_node_by_path(function_path)
        if function:
            if "parameters" not in function:
                function["parameters"] = []
            function["parameters"].append({
                "name": name,
                "description": description
            })
    
    async def add_return(self, function_path: str, description: str) -> None:
        """関数の戻り値の説明を追加"""
        function = self._get_node_by_path(function_path)
        if function:
            function["returns"] = {"description": description}
    
    async def add_logic(self, function_path: str, description: str) -> None:
        """関数のロジックの説明を追加"""
        function = self._get_node_by_path(function_path)
        if function:
            function["logic"] = {"description": description}
    
    async def show_structure(self, path: str = "") -> str:
        """現在のコード構造をツリー形式で表示"""
        if path:
            node = self._get_node_by_path(path)
            return self._format_tree(node, is_root=False)
        return self._format_tree(self.current_structure)
    
    async def show_summary(self) -> str:
        """プロジェクトの概要を表示"""
        summary = [
            f"# {self.current_structure['name']}",
            f"Description: {self.current_structure['description']}",
            "\nFunctions:",
        ]
        
        for item in self.current_structure["code_structure"]:
            if isinstance(item, dict) and "function" in item:
                func = item["function"]
                params = [p["name"] for p in func.get("parameters", [])]
                param_str = ", ".join(params) if params else "None"
                summary.append(f"- {func['name']}({param_str})")
                summary.append(f"  Description: {func['description']}")
        
        return "\n".join(summary)
    
    async def save_yaml(self, file_path: str) -> None:
        """現在の構造をYAMLファイルとして保存"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.current_structure, f, allow_unicode=True)
    
    async def load_yaml(self, file_path: str) -> None:
        """YAMLファイルから構造を読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.current_structure = yaml.safe_load(f)
    
    async def generate_code(self, output_path: str) -> str:
        """現在の構造からPythonコードを生成し保存"""
        code = self._generate_code_from_structure(self.current_structure)
        if output_path:
            Path(output_path).write_text(code, encoding='utf-8')
        return code
    
    def _get_node_by_path(self, path: str) -> Optional[Dict]:
        """パスから指定されたノードを取得"""
        parts = path.split('.')
        current = self.current_structure
        
        for part in parts:
            if "code_structure" in current:
                for item in current["code_structure"]:
                    if isinstance(item, dict):
                        if "function" in item and item["function"]["name"] == part:
                            current = item["function"]
                            break
                        elif "class" in item and item["class"]["name"] == part:
                            current = item["class"]
                            break
        return current
    
    def _format_tree(self, node: Dict, level: int = 0, is_root: bool = True) -> str:
        """ツリー形式でコード構造を表示"""
        lines = []
        indent = "  " * level
        
        if is_root:
            lines.append(f"{node['name']}/")
            lines.append(f"{indent}Description: {node['description']}")
            level += 1
            indent = "  " * level
        
        if "code_structure" in node:
            for item in node["code_structure"]:
                if isinstance(item, dict):
                    if "function" in item:
                        func = item["function"]
                        lines.append(f"{indent}└─ {func['name']}()")
                        if "description" in func:
                            lines.append(f"{indent}   Description: {func['description']}")
                        if "parameters" in func:
                            for param in func["parameters"]:
                                lines.append(f"{indent}   ├─ Param: {param['name']}")
                                lines.append(f"{indent}   │  {param['description']}")
                    elif "class" in item:
                        class_def = item["class"]
                        lines.append(f"{indent}└─ class {class_def['name']}")
                        if "description" in class_def:
                            lines.append(f"{indent}   Description: {class_def['description']}")
                        lines.extend(self._format_tree(class_def, level + 2, False).split('\n'))
                elif isinstance(item, str):
                    lines.append(f"{indent}└─ {item}")
        
        return "\n".join(lines)
    
    def _generate_code_from_structure(self, structure: Dict) -> str:
        """構造からPythonコードを生成"""
        return CodeGenerator.generate_code_from_structure(structure)
class CodeGenerator:
    """YAMLテンプレートから実行可能なPythonコードを生成するクラス"""
    
    @staticmethod
    def parse_yaml_structure(yaml_content: str) -> Dict:
        """YAMLコンテンツを解析してディクショナリに変換する"""
        return yaml.safe_load(yaml_content)
    
    @staticmethod
    def generate_function(func_def: Dict) -> str:
        """関数定義からコードを生成"""
        name = func_def.get("name", "unnamed_function")
        params = func_def.get("parameters", "")
        returns = func_def.get("returns", "")
        description = func_def.get("description", "")
        
        param_str = "" if params is None else ", ".join(params) if isinstance(params, list) else str(params)
        return_annotation = "" if returns is None else f" -> {returns}"
        
        code_blocks = []
        if "code" in func_def:
            for code_item in func_def["code"]:
                if isinstance(code_item, str):
                    code_blocks.append(f"    {code_item}")
                elif isinstance(code_item, dict) and "function" in code_item:
                    # ネストされた関数
                    nested_func = CodeGenerator.generate_function(code_item["function"])
                    # インデントを追加
                    nested_func = "\n".join(f"    {line}" for line in nested_func.split("\n"))
                    code_blocks.append(nested_func)
        
        docstring = f'    """{description}"""' if description else ""
        
        if code_blocks:
            code_content = "\n".join(code_blocks)
        else:
            code_content = "    pass"
        
        func_code = [
            f"def {name}({param_str}){return_annotation}:"
        ]
        
        if docstring:
            func_code.append(docstring)
        
        func_code.append(code_content)
        return "\n".join(func_code)
    
    @staticmethod
    def generate_class(class_def: Dict) -> str:
        """クラス定義からコードを生成"""
        name = class_def.get("name", "UnnamedClass")
        description = class_def.get("description", "")
        inherits = class_def.get("inherits", "")
        
        inherit_str = f"({inherits})" if inherits else ""
        
        code_blocks = []
        if "code_structure" in class_def:
            for item in class_def["code_structure"]:
                if isinstance(item, str):
                    code_blocks.append(f"    {item}")
                elif isinstance(item, dict):
                    if "function" in item:
                        # メソッド定義
                        method_code = CodeGenerator.generate_function(item["function"])
                        # インデントを追加
                        method_code = "\n".join(f"    {line}" for line in method_code.split("\n"))
                        code_blocks.append(method_code)
                    elif "class" in item:
                        # ネストされたクラス
                        nested_class = CodeGenerator.generate_class(item["class"])
                        # インデントを追加
                        nested_class = "\n".join(f"    {line}" for line in nested_class.split("\n"))
                        code_blocks.append(nested_class)
        
        docstring = f'    """{description}"""' if description else ""
        
        if code_blocks:
            code_content = "\n\n".join(code_blocks)
        else:
            code_content = "    pass"
        
        class_code = [
            f"class {name}{inherit_str}:"
        ]
        
        if docstring:
            class_code.append(docstring)
        
        class_code.append(code_content)
        return "\n".join(class_code)
    
    @staticmethod
    def generate_code_from_structure(structure: Dict) -> str:
        """YAMLの構造からコード全体を生成"""
        name = structure.get("name", "Unnamed Project")
        description = structure.get("description", "")
        
        # ヘッダーコメントを追加
        code = [f"# {name}", f"# {'-' * len(name)}", f"# {description}", ""]
        
        if "code_structure" in structure:
            for item in structure["code_structure"]:
                if isinstance(item, str):
                    code.append(item)
                elif isinstance(item, dict):
                    if "function" in item:
                        code.append(CodeGenerator.generate_function(item["function"]))
                    elif "class" in item:
                        code.append(CodeGenerator.generate_class(item["class"]))
        
        return "\n\n".join(code)
    
    @staticmethod
    def save_to_file(code: str, file_path: str) -> None:
        """生成されたコードをファイルに保存"""
        with open(file_path, "w") as f:
            f.write(code)
        print(f"コードが {file_path} に保存されました。")

class YAMLCodeTool:
    """YAMLからコードを生成するためのツール"""
    
    @staticmethod
    async def generate_from_yaml(yaml_content: str, output_file: Optional[str] = None) -> str:
        """YAMLコンテンツからコードを生成"""
        try:
            structure = CodeGenerator.parse_yaml_structure(yaml_content)
            generated_code = CodeGenerator.generate_code_from_structure(structure)
            
            if output_file:
                CodeGenerator.save_to_file(generated_code, output_file)
                
            return generated_code
        except Exception as e:
            return f"コード生成中にエラーが発生しました: {str(e)}"
    
    @staticmethod
    async def generate_from_yaml_file(yaml_file_path: str, output_file: Optional[str] = None) -> str:
        """YAMLファイルからコードを生成"""
        try:
            with open(yaml_file_path, "r") as f:
                yaml_content = f.read()
                
            return await YAMLCodeTool.generate_from_yaml(yaml_content, output_file)
        except Exception as e:
            return f"ファイル処理中にエラーが発生しました: {str(e)}"
