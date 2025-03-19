"""
Agent Core Module

このモジュールはエージェントの中核機能と意思決定ロジックを提供します。
タスクの分解と計画立案、実行制御、メモリ管理などの機能を含みます。
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum


class TaskStatus(Enum):
    """タスクの状態を表す列挙型"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """タスクを表すクラス"""
    
    def __init__(self, task_id: str, description: str, parent_id: Optional[str] = None):
        """
        タスクの初期化
        
        Args:
            task_id: タスクID
            description: タスクの説明
            parent_id: 親タスクのID (オプション)
        """
        self.task_id = task_id
        self.description = description
        self.parent_id = parent_id
        self.status = TaskStatus.PENDING
        self.subtasks: List[Task] = []
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
    
    def start(self) -> None:
        """タスクを開始状態に設定"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = time.time()
    
    def complete(self, result: Optional[Any] = None) -> None:
        """
        タスクを完了状態に設定
        
        Args:
            result: タスクの結果 (オプション)
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result
    
    def fail(self, error: str) -> None:
        """
        タスクを失敗状態に設定
        
        Args:
            error: エラーメッセージ
        """
        self.status = TaskStatus.FAILED
        self.completed_at = time.time()
        self.error = error
    
    def add_subtask(self, subtask: 'Task') -> None:
        """
        サブタスクを追加
        
        Args:
            subtask: 追加するサブタスク
        """
        self.subtasks.append(subtask)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        タスクを辞書形式に変換
        
        Returns:
            タスクの辞書表現
        """
        return {
            "task_id": self.task_id,
            "description": self.description,
            "parent_id": self.parent_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "subtasks": [subtask.to_dict() for subtask in self.subtasks]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        辞書からタスクを作成
        
        Args:
            data: タスクの辞書表現
            
        Returns:
            作成されたタスク
        """
        task = cls(data["task_id"], data["description"], data.get("parent_id"))
        task.status = TaskStatus(data["status"])
        task.created_at = data["created_at"]
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.result = data.get("result")
        task.error = data.get("error")
        
        for subtask_data in data.get("subtasks", []):
            task.add_subtask(cls.from_dict(subtask_data))
        
        return task


class TaskPlanner:
    """タスクの分解と計画立案を行うクラス"""
    
    def __init__(self):
        """TaskPlannerの初期化"""
        self.next_task_id = 1
    
    def create_task(self, description: str, parent_id: Optional[str] = None) -> Task:
        """
        新しいタスクを作成
        
        Args:
            description: タスクの説明
            parent_id: 親タスクのID (オプション)
            
        Returns:
            作成されたタスク
        """
        task_id = f"task_{self.next_task_id}"
        self.next_task_id += 1
        return Task(task_id, description, parent_id)
    
    def decompose_task(self, task: Task, subtask_descriptions: List[str]) -> List[Task]:
        """
        タスクをサブタスクに分解
        
        Args:
            task: 分解するタスク
            subtask_descriptions: サブタスクの説明リスト
            
        Returns:
            作成されたサブタスクのリスト
        """
        subtasks = []
        for description in subtask_descriptions:
            subtask = self.create_task(description, task.task_id)
            task.add_subtask(subtask)
            subtasks.append(subtask)
        
        return subtasks
    
    def plan_execution(self, tasks: List[Task]) -> List[Task]:
        """
        タスクの実行計画を作成
        
        Args:
            tasks: 計画するタスクのリスト
            
        Returns:
            実行順序に並べられたタスクのリスト
        """
        # 単純な実装: 与えられた順序をそのまま返す
        # 実際の実装では依存関係などを考慮する
        return tasks


class MemoryManager:
    """エージェントの作業記憶と長期記憶を管理するクラス"""
    
    def __init__(self, memory_dir: str = ".memory"):
        """
        MemoryManagerの初期化
        
        Args:
            memory_dir: メモリを保存するディレクトリ
        """
        self.memory_dir = memory_dir
        self.working_memory: Dict[str, Any] = {}
        self.ensure_memory_dir()
    
    def ensure_memory_dir(self) -> None:
        """メモリディレクトリが存在することを確認"""
        os.makedirs(self.memory_dir, exist_ok=True)
    
    def set_working_memory(self, key: str, value: Any) -> None:
        """
        作業記憶に値を設定
        
        Args:
            key: キー
            value: 値
        """
        self.working_memory[key] = value
    
    def get_working_memory(self, key: str, default: Any = None) -> Any:
        """
        作業記憶から値を取得
        
        Args:
            key: キー
            default: キーが存在しない場合のデフォルト値
            
        Returns:
            取得した値またはデフォルト値
        """
        return self.working_memory.get(key, default)
    
    def save_long_term_memory(self, key: str, value: Any) -> None:
        """
        長期記憶に値を保存
        
        Args:
            key: キー
            value: 値
        """
        file_path = os.path.join(self.memory_dir, f"{key}.json")
        with open(file_path, 'w') as f:
            json.dump(value, f)
    
    def load_long_term_memory(self, key: str, default: Any = None) -> Any:
        """
        長期記憶から値を読み込み
        
        Args:
            key: キー
            default: キーが存在しない場合のデフォルト値
            
        Returns:
            読み込んだ値またはデフォルト値
        """
        file_path = os.path.join(self.memory_dir, f"{key}.json")
        if not os.path.exists(file_path):
            return default
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def list_long_term_memories(self) -> List[str]:
        """
        長期記憶のキーリストを取得
        
        Returns:
            長期記憶のキーリスト
        """
        self.ensure_memory_dir()
        files = os.listdir(self.memory_dir)
        return [os.path.splitext(f)[0] for f in files if f.endswith('.json')]


class ExecutionEngine:
    """タスク実行の制御を行うクラス"""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        ExecutionEngineの初期化
        
        Args:
            memory_manager: メモリマネージャ
        """
        self.memory_manager = memory_manager
        self.task_handlers: Dict[str, Callable[[Task], Any]] = {}
    
    def register_task_handler(self, task_type: str, handler: Callable[[Task], Any]) -> None:
        """
        タスクハンドラを登録
        
        Args:
            task_type: タスクタイプ
            handler: ハンドラ関数
        """
        self.task_handlers[task_type] = handler
    
    def execute_task(self, task: Task) -> None:
        """
        タスクを実行
        
        Args:
            task: 実行するタスク
        """
        # タスクタイプを説明から抽出（実際の実装ではより堅牢な方法が必要）
        task_type = task.description.split(':')[0] if ':' in task.description else "default"
        
        task.start()
        
        try:
            handler = self.task_handlers.get(task_type)
            if handler:
                result = handler(task)
                task.complete(result)
            else:
                # デフォルトの処理: サブタスクを順次実行
                for subtask in task.subtasks:
                    self.execute_task(subtask)
                task.complete()
        except Exception as e:
            task.fail(str(e))
    
    def execute_plan(self, tasks: List[Task]) -> None:
        """
        タスク計画を実行
        
        Args:
            tasks: 実行するタスクのリスト
        """
        for task in tasks:
            self.execute_task(task)


class AgentManager:
    """エージェント全体の調整と管理を行うクラス"""
    
    def __init__(self):
        """AgentManagerの初期化"""
        self.memory_manager = MemoryManager()
        self.task_planner = TaskPlanner()
        self.execution_engine = ExecutionEngine(self.memory_manager)
        self.current_task: Optional[Task] = None
    
    def process_instruction(self, instruction: str) -> Task:
        """
        ユーザー指示を処理
        
        Args:
            instruction: ユーザーからの指示
            
        Returns:
            作成されたタスク
        """
        # メインタスクを作成
        main_task = self.task_planner.create_task(instruction)
        self.current_task = main_task
        
        # タスクを分解（実際の実装ではLLMを使用）
        subtask_descriptions = [
            "分析: 指示を分析",
            "計画: 実行計画を作成",
            "実行: タスクを実行",
            "検証: 結果を検証",
            "報告: 結果を報告"
        ]
        
        self.task_planner.decompose_task(main_task, subtask_descriptions)
        
        return main_task
    
    def execute_current_task(self) -> Optional[Any]:
        """
        現在のタスクを実行
        
        Returns:
            タスクの結果
        """
        if not self.current_task:
            return None
        
        # タスク実行計画を作成
        plan = self.task_planner.plan_execution([self.current_task])
        
        # 計画を実行
        self.execution_engine.execute_plan(plan)
        
        return self.current_task.result
    
    def get_task_status(self) -> Dict[str, Any]:
        """
        現在のタスク状態を取得
        
        Returns:
            タスク状態の辞書表現
        """
        if not self.current_task:
            return {"status": "no_task"}
        
        return self.current_task.to_dict()
    
    def save_state(self) -> None:
        """エージェントの状態を保存"""
        if self.current_task:
            self.memory_manager.save_long_term_memory(
                "current_task", 
                self.current_task.to_dict()
            )
    
    def load_state(self) -> bool:
        """
        エージェントの状態を読み込み
        
        Returns:
            読み込みに成功したかどうか
        """
        task_data = self.memory_manager.load_long_term_memory("current_task")
        if task_data:
            self.current_task = Task.from_dict(task_data)
            return True
        return False
