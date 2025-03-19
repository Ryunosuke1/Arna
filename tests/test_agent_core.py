"""
Agent Core コンポーネントのテスト

このモジュールはAgent Coreコンポーネントの機能をテストします。
"""

import os
import sys
import unittest
import tempfile
import json
import time

# テスト対象のモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.agent_core import AgentManager, TaskPlanner, MemoryManager, ExecutionEngine, Task, TaskStatus


class TestTask(unittest.TestCase):
    """Taskクラスのテストケース"""
    
    def test_task_initialization(self):
        """タスク初期化のテスト"""
        task = Task("task_1", "テストタスク", "parent_1")
        
        self.assertEqual(task.task_id, "task_1")
        self.assertEqual(task.description, "テストタスク")
        self.assertEqual(task.parent_id, "parent_1")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(len(task.subtasks), 0)
        self.assertIsNone(task.started_at)
        self.assertIsNone(task.completed_at)
        self.assertIsNone(task.result)
        self.assertIsNone(task.error)
    
    def test_task_lifecycle(self):
        """タスクライフサイクルのテスト"""
        task = Task("task_2", "ライフサイクルテスト")
        
        # 開始
        task.start()
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertIsNotNone(task.started_at)
        
        # 完了
        result = {"status": "success"}
        task.complete(result)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(task.result, result)
        
        # 新しいタスクで失敗をテスト
        task = Task("task_3", "失敗テスト")
        task.start()
        task.fail("エラーが発生しました")
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertEqual(task.error, "エラーが発生しました")
    
    def test_subtask_management(self):
        """サブタスク管理のテスト"""
        parent_task = Task("parent", "親タスク")
        subtask1 = Task("sub1", "サブタスク1", "parent")
        subtask2 = Task("sub2", "サブタスク2", "parent")
        
        parent_task.add_subtask(subtask1)
        parent_task.add_subtask(subtask2)
        
        self.assertEqual(len(parent_task.subtasks), 2)
        self.assertEqual(parent_task.subtasks[0].task_id, "sub1")
        self.assertEqual(parent_task.subtasks[1].task_id, "sub2")
    
    def test_task_serialization(self):
        """タスクのシリアライズとデシリアライズのテスト"""
        original_task = Task("serialize", "シリアライズテスト")
        original_task.start()
        original_task.complete({"data": "テスト結果"})
        
        # サブタスクを追加
        subtask = Task("sub", "サブタスク", "serialize")
        subtask.start()
        subtask.complete()
        original_task.add_subtask(subtask)
        
        # 辞書に変換
        task_dict = original_task.to_dict()
        
        # 辞書から再構築
        reconstructed_task = Task.from_dict(task_dict)
        
        # 検証
        self.assertEqual(reconstructed_task.task_id, original_task.task_id)
        self.assertEqual(reconstructed_task.description, original_task.description)
        self.assertEqual(reconstructed_task.status, original_task.status)
        self.assertEqual(reconstructed_task.result, original_task.result)
        self.assertEqual(len(reconstructed_task.subtasks), 1)
        self.assertEqual(reconstructed_task.subtasks[0].task_id, "sub")


class TestTaskPlanner(unittest.TestCase):
    """TaskPlannerクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.planner = TaskPlanner()
    
    def test_create_task(self):
        """タスク作成のテスト"""
        task = self.planner.create_task("テストタスク")
        
        self.assertEqual(task.description, "テストタスク")
        self.assertIsNone(task.parent_id)
        self.assertEqual(task.status, TaskStatus.PENDING)
        
        # 親タスクIDを指定
        subtask = self.planner.create_task("サブタスク", "parent_id")
        self.assertEqual(subtask.parent_id, "parent_id")
    
    def test_decompose_task(self):
        """タスク分解のテスト"""
        main_task = self.planner.create_task("メインタスク")
        subtask_descriptions = ["サブタスク1", "サブタスク2", "サブタスク3"]
        
        subtasks = self.planner.decompose_task(main_task, subtask_descriptions)
        
        self.assertEqual(len(subtasks), 3)
        self.assertEqual(len(main_task.subtasks), 3)
        
        for i, subtask in enumerate(subtasks):
            self.assertEqual(subtask.description, subtask_descriptions[i])
            self.assertEqual(subtask.parent_id, main_task.task_id)
    
    def test_plan_execution(self):
        """実行計画のテスト"""
        tasks = [
            self.planner.create_task("タスク1"),
            self.planner.create_task("タスク2"),
            self.planner.create_task("タスク3")
        ]
        
        plan = self.planner.plan_execution(tasks)
        
        # 現在の実装では順序はそのまま
        self.assertEqual(len(plan), 3)
        self.assertEqual(plan[0].description, "タスク1")
        self.assertEqual(plan[1].description, "タスク2")
        self.assertEqual(plan[2].description, "タスク3")


class TestMemoryManager(unittest.TestCase):
    """MemoryManagerクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        # 一時ディレクトリを使用
        self.temp_dir = tempfile.mkdtemp()
        self.memory_manager = MemoryManager(self.temp_dir)
    
    def tearDown(self):
        """各テスト後の後処理"""
        # 一時ディレクトリを削除
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_working_memory(self):
        """作業記憶のテスト"""
        # 値の設定
        self.memory_manager.set_working_memory("key1", "value1")
        self.memory_manager.set_working_memory("key2", {"nested": "value"})
        
        # 値の取得
        self.assertEqual(self.memory_manager.get_working_memory("key1"), "value1")
        self.assertEqual(self.memory_manager.get_working_memory("key2"), {"nested": "value"})
        
        # 存在しないキー
        self.assertIsNone(self.memory_manager.get_working_memory("non_existent"))
        self.assertEqual(self.memory_manager.get_working_memory("non_existent", "default"), "default")
    
    def test_long_term_memory(self):
        """長期記憶のテスト"""
        # 値の保存
        self.memory_manager.save_long_term_memory("ltm_key1", "ltm_value1")
        self.memory_manager.save_long_term_memory("ltm_key2", {"nested": "ltm_value"})
        
        # 値の読み込み
        self.assertEqual(self.memory_manager.load_long_term_memory("ltm_key1"), "ltm_value1")
        self.assertEqual(self.memory_manager.load_long_term_memory("ltm_key2"), {"nested": "ltm_value"})
        
        # 存在しないキー
        self.assertIsNone(self.memory_manager.load_long_term_memory("non_existent"))
        self.assertEqual(self.memory_manager.load_long_term_memory("non_existent", "default"), "default")
    
    def test_list_long_term_memories(self):
        """長期記憶リストのテスト"""
        # いくつかの長期記憶を保存
        self.memory_manager.save_long_term_memory("ltm_key1", "value1")
        self.memory_manager.save_long_term_memory("ltm_key2", "value2")
        
        # リストの取得
        memories = self.memory_manager.list_long_term_memories()
        
        self.assertEqual(len(memories), 2)
        self.assertIn("ltm_key1", memories)
        self.assertIn("ltm_key2", memories)


