import flet as ft
from typing import List, Optional, Callable, Dict, Any
from chat_ui import ChatUI, VyTheme
from tools import QuestionManager, Question

class DiscussionView:
    """チャットビューを管理するクラス"""
    def __init__(
        self,
        question_manager: QuestionManager,
        on_message: Callable[[str], None],
        on_toggle: Callable[[], None]
    ):
        self.question_manager = question_manager
        self.on_message = on_message
        self.on_toggle = on_toggle
        
        # チャットUIの初期化
        self.chat_ui = ChatUI(
            on_send=self._handle_message,
            on_toggle=on_toggle
        )
    
    def build(self) -> ft.Column:
        """ディスカッションビューを構築"""
        return self.chat_ui.build()
    
    def _handle_message(self, message: str):
        """
        メッセージを処理する
        
        1. 質問への回答として処理
        2. エージェントにメッセージを転送
        """
        try:
            # 現在の質問がある場合は回答として処理
            if self.question_manager and self.question_manager._current_question:
                self.question_manager.answer_current_question(message)
                # 次の質問を表示（存在する場合）
                next_question = self.question_manager.get_next_question()
                if next_question:
                    self.add_question(next_question)
            
            # エージェントにメッセージを転送
            self.on_message(message)
        except Exception as e:
            self.chat_ui.add_agent_message(f"Error: {str(e)}", "System")
    
    def add_question(self, question: Question):
        """質問を表示"""
        self.chat_ui.add_question(question)
    
    def add_agent_message(self, content: str, agent_name: str):
        """エージェントのメッセージを表示"""
        self.chat_ui.add_agent_message(content, agent_name)
    
    def set_processing(self, processing: bool):
        """処理中の状態を設定"""
        self.chat_ui.input_field.disabled = processing
        self.chat_ui.send_button.disabled = processing
        if processing:
            self.chat_ui.toggle_button.text = "停止"
        else:
            self.chat_ui.toggle_button.text = "一時停止"
