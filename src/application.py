from typing import Optional, List
import asyncio
import yaml

from tools import QuestionManager
from chat_ui import ChatUI
from discussion import DiscussionView
from team_settings import TeamMemberSettings
from download_view import DownloadView
from agents import SharedData, CodingAssistant, CodingAssistants

class Application:
    """アプリケーション全体を管理するクラス"""

    def __init__(self):
        self.shared_data = SharedData()
        self.coding_assistants: Optional[CodingAssistants] = None
        
        # チャットビューの初期化
        self.discussion_view = DiscussionView(
            question_manager=self.shared_data.question_manager,
            on_message=self._handle_message,
            on_toggle=self._handle_toggle
        )
        self.shared_data.chat_ui = self.discussion_view.chat_ui
        
        # 設定ビューの初期化
        self.settings_view = TeamMemberSettings(
            on_save=self._handle_settings_save
        )
        
        # ダウンロードビューの初期化
        self.download_view = DownloadView()
        
        self.is_processing = False
    
    async def _process_agent_message(self, message: str):
        """エージェントとのメッセージ処理を行う非同期メソッド"""
        async for agent_message in self.coding_assistants.run(
            system_message="",  # エージェントはすでに初期化済み
            user_message=message
        ):
            if isinstance(agent_message, dict) and "content" in agent_message:
                # YAMLデータであれば処理
                try:
                    content = agent_message["content"]
                    if "code_structure:" in content:
                        yaml_data = yaml.safe_load(content)
                        # ダウンロードビューを更新
                        python_code = self.coding_assistants.code_tools.generate_code()
                        self.download_view.update_code(python_code, yaml_data)
                except:
                    pass  # YAML解析エラーは無視
                
                # メッセージを表示
                self.shared_data.chat_ui.add_agent_message(
                    agent_message["content"],
                    agent_message.get("name", "Agent")
                )
    
    def _handle_message(self, message: str):
        """
        メインのメッセージハンドラ
        非同期処理をイベントループで実行
        """
        if self.is_processing:
            return
        
        self.is_processing = True
        self.discussion_view.set_processing(True)
        
        try:
            if not self.coding_assistants:
                self._initialize_coding_assistants()
            
            # 非同期処理を実行
            asyncio.create_task(self._process_agent_message(message))
        
        except Exception as e:
            self.shared_data.chat_ui.add_agent_message(
                f"Error: {str(e)}",
                "System"
            )
        
        finally:
            self.is_processing = False
            self.discussion_view.set_processing(False)
    
    def _handle_toggle(self):
        """処理の一時停止/再開を切り替え"""
        if self.is_processing:
            if self.shared_data.external_termination:
                self.shared_data.external_termination.set()
            self.is_processing = False
            self.discussion_view.set_processing(False)
    
    async def _update_settings(self, members: List[CodingAssistant]):
        """設定の非同期更新処理"""
        self.shared_data.base_url = members[0].base_url
        self.shared_data.api_key = members[0].api_key
        self.shared_data.model_name = members[0].model_name
        
        # エージェントの再初期化
        self._initialize_coding_assistants()
        
        self.shared_data.chat_ui.add_agent_message(
            "Settings updated successfully",
            "System"
        )
    
    def _handle_settings_save(self, members: List[CodingAssistant]):
        """設定保存のメインハンドラ"""
        try:
            asyncio.create_task(self._update_settings(members))
        except Exception as e:
            self.shared_data.chat_ui.add_agent_message(
                f"Error updating settings: {str(e)}",
                "System"
            )
    
    def _initialize_coding_assistants(self):
        """Coding Assistantsを初期化"""
        # 必須エージェントの設定
        coding_agent = CodingAssistant(
            api_key=self.shared_data.api_key,
            base_url=self.shared_data.base_url,
            model_name=self.shared_data.model_name,
            name="coding assistant"
        )
        
        critic_agent = CodingAssistant(
            api_key=self.shared_data.api_key,
            base_url=self.shared_data.base_url,
            model_name=self.shared_data.model_name,
            name="critic",
            desc="Provide constructive feedback and approve when requirements are met."
        )
        
        # Coding Assistantsの初期化
        self.coding_assistants = CodingAssistants(
            planning_agents=[coding_agent, critic_agent],
            coding_agent=coding_agent,
            api_key=self.shared_data.api_key,
            base_url=self.shared_data.base_url,
            shared_data=self.shared_data
        )
