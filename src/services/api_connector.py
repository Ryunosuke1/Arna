#!/usr/bin/env python3
"""
Arna - API Connector Service

このモジュールはArnaアプリケーションのAPI連携機能を提供します。
OpenAI Compatible APIを使用したLLMへのリクエスト機能を実装しています。
"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Optional, Any, Union, Tuple
import yaml

# ロガーの設定
logger = logging.getLogger(__name__)


class APIConnectorService:
    """API連携機能を提供するクラス"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        APIConnectorServiceを初期化します。
        
        Args:
            config: API設定の辞書（省略時はデフォルト設定）
        """
        # デフォルト設定
        self.default_config = {
            "api_url": "https://api.openai.com/v1",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 4000,
            "timeout": 60,
            "retry_count": 3,
            "retry_delay": 2
        }
        
        # 設定の初期化
        self.config = self.default_config.copy()
        
        if config:
            self.config.update(config)
        
        # APIキーの取得
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
    
    def set_api_key(self, api_key: str) -> None:
        """
        APIキーを設定します。
        
        Args:
            api_key: APIキー
        """
        self.api_key = api_key
    
    def set_config(self, key: str, value: Any) -> None:
        """
        設定を変更します。
        
        Args:
            key: 変更する設定のキー
            value: 設定値
        """
        self.config[key] = value
    
    def get_config(self, key: str = None) -> Any:
        """
        設定を取得します。
        
        Args:
            key: 取得する設定のキー（省略時は全設定）
            
        Returns:
            設定値
        """
        if key is None:
            return self.config
        
        return self.config.get(key)
    
    def reset_config(self) -> None:
        """設定をデフォルトに戻します。"""
        self.config = self.default_config.copy()
    
    def _prepare_headers(self) -> Dict[str, str]:
        """
        リクエストヘッダーを準備します。
        
        Returns:
            ヘッダーの辞書
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        レスポンスを処理します。
        
        Args:
            response: レスポンスオブジェクト
            
        Returns:
            処理結果の辞書
            
        Raises:
            Exception: API呼び出しエラー
        """
        if response.status_code == 200:
            return response.json()
        else:
            error_message = f"API呼び出しエラー: {response.status_code} - {response.text}"
            logger.error(error_message)
            raise Exception(error_message)
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        チャット補完APIを呼び出します。
        
        Args:
            messages: メッセージのリスト
            **kwargs: その他のパラメータ
            
        Returns:
            API呼び出し結果の辞書
            
        Raises:
            Exception: API呼び出しエラー
        """
        # APIキーの確認
        if not self.api_key:
            error_message = "APIキーが設定されていません"
            logger.error(error_message)
            raise Exception(error_message)
        
        # エンドポイントの構築
        endpoint = f"{self.config['api_url']}/chat/completions"
        
        # リクエストデータの準備
        request_data = {
            "model": kwargs.get("model", self.config["model"]),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config["temperature"]),
            "max_tokens": kwargs.get("max_tokens", self.config["max_tokens"])
        }
        
        # 追加パラメータの設定
        for key, value in kwargs.items():
            if key not in ["model", "messages", "temperature", "max_tokens"]:
                request_data[key] = value
        
        # ヘッダーの準備
        headers = self._prepare_headers()
        
        # リトライ設定
        retry_count = self.config["retry_count"]
        retry_delay = self.config["retry_delay"]
        
        # API呼び出し（リトライあり）
        for i in range(retry_count + 1):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=request_data,
                    timeout=self.config["timeout"]
                )
                
                return self._handle_response(response)
            
            except Exception as e:
                if i < retry_count:
                    logger.warning(f"API呼び出し失敗（リトライ {i+1}/{retry_count}）: {str(e)}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"API呼び出し失敗（リトライ回数超過）: {str(e)}")
                    raise
    
    def extract_text_from_completion(self, completion_result: Dict[str, Any]) -> str:
        """
        補完結果からテキストを抽出します。
        
        Args:
            completion_result: 補完結果の辞書
            
        Returns:
            抽出されたテキスト
        """
        try:
            return completion_result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"補完結果からのテキスト抽出エラー: {str(e)}")
            return ""
    
    def generate_code(self, prompt: str, **kwargs) -> str:
        """
        コードを生成します。
        
        Args:
            prompt: プロンプト
            **kwargs: その他のパラメータ
            
        Returns:
            生成されたコード
        """
        messages = [
            {"role": "system", "content": "You are a skilled software developer. Generate code based on the requirements."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"コード生成エラー: {str(e)}")
            return ""
    
    def analyze_code(self, code: str, **kwargs) -> str:
        """
        コードを分析します。
        
        Args:
            code: 分析対象のコード
            **kwargs: その他のパラメータ
            
        Returns:
            分析結果
        """
        messages = [
            {"role": "system", "content": "You are a code review expert. Analyze the provided code and provide feedback."},
            {"role": "user", "content": f"Please analyze the following code:\n\n```\n{code}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"コード分析エラー: {str(e)}")
            return ""
    
    def generate_test(self, code: str, **kwargs) -> str:
        """
        テストコードを生成します。
        
        Args:
            code: テスト対象のコード
            **kwargs: その他のパラメータ
            
        Returns:
            生成されたテストコード
        """
        messages = [
            {"role": "system", "content": "You are a test automation expert. Generate test code for the provided implementation."},
            {"role": "user", "content": f"Please generate test code for the following implementation:\n\n```\n{code}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"テストコード生成エラー: {str(e)}")
            return ""
    
    def generate_documentation(self, code: str, **kwargs) -> str:
        """
        ドキュメントを生成します。
        
        Args:
            code: ドキュメント対象のコード
            **kwargs: その他のパラメータ
            
        Returns:
            生成されたドキュメント
        """
        messages = [
            {"role": "system", "content": "You are a technical documentation expert. Generate documentation for the provided code."},
            {"role": "user", "content": f"Please generate documentation for the following code:\n\n```\n{code}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"ドキュメント生成エラー: {str(e)}")
            return ""
    
    def refactor_code(self, code: str, instructions: str, **kwargs) -> str:
        """
        コードをリファクタリングします。
        
        Args:
            code: リファクタリング対象のコード
            instructions: リファクタリング指示
            **kwargs: その他のパラメータ
            
        Returns:
            リファクタリングされたコード
        """
        messages = [
            {"role": "system", "content": "You are a code refactoring expert. Refactor the provided code according to the instructions."},
            {"role": "user", "content": f"Please refactor the following code according to these instructions: {instructions}\n\n```\n{code}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"コードリファクタリングエラー: {str(e)}")
            return ""
    
    def explain_code(self, code: str, **kwargs) -> str:
        """
        コードを説明します。
        
        Args:
            code: 説明対象のコード
            **kwargs: その他のパラメータ
            
        Returns:
            コードの説明
        """
        messages = [
            {"role": "system", "content": "You are a programming tutor. Explain the provided code in a clear and educational manner."},
            {"role": "user", "content": f"Please explain the following code:\n\n```\n{code}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"コード説明エラー: {str(e)}")
            return ""
    
    def debug_code(self, code: str, error_message: str, **kwargs) -> str:
        """
        コードをデバッグします。
        
        Args:
            code: デバッグ対象のコード
            error_message: エラーメッセージ
            **kwargs: その他のパラメータ
            
        Returns:
            デバッグ結果
        """
        messages = [
            {"role": "system", "content": "You are a debugging expert. Find and fix issues in the provided code."},
            {"role": "user", "content": f"Please debug the following code that produces this error: {error_message}\n\n```\n{code}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"コードデバッグエラー: {str(e)}")
            return ""
    
    def generate_from_yaml(self, yaml_structure: str, **kwargs) -> str:
        """
        YAML構造からコードを生成します。
        
        Args:
            yaml_structure: YAML構造
            **kwargs: その他のパラメータ
            
        Returns:
            生成されたコード
        """
        messages = [
            {"role": "system", "content": "You are a code generation expert. Generate code based on the provided YAML structure."},
            {"role": "user", "content": f"Please generate code based on the following YAML structure:\n\n```yaml\n{yaml_structure}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"YAML構造からのコード生成エラー: {str(e)}")
            return ""
    
    def generate_yaml_from_code(self, code: str, **kwargs) -> str:
        """
        コードからYAML構造を生成します。
        
        Args:
            code: 対象のコード
            **kwargs: その他のパラメータ
            
        Returns:
            生成されたYAML構造
        """
        messages = [
            {"role": "system", "content": "You are a code analysis expert. Generate a YAML structure that represents the provided code."},
            {"role": "user", "content": f"Please generate a YAML structure that represents the following code:\n\n```\n{code}\n```"}
        ]
        
        try:
            completion_result = self.chat_completion(messages, **kwargs)
            return self.extract_text_from_completion(completion_result)
        except Exception as e:
            logger.error(f"コードからのYAML構造生成エラー: {str(e)}")
            return ""
    
    def check_api_status(self) -> Dict[str, Any]:
        """
        APIの状態を確認します。
        
        Returns:
            API状態の辞書
        """
        # APIキーの確認
        if not self.api_key:
            return {
                "status": "error",
                "message": "APIキーが設定されていません"
            }
        
        try:
            # モデル一覧の取得
            endpoint = f"{self.config['api_url']}/models"
            headers = self._prepare_headers()
            
            response = requests.get(
                endpoint,
                headers=headers,
                timeout=self.config["timeout"]
            )
            
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "API接続成功",
                    "models": response.json().get("data", [])
                }
            else:
                return {
                    "status": "error",
                    "message": f"API接続エラー: {response.status_code} - {response.text}"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"API接続エラー: {str(e)}"
            }
