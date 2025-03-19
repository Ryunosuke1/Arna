#!/usr/bin/env python3
"""
Arna - Agent Core

このモジュールはArnaエージェントのコア機能を提供します。
タスクの状態管理、タスクの計画と分割、エージェントの記憶と状態管理、
タスクの実行制御などの機能を実装しています。
"""

import uuid
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field

# ロガーの設定
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """タスクの状態を表す列挙型"""
    PENDING = "pending"       # 保留中
    PLANNING = "planning"     # 計画中
    IN_PROGRESS = "in_progress"  # 実行中
    COMPLETED = "completed"   # 完了
    FAILED = "failed"         # 失敗
    CANCELLED = "cancelled"   # キャンセル


@dataclass
class Task:
    """タスクの基本単位を表すクラス"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    parent_id: Optional[str] = None
    subtasks: List['Task'] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_subtask(self, name: str, description: str) -> 'Task':
        """
        サブタスクを追加します。
        
        Args:
            name: タスク名
            description: タスクの説明
            
        Returns:
            作成されたサブタスク
        """
        subtask = Task(
            name=name,
            description=description,
            parent_id=self.id
        )
        self.subtasks.append(subtask)
        return subtask
    
    def update_status(self, status: TaskStatus) -> None:
        """
        タスクの状態を更新します。
        
        Args:
            status: 新しいタスク状態
        """
        self.status = status
        self.updated_at = time.time()
        
        if status == TaskStatus.COMPLETED:
            self.completed_at = time.time()
    
    def is_completed(self) -> bool:
        """
        タスクが完了しているかを確認します。
        
        Returns:
            タスクが完了している場合はTrue
        """
        return self.status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """
        タスクが失敗したかを確認します。
        
        Returns:
            タスクが失敗した場合はTrue
        """
        return self.status == TaskStatus.FAILED
    
    def get_all_subtasks(self) -> List['Task']:
        """
        すべてのサブタスク（再帰的に）を取得します。
        
        Returns:
            すべてのサブタスクのリスト
        """
        result = []
        for subtask in self.subtasks:
            result.append(subtask)
            result.extend(subtask.get_all_subtasks())
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        タスクを辞書形式に変換します。
        
        Returns:
            タスクの辞書表現
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "subtasks": [subtask.to_dict() for subtask in self.subtasks],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        辞書からタスクを生成します。
        
        Args:
            data: タスクの辞書表現
            
        Returns:
            生成されたTaskインスタンス
        """
        task = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "pending")),
            parent_id=data.get("parent_id"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            completed_at=data.get("completed_at"),
            metadata=data.get("metadata", {})
        )
        
        # サブタスクの読み込み
        for subtask_data in data.get("subtasks", []):
            subtask = Task.from_dict(subtask_data)
            task.subtasks.append(subtask)
        
        return task


