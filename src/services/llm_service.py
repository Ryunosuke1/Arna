#!/usr/bin/env python3
"""
Arna - LLM Service

このモジュールはLLM（大規模言語モデル）サービスとの連携機能を提供します。
OpenAI Compatible APIとの通信、効果的なプロンプトの生成、
LLMレスポンスの解析などの機能を実装しています。
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
import requests
from requests.exceptions import RequestException

# ロガーの設定
logger = logging.getLogger(__name__)


class LLMConnector:
    """OpenAI Compatible APIとの通信を行うクラス"""
    
    def __init__(self, api_base_url: str, api_key: str, model: str = "gpt-4"):
        """
        LLMConnectorを初期化します。
        
        Args:
            api_base_url: API基本URL
            api_key: APIキー
            model: 使用するモデル名
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def generate_completion(self, prompt: str, max_tokens: int = 1000, 
                           temperature: float = 0.7, top_p: float = 1.0,
                           stop: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        テキスト補完を生成します。
        
        Args:
            prompt: 入力プロンプト
            max_tokens: 生成する最大トークン数
            temperature: 生成の多様性（0.0-1.0）
            top_p: 核サンプリングの確率閾値
            stop: 生成を停止する文字列のリスト
            
        Returns:
            APIレスポンスの辞書
            
        Raises:
            RequestException: API通信エラーの場合
        """
        endpoint = f"{self.api_base_url}/v1/completions"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"API通信エラー: {str(e)}")
            raise
    
    def generate_chat_completion(self, messages: List[Dict[str, str]], 
                                max_tokens: int = 1000, temperature: float = 0.7,
                                top_p: float = 1.0, stop: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        チャット補完を生成します。
        
        Args:
            messages: メッセージのリスト（各メッセージは"role"と"content"を含む辞書）
            max_tokens: 生成する最大トークン数
            temperature: 生成の多様性（0.0-1.0）
            top_p: 核サンプリングの確率閾値
            stop: 生成を停止する文字列のリスト
            
        Returns:
            APIレスポンスの辞書
            
        Raises:
            RequestException: API通信エラーの場合
        """
        endpoint = f"{self.api_base_url}/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"API通信エラー: {str(e)}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        テキストの埋め込みベクトルを取得します。
        
        Args:
            text: 埋め込みを取得するテキスト
            
        Returns:
            埋め込みベクトル
            
        Raises:
            RequestException: API通信エラーの場合
        """
        endpoint = f"{self.api_base_url}/v1/embeddings"
        
        payload = {
            "model": "text-embedding-ada-002",  # 埋め込みモデル
            "input": text
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["data"][0]["embedding"]
        except (RequestException, KeyError) as e:
            logger.error(f"埋め込み取得エラー: {str(e)}")
            raise


class PromptGenerator:
    """効果的なプロンプトの生成を行うクラス"""
    
    def __init__(self):
        """PromptGeneratorを初期化します。"""
        self.templates: Dict[str, str] = {
            "task_planning": """
            タスク「{task_name}」の計画を立ててください。
            
            タスクの説明:
            {task_description}
            
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
            """,
            
            "code_generation": """
            以下の仕様に基づいて、Pythonコードを生成してください。
            
            機能名: {function_name}
            
            機能の説明:
            {function_description}
            
            パラメータ:
            {parameters}
            
            戻り値:
            {returns}
            
            ロジック:
            {logic}
            
            コードは完全に動作するものを生成し、適切なコメントを含めてください。
            エラー処理も適切に実装してください。
            
            出力形式:
            ```python
            # コードをここに生成
            ```
            """,
            
            "code_review": """
            以下のPythonコードをレビューしてください。
            
            ```python
            {code}
            ```
            
            以下の観点からレビューを行い、問題点と改善案を提示してください。
            
            1. 機能性: コードは仕様通りに動作するか
            2. 可読性: コードは理解しやすいか
            3. 保守性: コードは将来的な変更に対応しやすいか
            4. エラー処理: 例外処理は適切か
            5. パフォーマンス: 効率的な実装か
            
            出力形式:
            {
                "issues": [
                    {"severity": "high/medium/low", "description": "問題の説明", "suggestion": "改善案"}
                ],
                "overall_assessment": "全体的な評価"
            }
            """,
            
            "test_generation": """
            以下の関数に対するユニットテストを生成してください。
            
            ```python
            {function_code}
            ```
            
            テストは以下の条件を満たすようにしてください。
            
            1. pytestフレームワークを使用する
            2. 正常系と異常系の両方をテストする
            3. エッジケースも考慮する
            4. モックを適切に使用する（必要な場合）
            
            出力形式:
            ```python
            # テストコードをここに生成
            ```
            """
        }
    
    def add_template(self, name: str, template: str) -> None:
        """
        新しいテンプレートを追加します。
        
        Args:
            name: テンプレート名
            template: テンプレート文字列
        """
        self.templates[name] = template
    
    def generate_prompt(self, template_name: str, **kwargs) -> str:
        """
        指定されたテンプレートを使用してプロンプトを生成します。
        
        Args:
            template_name: 使用するテンプレート名
            **kwargs: テンプレートに埋め込む変数
            
        Returns:
            生成されたプロンプト
            
        Raises:
            ValueError: テンプレートが見つからない場合
        """
        if template_name not in self.templates:
            raise ValueError(f"テンプレート '{template_name}' が見つかりません")
        
        template = self.templates[template_name]
        return template.format(**kwargs)
    
    def generate_custom_prompt(self, base_prompt: str, **kwargs) -> str:
        """
        カスタムプロンプトを生成します。
        
        Args:
            base_prompt: 基本プロンプト
            **kwargs: プロンプトに埋め込む変数
            
        Returns:
            生成されたプロンプト
        """
        return base_prompt.format(**kwargs)


class ResponseParser:
    """LLMレスポンスの解析を行うクラス"""
    
    @staticmethod
    def extract_text(response: Dict[str, Any]) -> str:
        """
        APIレスポンスからテキストを抽出します。
        
        Args:
            response: APIレスポンスの辞書
            
        Returns:
            抽出されたテキスト
            
        Raises:
            ValueError: レスポンス形式が不正な場合
        """
        try:
            # チャット補完の場合
            if "choices" in response and len(response["choices"]) > 0:
                if "message" in response["choices"][0]:
                    return response["choices"][0]["message"]["content"]
                elif "text" in response["choices"][0]:
                    return response["choices"][0]["text"]
            
            raise ValueError("レスポンスから有効なテキストを抽出できません")
        except (KeyError, IndexError) as e:
            logger.error(f"テキスト抽出エラー: {str(e)}")
            raise ValueError(f"レスポンス形式が不正です: {str(e)}")
    
    @staticmethod
    def parse_json(text: str) -> Any:
        """
        テキストからJSONを解析します。
        
        Args:
            text: 解析するテキスト
            
        Returns:
            解析されたJSONオブジェクト
            
        Raises:
            json.JSONDecodeError: JSON解析エラーの場合
        """
        # コードブロックからJSONを抽出
        json_text = text
        if "```json" in text:
            parts = text.split("```json")
            if len(parts) > 1:
                json_text = parts[1].split("```")[0].strip()
        elif "```" in text:
            parts = text.split("```")
            if len(parts) > 1:
                json_text = parts[1].strip()
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {str(e)}")
            raise
    
    @staticmethod
    def extract_code(text: str, language: str = "python") -> str:
        """
        テキストからコードを抽出します。
        
        Args:
            text: 抽出元のテキスト
            language: コードの言語
            
        Returns:
            抽出されたコード
        """
        code_marker = f"```{language}"
        if code_marker in text:
            parts = text.split(code_marker)
            if len(parts) > 1:
                code = parts[1].split("```")[0].strip()
                return code
        
        # コードブロックが見つからない場合は、テキスト全体を返す
        return text


class LLMService:
    """LLMサービスの主要機能を提供するクラス"""
    
    def __init__(self, api_base_url: str, api_key: str, model: str = "gpt-4"):
        """
        LLMServiceを初期化します。
        
        Args:
            api_base_url: API基本URL
            api_key: APIキー
            model: 使用するモデル名
        """
        self.connector = LLMConnector(api_base_url, api_key, model)
        self.prompt_generator = PromptGenerator()
        self.response_parser = ResponseParser()
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 10
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, 
                     temperature: float = 0.7) -> str:
        """
        テキストを生成します。
        
        Args:
            prompt: 入力プロンプト
            max_tokens: 生成する最大トークン数
            temperature: 生成の多様性（0.0-1.0）
            
        Returns:
            生成されたテキスト
        """
        try:
            response = self.connector.generate_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return self.response_parser.extract_text(response)
        except Exception as e:
            logger.error(f"テキスト生成エラー: {str(e)}")
            return f"エラーが発生しました: {str(e)}"
    
    def generate_chat_response(self, user_message: str, system_message: str = None,
                              max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        チャットレスポンスを生成します。
        
        Args:
            user_message: ユーザーメッセージ
            system_message: システムメッセージ（省略可）
            max_tokens: 生成する最大トークン数
            temperature: 生成の多様性（0.0-1.0）
            
        Returns:
            生成されたレスポンス
        """
        messages = []
        
        # システムメッセージがある場合は追加
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # 会話履歴を追加
        messages.extend(self.conversation_history)
        
        # ユーザーメッセージを追加
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.connector.generate_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # レスポンスからテキストを抽出
            response_text = self.response_parser.extract_text(response)
            
            # 会話履歴を更新
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # 履歴が長すぎる場合は古いものを削除
            while len(self.conversation_history) > self.max_history_length * 2:
                self.conversation_history.pop(0)
                self.conversation_history.pop(0)
            
            return response_text
        except Exception as e:
            logger.error(f"チャットレスポンス生成エラー: {str(e)}")
            return f"エラーが発生しました: {str(e)}"
    
    def clear_conversation_history(self) -> None:
        """会話履歴をクリアします。"""
        self.conversation_history.clear()
    
    def generate_code(self, function_name: str, function_description: str,
                     parameters: str, returns: str, logic: str) -> str:
        """
        コードを生成します。
        
        Args:
            function_name: 関数名
            function_description: 関数の説明
            parameters: パラメータの説明
            returns: 戻り値の説明
            logic: ロジックの説明
            
        Returns:
            生成されたコード
        """
        prompt = self.prompt_generator.generate_prompt(
            "code_generation",
            function_name=function_name,
            function_description=function_description,
            parameters=parameters,
            returns=returns,
            logic=logic
        )
        
        response = self.generate_text(prompt, max_tokens=2000, temperature=0.2)
        return self.response_parser.extract_code(response)
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """
        コードをレビューします。
        
        Args:
            code: レビュー対象のコード
            
        Returns:
            レビュー結果の辞書
        """
        prompt = self.prompt_generator.generate_prompt(
            "code_review",
            code=code
        )
        
        response = self.generate_text(prompt, max_tokens=2000, temperature=0.3)
        
        try:
            return self.response_parser.parse_json(response)
        except json.JSONDecodeError:
            # JSON解析に失敗した場合は、テキストをそのまま返す
            return {"text": response}
    
    def generate_tests(self, function_code: str) -> str:
        """
        テストコードを生成します。
        
        Args:
            function_code: テスト対象の関数コード
            
        Returns:
            生成されたテストコード
        """
        prompt = self.prompt_generator.generate_prompt(
            "test_generation",
            function_code=function_code
        )
        
        response = self.generate_text(prompt, max_tokens=2000, temperature=0.2)
        return self.response_parser.extract_code(response)
    
    def parse_json_response(self, text: str) -> Any:
        """
        テキストからJSONを解析します。
        
        Args:
            text: 解析するテキスト
            
        Returns:
            解析されたJSONオブジェクト
        """
        try:
            return self.response_parser.parse_json(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {str(e)}")
            return None