class TestExecutionEngine(unittest.TestCase):
    """ExecutionEngineクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.memory_manager = MemoryManager()
        self.execution_engine = ExecutionEngine(self.memory_manager)
    
    def test_task_handler_registration(self):
        """タスクハンドラ登録のテスト"""
        # ハンドラ関数
        def test_handler(task):
            return "handled"
        
        # 登録
        self.execution_engine.register_task_handler("test_type", test_handler)
        
        # 登録の確認
        self.assertIn("test_type", self.execution_engine.task_handlers)
        self.assertEqual(self.execution_engine.task_handlers["test_type"], test_handler)
    
    def test_execute_task(self):
        """タスク実行のテスト"""
        # テスト用のタスク
        task = Task("exec_test", "test_type: テスト実行")
        
        # ハンドラ関数
        def test_handler(task):
            return "executed"
        
        # 登録
        self.execution_engine.register_task_handler("test_type", test_handler)
        
        # 実行
        self.execution_engine.execute_task(task)
        
        # 検証
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result, "executed")
    
    def test_execute_task_with_subtasks(self):
        """サブタスクを持つタスク実行のテスト"""
        # 親タスク
        parent_task = Task("parent", "親タスク")
        
        # サブタスク
        subtask1 = Task("sub1", "サブタスク1", "parent")
        subtask2 = Task("sub2", "サブタスク2", "parent")
        
        parent_task.add_subtask(subtask1)
        parent_task.add_subtask(subtask2)
        
        # 実行
        self.execution_engine.execute_task(parent_task)
        
        # 検証
        self.assertEqual(parent_task.status, TaskStatus.COMPLETED)
        self.assertEqual(subtask1.status, TaskStatus.COMPLETED)
        self.assertEqual(subtask2.status, TaskStatus.COMPLETED)
    
    def test_execute_task_with_error(self):
        """エラー発生時のタスク実行のテスト"""
        # テスト用のタスク
        task = Task("error_test", "error_type: エラーテスト")
        
        # エラーを発生させるハンドラ
        def error_handler(task):
            raise ValueError("テストエラー")
        
        # 登録
        self.execution_engine.register_task_handler("error_type", error_handler)
        
        # 実行
        self.execution_engine.execute_task(task)
        
        # 検証
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertIn("テストエラー", task.error)


class TestAgentManager(unittest.TestCase):
    """AgentManagerクラスのテストケース"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.agent_manager = AgentManager()
    
    def test_process_instruction(self):
        """指示処理のテスト"""
        instruction = "テスト指示"
        
        task = self.agent_manager.process_instruction(instruction)
        
        self.assertEqual(task.description, instruction)
        self.assertEqual(self.agent_manager.current_task, task)
        self.assertEqual(len(task.subtasks), 5)  # デフォルトで5つのサブタスク
    
    def test_execute_current_task(self):
        """現在のタスク実行のテスト"""
        self.agent_manager.process_instruction("実行テスト")
        
        result = self.agent_manager.execute_current_task()
        
        # 現在の実装では結果はNone
        self.assertEqual(self.agent_manager.current_task.status, TaskStatus.COMPLETED)
    
    def test_get_task_status(self):
        """タスク状態取得のテスト"""
        # タスクがない場合
        status = self.agent_manager.get_task_status()
        self.assertEqual(status, {"status": "no_task"})
        
        # タスクがある場合
        self.agent_manager.process_instruction("状態テスト")
        status = self.agent_manager.get_task_status()
        
        self.assertEqual(status["description"], "状態テスト")
        self.assertIn("subtasks", status)
    
    def test_save_and_load_state(self):
        """状態の保存と読み込みのテスト"""
        # 一時ディレクトリを使用
        temp_dir = tempfile.mkdtemp()
        self.agent_manager.memory_manager.memory_dir = temp_dir
        
        try:
            # タスクを作成
            self.agent_manager.process_instruction("状態保存テスト")
            
            # 状態を保存
            self.agent_manager.save_state()
            
            # 新しいエージェントマネージャーを作成
            new_agent = AgentManager()
            new_agent.memory_manager.memory_dir = temp_dir
            
            # 状態を読み込み
            success = new_agent.load_state()
            
            self.assertTrue(success)
            self.assertIsNotNone(new_agent.current_task)
            self.assertEqual(new_agent.current_task.description, "状態保存テスト")
        finally:
            # 一時ディレクトリを削除
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