class TaskPlanner:
    """タスクの計画と分割を行うクラス"""
    
    def __init__(self, llm_service=None):
        """
        TaskPlannerを初期化します。
        
        Args:
            llm_service: LLMサービスのインスタンス（省略可）
        """
        self.llm_service = llm_service
    
    def create_task(self, name: str, description: str) -> Task:
        """
        新しいタスクを作成します。
        
        Args:
            name: タスク名
            description: タスクの説明
            
        Returns:
            作成されたタスク
        """
        return Task(name=name, description=description)
    
    def plan_task(self, task: Task, complexity_level: int = 1) -> Task:
        """
        タスクの計画を立て、必要に応じてサブタスクに分割します。
        
        Args:
            task: 計画対象のタスク
            complexity_level: 複雑さのレベル（1-5、大きいほど詳細に分割）
            
        Returns:
            計画されたタスク
        """
        task.update_status(TaskStatus.PLANNING)
        
        # LLMサービスが利用可能な場合、それを使用してタスク分割
        if self.llm_service:
            subtasks_data = self._generate_subtasks_with_llm(task, complexity_level)
            for subtask_data in subtasks_data:
                task.add_subtask(
                    name=subtask_data.get("name", ""),
                    description=subtask_data.get("description", "")
                )
        else:
            # LLMサービスがない場合は、基本的な分割ロジックを使用
            self._generate_basic_subtasks(task, complexity_level)
        
        task.update_status(TaskStatus.IN_PROGRESS)
        return task
    
    def _generate_subtasks_with_llm(self, task: Task, complexity_level: int) -> List[Dict[str, str]]:
        """
        LLMを使用してサブタスクを生成します。
        
        Args:
            task: 親タスク
            complexity_level: 複雑さのレベル
            
        Returns:
            サブタスクデータのリスト
        """
        if not self.llm_service:
            return []
        
        prompt = f"""
        タスク「{task.name}」の計画を立ててください。
        
        タスクの説明:
        {task.description}
        
        複雑さレベル: {complexity_level}/5
        
        このタスクを完了するために必要なサブタスクのリストを作成してください。
        各サブタスクには名前と説明を含めてください。
        複雑さレベルに応じて、適切な詳細度でサブタスクを分割してください。
        
        出力形式:
        [
            {{"name": "サブタスク1の名前", "description": "サブタスク1の説明"}},
            {{"name": "サブタスク2の名前", "description": "サブタスク2の説明"}},
            ...
        ]
        """
        
        try:
            response = self.llm_service.generate_text(prompt)
            subtasks_data = self.llm_service.parse_json_response(response)
            return subtasks_data if isinstance(subtasks_data, list) else []
        except Exception as e:
            logger.error(f"LLMを使用したサブタスク生成中にエラーが発生しました: {e}")
            return []
    
    def _generate_basic_subtasks(self, task: Task, complexity_level: int) -> None:
        """
        基本的なロジックを使用してサブタスクを生成します。
        
        Args:
            task: 親タスク
            complexity_level: 複雑さのレベル
        """
        # 基本的なソフトウェア開発タスクの分割例
        if "開発" in task.name or "実装" in task.name:
            task.add_subtask("要件分析", "機能の要件を分析し、明確にする")
            task.add_subtask("設計", "機能の設計を行う")
            task.add_subtask("実装", "コードを実装する")
            task.add_subtask("テスト", "機能をテストする")
            task.add_subtask("文書化", "機能の使用方法を文書化する")
        elif "テスト" in task.name:
            task.add_subtask("テスト計画", "テスト計画を作成する")
            task.add_subtask("テストケース作成", "テストケースを作成する")
            task.add_subtask("テスト実行", "テストを実行する")
            task.add_subtask("バグ修正", "発見されたバグを修正する")
        elif "設計" in task.name:
            task.add_subtask("要件確認", "設計に必要な要件を確認する")
            task.add_subtask("アーキテクチャ設計", "全体アーキテクチャを設計する")
            task.add_subtask("詳細設計", "詳細設計を行う")
            task.add_subtask("レビュー", "設計のレビューを行う")
        else:
            # 一般的なタスク分割
            task.add_subtask("計画", f"{task.name}の計画を立てる")
            task.add_subtask("実行", f"{task.name}を実行する")
            task.add_subtask("検証", f"{task.name}の結果を検証する")


