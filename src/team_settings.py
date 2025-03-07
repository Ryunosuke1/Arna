import flet as ft
from typing import List, Callable, Optional
from dataclasses import dataclass

from agents import CodingAssistant

class VyTheme:
    """Vyスタイルのカラーテーマ"""
    PRIMARY = "#007BFF"
    SECONDARY = "#2196F3"
    BACKGROUND = "#F8F9FA"
    CARD_BG = "#FFFFFF"
    TEXT_FIELD_BG = "#F8F9FA"
    BORDER_COLOR = "#E9ECEF"
    TEXT_COLOR = "#495057"

class TeamMemberSettings:
    def __init__(
        self,
        on_save: Callable[[List[CodingAssistant]], None],
        initial_members: Optional[List[CodingAssistant]] = None
    ):
        self.on_save = on_save
        self.members = initial_members or []
        
        # 必須メンバー
        self.coding_assistant = CodingAssistant(
            api_key="",
            name="coding assistant",
            desc="A coding assistant that can generate python code structure based on the specification."
        )
        
        self.critic = CodingAssistant(
            api_key="",
            name="critic",
            desc="Provide constructive feedback and approve when requirements are met."
        )
        
        # UI コンポーネント
        self.base_url = ft.TextField(
            label="Base URL",
            value="",
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True
        )
        
        self.api_key = ft.TextField(
            label="API Key",
            value="",
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True
        )
        
        self.model_name = ft.TextField(
            label="Model Name",
            value="deepseek-r1",
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True
        )
        
        self.max_tokens = ft.TextField(
            label="Max Tokens",
            value="4096",
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        
        self.context_length = ft.TextField(
            label="Context Length",
            value="8192",
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        
        # 追加メンバーのリスト
        self.member_list = ft.Column(spacing=10)
        
        # 追加メンバー用のフォーム
        self.new_member_name = ft.TextField(
            label="Name",
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True
        )
        
        self.new_member_desc = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True
        )
    
    def build(self) -> ft.Container:
        """Team Member設定画面を構築"""
        return ft.Container(
            content=ft.Column([
                # 基本設定セクション
                self._build_base_settings(),
                ft.Divider(height=20, color=VyTheme.BORDER_COLOR),
                
                # 必須メンバーセクション
                self._build_required_members(),
                ft.Divider(height=20, color=VyTheme.BORDER_COLOR),
                
                # 追加メンバーセクション
                self._build_additional_members(),
                
                # 保存ボタン
                ft.ElevatedButton(
                    text="設定を保存",
                    on_click=self._handle_save,
                    style=ft.ButtonStyle(
                        bgcolor=VyTheme.PRIMARY,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=12)
                    )
                )
            ],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,  # 親コンテナいっぱいに広がる
            )
        )
    
    def _build_base_settings(self) -> ft.Container:
        """基本設定セクションを構築"""
        return ft.Container(
            content=ft.Column([
                ft.Text("基本設定", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([ft.Text("Base URL:"), self.base_url], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Text("API Key:"), self.api_key], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Text("Model Name:"), self.model_name], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Text("Max Tokens:"), self.max_tokens], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Text("Context Length:"), self.context_length], alignment=ft.MainAxisAlignment.CENTER),
            ]),
            bgcolor=VyTheme.CARD_BG,
            padding=20,
            border_radius=12
        )
    
    def _build_required_members(self) -> ft.Container:
        """必須メンバーセクションを構築"""
        return ft.Container(
            content=ft.Column([
                ft.Text("必須メンバー", size=18, weight=ft.FontWeight.BOLD),
                self._build_member_card(
                    "Coding Assistant",
                    self.coding_assistant.desc,
                    True
                ),
                self._build_member_card(
                    "Critic",
                    self.critic.desc,
                    True
                )
            ]),
            bgcolor=VyTheme.CARD_BG,
            padding=20,
            border_radius=12
        )
    
    def _build_additional_members(self) -> ft.Container:
        """追加メンバーセクションを構築"""
        return ft.Container(
            content=ft.Column([
                ft.Text("追加メンバー", size=18, weight=ft.FontWeight.BOLD),
                self.member_list,
                # 新規メンバー追加フォーム
                ft.Container(
                    content=ft.Column([
                        self.new_member_name,
                        self.new_member_desc,
                        ft.ElevatedButton(
                            text="メンバーを追加",
                            on_click=self._handle_add_member,
                            style=ft.ButtonStyle(
                                bgcolor=VyTheme.SECONDARY,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=12)
                            )
                        )
                    ]),
                    bgcolor=VyTheme.CARD_BG,
                    padding=20,
                    border_radius=12
                )
            ])
        )
    
    def _build_member_card(
        self,
        name: str,
        description: str,
        is_required: bool = False
    ) -> ft.Card:
        """メンバーカードを構築"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            name,
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Required",
                            color=VyTheme.SECONDARY,
                            italic=True
                        ) if is_required else None
                    ]),
                    ft.Text(description)
                ]),
                padding=10
            )
        )
    
    async def _handle_add_member(self, e):
        """新しいメンバーを追加"""
        if self.new_member_name.value and self.new_member_desc.value:
            # 数値設定の変換
            try:
                max_tokens = int(self.max_tokens.value)
                context_length = int(self.context_length.value)
            except ValueError:
                max_tokens = 4096
                context_length = 8192

            member = CodingAssistant(
                api_key=self.api_key.value,
                base_url=self.base_url.value,
                model_name=self.model_name.value,
                name=self.new_member_name.value,
                desc=self.new_member_desc.value,
                max_tokens=max_tokens,
                context_length=context_length
            )
            
            self.members.append(member)
            self.member_list.controls.append(
                self._build_member_card(member.name, member.desc)
            )
            
            # フォームをクリア
            self.new_member_name.value = ""
            self.new_member_desc.value = ""
            
            await self.member_list.update_async()
    
    async def _handle_save(self, e):
        """設定を保存"""
        # 数値設定の変換
        try:
            max_tokens = int(self.max_tokens.value)
            context_length = int(self.context_length.value)
        except ValueError:
            max_tokens = 4096
            context_length = 8192
        
        # 必須メンバーの更新
        self.coding_assistant.api_key = self.api_key.value
        self.coding_assistant.base_url = self.base_url.value
        self.coding_assistant.model_name = self.model_name.value
        self.coding_assistant.max_tokens = max_tokens
        self.coding_assistant.context_length = context_length
        
        self.critic.api_key = self.api_key.value
        self.critic.base_url = self.base_url.value
        self.critic.model_name = self.model_name.value
        self.critic.max_tokens = max_tokens
        self.critic.context_length = context_length
        
        # 全メンバーをリストにまとめる
        all_members = [self.coding_assistant, self.critic] + self.members
        
        # コールバックを呼び出し
        await self.on_save(all_members)
