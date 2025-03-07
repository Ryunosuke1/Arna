from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

@dataclass
class Question:
    """エージェントからの質問を表すデータクラス"""
    agent_name: str
    category: str
    content: str
    answered: bool = False
    answer: str = ""
    number: int = 0  # 質問番号（表示用）

class QuestionManager:
    """質問のキュー管理を行うクラス"""
    def __init__(self):
        self._question_queue: List[Question] = []
        self._current_question: Optional[Question] = None
        self._question_count: int = 0
        self.logger = logging.getLogger(__name__)
    
    def add_question(self, agent_name: str, category: str, content: str) -> None:
        """
        エージェントから新しい質問を追加
        
        Args:
            agent_name: 質問するエージェントの名前
            category: 質問のカテゴリ
            content: 質問内容
        """
        self._question_count += 1
        question = Question(
            agent_name=agent_name,
            category=category,
            content=content,
            number=self._question_count
        )
        self._question_queue.append(question)
        self.logger.info(f"Added question {self._question_count} from {agent_name}")
    
    def get_next_question(self) -> Optional[Question]:
        """次の未回答の質問を取得"""
        if self._current_question is None:
            unanswered = [q for q in self._question_queue if not q.answered]
            if unanswered:
                self._current_question = unanswered[0]
                self.logger.info(f"Next question: {self._current_question.number}")
                return self._current_question
        return self._current_question
    
    def answer_current_question(self, answer: str) -> None:
        """
        現在の質問に回答を記録
        
        Args:
            answer: ユーザーからの回答
        """
        if self._current_question:
            self._current_question.answered = True
            self._current_question.answer = answer
            self.logger.info(f"Answered question {self._current_question.number}")
            self._current_question = None
    
    def get_all_answers(self) -> List[Dict]:
        """
        回答済みの全質問と回答を取得
        
        Returns:
            List[Dict]: 質問と回答のリスト
        """
        return [
            {
                "number": q.number,
                "agent": q.agent_name,
                "category": q.category,
                "question": q.content,
                "answer": q.answer
            }
            for q in self._question_queue
            if q.answered
        ]
    
    def has_unanswered_questions(self) -> bool:
        """未回答の質問が残っているかどうかを確認"""
        return any(not q.answered for q in self._question_queue)

class QuestionTool:
    """エージェントが使用する質問ツール"""
    
    categories = [
        "LIBRARY",      # ライブラリ選択・使用方法
        "ALGORITHM",    # アルゴリズム・実装方法
        "UI",          # UIデザイン・実装
        "ARCHITECTURE", # 設計・構造
        "OTHERS"       # その他
    ]
    
    def __init__(self):
        self.question_manager = QuestionManager()
    
    def ask_question(self, agent_name: str, category: str, content: str) -> None:
        """
        質問を追加するツール
        
        Args:
            agent_name: エージェント名
            category: 質問カテゴリ（QuestionTool.categoriesから選択）
            content: 質問内容
        """
        if category not in self.categories:
            category = "OTHERS"
        self.question_manager.add_question(agent_name, category, content)
    
    def get_answers(self) -> List[Dict]:
        """
        全ての回答済み質問と回答を取得
        
        Returns:
            List[Dict]: 質問と回答のリスト
        """
        return self.question_manager.get_all_answers()