class MemoryManager:
    """エージェントの記憶と状態を管理するクラス"""
    
    def __init__(self):
        """MemoryManagerを初期化します。"""
        self.short_term_memory: Dict[str, Any] = {}
        self.long_term_memory: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []
    
    def remember(self, key: str, value: Any, long_term: bool = False) -> None:
        """
        情報を記憶します。
        
        Args:
            key: 記憶のキー
            value: 記憶する値
            long_term: 長期記憶として保存するかどうか
        """
        self.short_term_memory[key] = value
        
        if long_term:
            self.long_term_memory[key] = value
    
    def recall(self, key: str, default: Any = None) -> Any:
        """
        記憶を思い出します。
        
        Args:
            key: 記憶のキー
            default: キーが存在しない場合のデフォルト値
            
        Returns:
            記憶された値、またはデフォルト値
        """
        # まず短期記憶から検索
        if key in self.short_term_memory:
            return self.short_term_memory[key]
        
        # 次に長期記憶から検索
        if key in self.long_term_memory:
            # 見つかった場合は短期記憶にも追加
            value = self.long_term_memory[key]
            self.short_term_memory[key] = value
            return value
        
        return default
    
    def forget(self, key: str, long_term: bool = False) -> None:
        """
        記憶を忘れます。
        
        Args:
            key: 記憶のキー
            long_term: 長期記憶からも削除するかどうか
        """
        if key in self.short_term_memory:
            del self.short_term_memory[key]
        
        if long_term and key in self.long_term_memory:
            del self.long_term_memory[key]
    
    def clear_short_term_memory(self) -> None:
        """短期記憶をクリアします。"""
        self.short_term_memory.clear()
    
    def add_task_to_history(self, task: Task) -> None:
        """
        タスクを履歴に追加します。
        
        Args:
            task: 追加するタスク
        """
        self.task_history.append(task.to_dict())
    
    def get_task_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        タスク履歴を取得します。
        
        Args:
            limit: 取得する履歴の最大数
            
        Returns:
            タスク履歴のリスト
        """
        if limit is None:
            return self.task_history
        return self.task_history[-limit:]
    
    def get_memory_snapshot(self) -> Dict[str, Any]:
        """
        現在の記憶の状態のスナップショットを取得します。
        
        Returns:
            記憶の状態を表す辞書
        """
        return {
            "short_term_memory": self.short_term_memory.copy(),
            "long_term_memory": self.long_term_memory.copy(),
            "task_history_count": len(self.task_history)
        }


class ExecutionEngine:
    """タスクの実行を制御するクラス"""
    
    def __init__(self, memory_manager: MemoryManager = None, llm_service=None):
        """
        ExecutionEngineを初期化します。
        
        Args:
            memory_manager: 記憶管理のインスタンス（省略可）
            llm_service: LLMサービスのインスタンス（省略可）
        """
        self.memory_manager = memory_manager or MemoryManager()
        self.llm_service = llm_service
        self.tool_registry: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, tool_function: Callable) -> None:
        """
        ツールを登録します。
        
        Args:
            name: ツール名
            tool_function: ツール関数
        """
        self.tool_registry[name] = tool_function
    
    def execute_task(self, task: Task) -> bool:
        """
        タスクを実行します。
        
        Args:
            task: 実行するタスク
            
        Returns:
            タスクが成功したかどうか
        """
        logger.info(f"タスク実行開始: {task.name}")
        task.update_status(TaskStatus.IN_PROGRESS)
        
        # サブタスクがある場合は、それらを実行
        if task.subtasks:
            all_success = True
            for subtask in task.subtasks:
                success = self.execute_task(subtask)
                if not success:
                    all_success = False
            
            # すべてのサブタスクの結果に基づいてタスクの状態を更新
            if all_success:
                task.update_status(TaskStatus.COMPLETED)
                logger.info(f"タスク完了: {task.name}")
            else:
                task.update_status(TaskStatus.FAILED)
                logger.warning(f"タスク失敗: {task.name} (サブタスクの失敗)")
            
            return all_success
        
        # サブタスクがない場合は、LLMを使用してタスクを実行
        try:
            if self.llm_service:
                success = self._execute_with_llm(task)
            else:
                # LLMがない場合は、基本的な実行ロジックを使用
                success = self._execute_basic(task)
            
            if success:
                task.update_status(TaskStatus.COMPLETED)
                logger.info(f"タスク完了: {task.name}")
            else:
                task.update_status(TaskStatus.FAILED)
                logger.warning(f"タスク失敗: {task.name}")
            
            # タスク履歴に追加
            if self.memory_manager:
                self.memory_manager.add_task_to_history(task)
            
            return success
        
        except Exception as e:
            logger.error(f"タスク実行中にエラーが発生: {task.name} - {str(e)}")
            task.update_status(TaskStatus.FAILED)
            task.metadata["error"] = str(e)
            
            # タスク履歴に追加
            if self.memory_manager:
                self.memory_manager.add_task_to_history(task)
            
            return False
    
    def _execute_with_llm(self, task: Task) -> bool:
        """
        LLMを使用してタスクを実行します。
        
        Args:
            task: 実行するタスク
            
        Returns:
            タスクが成功したかどうか
        """
        if not self.llm_service:
            return False
        
        # タスクの実行計画を生成
        prompt = f"""
        タスク「{task.name}」を実行する計画を立ててください。
        
        タスクの説明:
        {task.description}
        
        利用可能なツール:
        {', '.join(self.tool_registry.keys())}
        
        このタスクを完了するために必要な手順と、各手順で使用するツールを指定してください。
        
        出力形式:
        [
            {{"step": "手順1の説明", "tool": "ツール名", "parameters": {{"パラメータ名": "値"}}}},
            {{"step": "手順2の説明", "tool": "ツール名", "parameters": {{"パラメータ名": "値"}}}},
            ...
        ]
        """
        
        try:
            response = self.llm_service.generate_text(prompt)
            steps = self.llm_service.parse_json_response(response)
            
            if not isinstance(steps, list):
                logger.error(f"LLMからの応答が不正な形式です: {response}")
                return False
            
            # 各ステップを実行
            for i, step in enumerate(steps):
                step_desc = step.get("step", f"ステップ{i+1}")
                tool_name = step.get("tool")
                parameters = step.get("parameters", {})
                
                logger.info(f"ステップ実行: {step_desc}")
                
                if tool_name and tool_name in self.tool_registry:
                    tool_func = self.tool_registry[tool_name]
                    result = tool_func(**parameters)
                    
                    # 結果をメモリに保存
                    if self.memory_manager:
                        self.memory_manager.remember(f"step_{i}_result", result)
                else:
                    logger.warning(f"ツール '{tool_name}' が見つかりません")
            
            # タスクの結果を評価
            evaluation_prompt = f"""
            タスク「{task.name}」の実行結果を評価してください。
            
            タスクの説明:
            {task.description}
            
            実行された手順:
            {str(steps)}
            
            このタスクは正常に完了しましたか？ "yes" または "no" で回答してください。
            """
            
            evaluation = self.llm_service.generate_text(evaluation_prompt).strip().lower()
            return "yes" in evaluation
            
        except Exception as e:
            logger.error(f"LLMを使用したタスク実行中にエラーが発生しました: {e}")
            return False
    
    def _execute_basic(self, task: Task) -> bool:
        """
        基本的なロジ<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>