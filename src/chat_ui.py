import flet as ft
from typing import List, Optional, Callable, Dict
from tools import Question

class VyTheme:
    """Vyスタイルのカラーテーマ"""
    PRIMARY = "#007BFF"          # Vyブルー
    SECONDARY = "#2196F3"        # 補助的なブルー
    BACKGROUND = "#F8F9FA"       # 背景色
    CARD_BG = "#FFFFFF"          # カード背景
    TEXT_FIELD_BG = "#F8F9FA"    # 入力フィールド背景
    BORDER_COLOR = "#E9ECEF"     # ボーダー色
    TEXT_COLOR = "#495057"       # テキスト色
    
    # メッセージタイプ別の色
    QUESTION_BG = PRIMARY
    QUESTION_TEXT = "#FFFFFF"
    USER_BG = TEXT_FIELD_BG
    USER_TEXT = TEXT_COLOR
    AGENT_BG = SECONDARY
    AGENT_TEXT = "#FFFFFF"

class Message:
    """メッセージを表すクラス"""
    def __init__(
        self,
        content: str,
        message_type: str = "user",
        sender: str = "User",
        metadata: Optional[Dict] = None
    ):
        self.content = content
        self.message_type = message_type
        self.sender = sender
        self.metadata = metadata or {}

class ChatUI:
    def __init__(
        self,
        on_send: Callable[[str], None],
        on_toggle: Callable[[], None]
    ):
        self.on_send = on_send
        self.on_toggle = on_toggle
        self.messages: List[Message] = []
        
        # UIコンポーネント
        self.messages_view = ft.Column(
            spacing=15,
            scroll=ft.ScrollMode.ALWAYS,  # 常にスクロール可能
            auto_scroll=True,
            expand=True  # 親コンテナいっぱいに広がる
        )
        
        self.input_field = ft.TextField(
            hint_text="メッセージを入力",
            expand=1,
            border_radius=12,
            bgcolor=VyTheme.TEXT_FIELD_BG,
            border_color=VyTheme.BORDER_COLOR,
            content_padding=15,
            filled=True,
            on_submit=self._handle_send
        )
        
        self.send_button = ft.ElevatedButton(
            text="Send",
            icon=ft.Icons.SEND,
            icon_color=ft.Colors.WHITE,
            on_click=self._handle_send,
            style=ft.ButtonStyle(bgcolor=VyTheme.PRIMARY)
        )
        
        self.toggle_button = ft.ElevatedButton(
            text="一時停止",
            on_click=lambda _: self.on_toggle(),
            style=ft.ButtonStyle(
                bgcolor=VyTheme.PRIMARY,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=12)
            )
        )
    
    def build(self) -> ft.Container:
        """チャットUIを構築"""
        return ft.Container(
            content=ft.Column([
                # メッセージ表示エリア
                ft.Container(
                    content=self.messages_view,
                    bgcolor=VyTheme.BACKGROUND,
                    padding=20,
                    border_radius=12,
                    expand=True,
                ),
                # 入力エリア
                ft.Row([
                    self.input_field,
                    self.send_button,
                    self.toggle_button
                ], spacing=15)
            ],
            expand=True,  # 親コンテナいっぱいに広がる
            scroll=ft.ScrollMode.ALWAYS  # 常にスクロール可能
            )
        )
    
    def _handle_send(self, e):
        """送信ボタンのクリックまたはEnterキー押下時の処理"""
        if message := self.input_field.value.strip():
            self.add_user_message(message)
            self.input_field.value = ""
            self.input_field.update()
            self.on_send(message)
    
    def _create_message_container(self, message: Message) -> ft.Container:
        """メッセージコンテナを作成"""
        if message.message_type == "question":
            bg_color = VyTheme.QUESTION_BG
            text_color = VyTheme.QUESTION_TEXT
        elif message.message_type == "user":
            bg_color = VyTheme.USER_BG
            text_color = VyTheme.USER_TEXT
        else:
            bg_color = VyTheme.AGENT_BG
            text_color = VyTheme.AGENT_TEXT
        
        content_controls = [
            ft.Text(
                message.sender,
                color=text_color,
                weight=ft.FontWeight.BOLD,
                size=14
            ),
            ft.Text(
                message.content,
                color=text_color
            )
        ]
        
        # メタデータがある場合は追加
        if message.metadata:
            for key, value in message.metadata.items():
                content_controls.append(
                    ft.Text(
                        f"{key}: {value}",
                        color=text_color,
                        size=12,
                        italic=True
                    )
                )
        
        return ft.Container(
            content=ft.Column(content_controls),
            bgcolor=bg_color,
            padding=15,
            border_radius=12
        )
    
    def add_question(self, question: Question):
        """エージェントからの質問を表示"""
        message = Message(
            content=question.content,
            message_type="question",
            sender=f"Question {question.number}",
            metadata={
                "Category": question.category,
                "From": question.agent_name
            }
        )
        self.messages.append(message)
        
        self.messages_view.controls.append(
            self._create_message_container(message)
        )
        # メッセージビューを更新
        self.messages_view.update()
    
    def add_user_message(self, content: str):
        """ユーザーのメッセージを表示"""
        message = Message(content=content)
        self.messages.append(message)
        
        self.messages_view.controls.append(
            self._create_message_container(message)
        )
        self.messages_view.update()
    
    def add_agent_message(self, content: str, agent_name: str):
        """エージェントのメッセージを表示"""
        message = Message(
            content=content,
            message_type="agent",
            sender=agent_name
        )
        self.messages.append(message)
        
        self.messages_view.controls.append(
            self._create_message_container(message)
        )
        self.messages_view.update()
