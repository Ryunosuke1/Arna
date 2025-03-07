import flet as ft
from typing import Callable, Optional
from chat_ui import VyTheme
import yaml

class DownloadView:
    """ダウンロードビューを管理するクラス"""
    def __init__(self, code_structure: Optional[dict] = None):
        self.code_structure = code_structure or {}
        
        # UI コンポーネント
        self.python_code = ft.TextField(
            multiline=True,
            read_only=True,
            max_lines=10,
            min_lines=5,
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True
        )
        
        self.yaml_code = ft.TextField(
            multiline=True,
            read_only=True,
            max_lines=10,
            min_lines=5,
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True
        )
    
    def build(self) -> ft.Column:
        """ダウンロードビューを構築"""
        return ft.Column([
            # Pythonコードセクション
            ft.Container(
                content=ft.Column([
                    ft.Text("Pythonコード", size=18, weight=ft.FontWeight.BOLD),
                    self.python_code,
                    ft.ElevatedButton(
                        text="Pythonファイルをダウンロード",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=self._handle_python_download,
                        style=ft.ButtonStyle(
                            bgcolor=VyTheme.PRIMARY,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12)
                        )
                    )
                ]),
                bgcolor=VyTheme.CARD_BG,
                padding=20,
                border_radius=12
            ),
            
            ft.Divider(height=20, color=VyTheme.BORDER_COLOR),
            
            # YAMLセクション
            ft.Container(
                content=ft.Column([
                    ft.Text("YAML構造", size=18, weight=ft.FontWeight.BOLD),
                    self.yaml_code,
                    ft.ElevatedButton(
                        text="YAMLファイルをダウンロード",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=self._handle_yaml_download,
                        style=ft.ButtonStyle(
                            bgcolor=VyTheme.PRIMARY,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12)
                        )
                    )
                ]),
                bgcolor=VyTheme.CARD_BG,
                padding=20,
                border_radius=12
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def update_code(self, python_code: str, yaml_data: dict):
        """コードを更新"""
        self.python_code.value = python_code
        self.yaml_code.value = yaml.dump(yaml_data, allow_unicode=True)
        self.code_structure = yaml_data
        self.python_code.update()
        self.yaml_code.update()
    
    async def _handle_python_download(self, e):
        """Pythonファイルのダウンロード処理"""
        try:
            # ファイルダイアログを開く
            result = await ft.FilePicker.save_file_async(
                dialog_title="Save Python File",
                file_name="generated_code.py",
                allowed_extensions=["py"]
            )
            
            if result is not None:
                with open(result, "w", encoding="utf-8") as f:
                    f.write(self.python_code.value)
        except Exception as ex:
            print(f"Error saving Python file: {str(ex)}")
    
    async def _handle_yaml_download(self, e):
        """YAMLファイルのダウンロード処理"""
        try:
            # ファイルダイアログを開く
            result = await ft.FilePicker.save_file_async(
                dialog_title="Save YAML File",
                file_name="code_structure.yaml",
                allowed_extensions=["yaml", "yml"]
            )
            
            if result is not None:
                with open(result, "w", encoding="utf-8") as f:
                    yaml.dump(self.code_structure, f, allow_unicode=True)
        except Exception as ex:
            print(f"Error saving YAML file: {str(ex)}")
