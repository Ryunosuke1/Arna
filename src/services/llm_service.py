"""
LLM Service Module

このモジュールはOpenAI Compatible APIを使用したLLMとの連携機能を提供します。
LLMConnector、PromptManager、ResponseParser、ContextManagerなどのコンポーネントを含みます。
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any, Union, Callable
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMConnector:
    """OpenAI Compatible APIとの通信を管理するクラス"""
    
    def __init__(self, api_base_url: str = None, api_key: str = None):
        """
        LLMConnectorの初期化
        
        Args:
            api_base_url: API基本URL (オプション)
            api_key: APIキー (オプション)
        """
        # 環境変数から設定を読み込む
        self.api_base_url = api_base_url or os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        
        if not self.api_key:
            logger.warning("APIキーが設定されていません。環境変数OPENAI_API_KEYを設定するか、初期化時に指定してください。")
        
        self.default_model = os.environ.get("OPENAI_MODEL", "gpt-4")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })
    
    def set_api_key(self, api_key: str) -> None:
        """
        APIキーを設定
        
        Args:
            api_key: APIキー
        """
        self.api_key = api_key
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })
    
    def set_api_base_url(self, api_base_url: str) -> None:
        """
        API基本URLを設定
        
        Args:
            api_base_url: API基本URL
        """
        self.api_base_url = api_base_url
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = None, 
                        temperature: float = 0.7, 
                        max_tokens: int = None,
                        stream: bool = False,
                        **kwargs) -> Dict[str, Any]:
        """
        チャット補完APIを呼び出す
        
        Args:
            messages: メッセージリスト
            model: モデル名 (オプション)
            temperature: 温度パラメータ (オプション)
            max_tokens: 最大トークン数 (オプション)
            stream: ストリーミングモード (オプション)
            **kwargs: その他のパラメータ
            
        Returns:
            APIレスポンス
        """
        url = f"{self.api_base_url}/chat/completions"
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # その他のパラメータを追加
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API呼び出し中にエラーが発生しました: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"レスポンス: {e.response.text}")
            raise
    
    def streaming_chat_completion(self, 
                                 messages: List[Dict[str, str]], 
                                 model: str = None, 
                                 temperature: float = 0.7, 
                                 max_tokens: int = None,
                                 callback: Callable[[str], None] = None,
                                 **kwargs) -> str:
        """
        ストリーミングモードでチャット補完APIを呼び出す
        
        Args:
            messages: メッセージリスト
            model: モデル名 (オプション)
            temperature: 温度パラメータ (オプション)
            max_tokens: 最大トークン数 (オプション)
            callback: 各チャンクを受け取るコールバック関数 (オプション)
            **kwargs: その他のパラメータ
            
        Returns:
            生成されたテキスト全体
        """
        url = f"{self.api_base_url}/chat/completions"
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # その他のパラメータを追加
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            response = self.session.post(url, json=payload, stream=True)
            response.raise_for_status()
            
            full_text = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: ') and line != 'data: [DONE]':
                        data = json.loads(line[6:])
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                full_text += content
                                if callback:
                                    callback(content)
            
            return full_text
        except requests.exceptions.RequestException as e:
            logger.error(f"ストリーミングAPI呼び出し中にエラーが発生しました: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"レスポンス: {e.response.text}")
            raise


class PromptManager:
    """プロンプト生成と最適化を行うクラス"""
    
    def __init__(self, templates_dir: str = None):
        """
        PromptManagerの初期化
        
        Args:
            templates_dir: テンプレートディレクトリ (オプション)
        """
        self.templates_dir = templates_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates/prompts")
        self.templates: Dict[str, str] = {}
        self.load_templates()
    
    def load_templates(self) -> None:
        """テンプレートを読み込む"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            self._create_default_templates()
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".txt"):
                template_name = os.path.splitext(filename)[0]
                with open(os.path.join(self.templates_dir, filename), 'r') as f:
                    self.templates[template_name] = f.read()
    
    def _create_default_templates(self) -> None:
        """デフォルトのテンプレートを作成"""
        default_templates = {
            "code_generation": "以下の要件に基づいてPythonコードを生成してください:\n\n{requirements}\n\n以下の制約を守ってください:\n{constraints}",
            "code_review": "以下のコードをレビューし、改善点を指摘してください:\n\n```python\n{code}\n```",
            "task_decomposition": "以下のタスクを小さなサブタスクに分解してください:\n\n{task}",
            "error_analysis": "以下のエラーを分析し、解決策を提案してください:\n\n{error}"
        }
        
        for name, content in default_templates.items():
            with open(os.path.join(self.templates_dir, f"{name}.txt"), 'w') as f:
                f.write(content)
    
    def get_template(self, template_name: str) -> Optional[str]:
        """
        テンプレートを取得
        
        Args:
            template_name: テンプレート名
            
        Returns:
            テンプレート文字列、存在しない場合はNone
        """
        return self.templates.get(template_name)
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """
        テンプレートを使用してプロンプトをフォーマット
        
        Args:
            template_name: テンプレート名
            **kwargs: テンプレート変数
            
        Returns:
            フォーマットされたプロンプト
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"テンプレート '{template_name}' が見つかりません")
        
        return template.format(**kwargs)
    
    def create_chat_messages(self, system_prompt: str, user_prompt: str, 
                            assistant_messages: List[str] = None,
                            user_messages: List[str] = None) -> List[Dict[str, str]]:
        """
        チャットメッセージを作成
        
        Args:
            system_prompt: システムプロンプト
            user_prompt: ユーザープロンプト
            assistant_messages: アシスタントメッセージリスト (オプション)
            user_messages: ユーザーメッセージリスト (オプション)
            
        Returns:
            チャットメッセージリスト
        """
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 過去のメッセージがある場合は追加
        if user_messages and assistant_messages:
            for user_msg, assistant_msg in zip(user_messages, assistant_messages):
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": assistant_msg})
        
        # 最新のユーザーメッセージを追加
        messages.append({"role": "user", "content": user_prompt})
        
        return messages


class ResponseParser:
    """LLMの応答を解析するクラス"""
    
    def extract_code(self, text: str) -> List[Dict[str, str]]:
        """
        テキストからコードブロックを抽出
        
        Args:
            text: 抽出元テキスト
            
        Returns:
            言語とコードのペアのリスト
        """
        import re
        
        # コードブロックを抽出するための正規表現
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.finditer(pattern, text, re.DOTALL)
        
        code_blocks = []
        for match in matches:
            language = match.group(1) or "text"
            code = match.group(2)
            code_blocks.append({
                "language": language,
                "code": code
            })
        
        return code_blocks
    
    def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        テキストからJSONを抽出
        
        Args:
            text: 抽出元テキスト
            
        Returns:
            抽出されたJSON、抽出できない場合はNone
        """
        import re
        import json
        
        # JSONブロックを抽出するための正規表現
        pattern = r"```json\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.error("JSONの解析に失敗しました")
                return None
        
        # JSONブロックが見つからない場合は、テキスト全体をJSONとして解析を試みる
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.error("テキスト全体のJSON解析に失敗しました")
            return None
    
    def extract_list(self, text: str) -> List[str]:
        """
        テキストからリストを抽出
        
        Args:
            text: 抽出元テキスト
            
        Returns:
            抽出されたリスト
        """
        import re
        
        # 箇条書きを抽出するための正規表現
        pattern = r"(?:^|\n)[-*]\s+(.*?)(?=\n[-*]|\n\n|$)"
        matches = re.finditer(pattern, text, re.DOTALL)
        
        items = []
        for match in matches:
            items.append(match.group(1).strip())
        
        return items


class ContextManager:
    """コンテキスト情報を管理するクラス"""
    
    def __init__(self, max_context_length: int = 10):
        """
        ContextManagerの初期化
        
        Args:
            max_context_length: 最大コンテキスト長
        """
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_length = max_context_length
    
    def add_message(self, role: str, content: str) -> None:
        """
        メッセージを追加
        
        Args:
            role: ロール ("system", "user", "assistant")
            content: メッセージ内容
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        
        # 最大長を超えた場合は古いメッセージを削除
        if len(self.conversation_history) > self.max_context_length:
            # システムメッセージは保持
            system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
            other_messages = [msg for msg in self.conversation_history if msg["role"] != "system"]
            
            # 古いメッセージから削除
            other_messages = other_messages[-(self.max_context_length - len(system_messages)):]
            
            self.conversation_history = system_messages + other_messages
    
    def get_conversation_messages(self) -> List[Dict[str, str]]:
        """
        会話メッセージを取得
        
        Returns:
            会話メッセージリスト
        """
        return [{"role": msg["role"], "content": msg["content"]} 
                for msg in self.conversation_history]
    
    def clear_conversation(self, keep_system: bool = True) -> None:
        """
        会話履歴をクリア
        
        Args:
            keep_system: システムメッセージを保持するかどうか
        """
        if keep_system:
            self.conversation_history = [msg for msg in self.conversation_history if msg["role"] == "system"]
        else:
            self.conversation_history = []
    
    def save_conversation(self, file_path: str) -> None:
        """
        会話履歴を保存
        
        Args:
            file_path: 保存先ファイルパス
        """
        with open(file_path, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
    
    def load_conversation(self, file_path: str) -> None:
        """
        会話履歴を読み込み
        
        Args:
            file_path: 読み込むファイルパス
        """
        with open(file_path, 'r') as f:
            self.conversation_history = json.load(f)


class LLMService:
    """LLMサービスの統合クラス"""
    
    def __init__(self, api_base_url: str = None, api_key: str = None):
        """
        LLMServiceの初期化
        
        Args:
            api_base_url: API基本URL (オプション)
            api_key: APIキー (オプション)
        """
        self.connector = LLMConnector(api_base_url, api_key)
        self.prompt_manager = PromptManager()
        self.response_parser = ResponseParser()
        self.context_manager = ContextManager()
    
    def generate_code(self, requirements: str, constraints: str = "") -> List[Dict[str, str]]:
        """
        コードを生成
        
        Args:
            requirements: 要件
            constraints: 制約 (オプション)
            
        Returns:
            生成されたコードブロックのリスト
        """
        prompt = self.prompt_manager.format_prompt(
            "code_generation",
            requirements=requirements,
            constraints=constraints
        )
        
        messages = self.prompt_manager.create_chat_messages(
            system_prompt="あなたは優秀なプログラマーです。要件に基づいて高品質なコードを生成してください。",
            user_prompt=prompt
        )
        
        response = self.connector.chat_completion(messages)
        content = response["choices"][0]["message"]["content"]
        
        self.context_manager.add_message("user", prompt)
        self.context_manager.add_message("assistant", content)
        
        return self.response_parser.extract_code(content)
    
    def review_code(self, code: str) -> str:
        """
        コードをレビュー
        
        Args:
            code: レビュー対象のコード
            
        Returns:
            レビュー結果
        """
        prompt = self.prompt_manager.format_prompt(
            "code_review",
            code=code
        )
        
        messages = self.prompt_manager.create_chat_messages(
            system_prompt="あなたは経験豊富なコードレビュアーです。コードの問題点や改善点を指摘してください。",
            user_prompt=prompt
        )
        
        response = self.connector.chat_completion(messages)
        content = response["choices"][0]["message"]["content"]
        
        self.context_manager.add_message("user", prompt)
        self.context_manager.add_message("assistant", content)
        
        return content
    
    def decompose_task(self, task: str) -> List[str]:
        """
        タスクを分解
        
        Args:
            task: 分解対象のタスク
            
        Returns:
            分解されたサブタスクのリスト
        """
        prompt = self.prompt_manager.format_prompt(
            "task_decomposition",
            task=task
        )
        
        messages = self.prompt_manager.create_chat_messages(
            system_prompt="あなたは優れたタスク管理の専門家です。複雑なタスクを小さな実行可能なサブタスクに分解してください。",
            user_prompt=prompt
        )
        
        response = self.connector.chat_completion(messages)
        content = response["choices"][0]["message"]["content"]
        
        self.context_manager.add_message("user", prompt)
        self.context_manager.add_message("assistant", content)
        
        return self.response_parser.extract_list(content)
    
    def analyze_error(self, error: str) -> str:
        """
        エラーを分析
        
        Args:
            error: 分析対象のエラー
            
        Returns:
            分析結果
        """
        prompt = self.prompt_manager.format_prompt(
            "error_analysis",
            error=error
        )
        
        messages = self.prompt_manager.create_chat_messages(
            system_prompt="あなたはデバッグの専門家です。エラーメッセージを分析し、問題の原因と解決策を提案してください。",
            user_prompt=prompt
        )
        
        response = self.connector.chat_completion(messages)
        content = response["choices"][0]["message"]["content"]
        
        self.context_manager.add_message("user", prompt)
        self.context_manager.add_message("assistant", content)
        
        return content
    
    def chat(self, message: str, system_prompt: str = None) -> str:
        """
        チャット
        
        Args:
            message: ユーザーメッセージ
            system_prompt: システムプロンプト (オプション)
            
        Returns:
            アシスタントの応答
        """
        if system_prompt:
            # 新しいシステムプロンプトが提供された場合は会話をリセット
            self.context_manager.clear_conversation()
            self.context_manager.add_message("system", system_prompt)
        
        self.context_manager.add_message("user", message)
        
        messages = self.context_manager.get_conversation_messages()
        
        response = self.connector.chat_completion(messages)
        content = response["choices"][0]["message"]["content"]
        
        self.context_manager.add_message("assistant", content)
        
        return content
    
    def streaming_chat(self, message: str, callback: Callable[[str], None], system_prompt: str = None) -> str:
        """
        ストリーミングチャット
        
        Args:
            message: ユーザーメッセージ
            callback: 各チャンクを受け取るコールバック関数
            system_prompt: システムプロンプト (オプション)
            
        Returns:
            アシスタントの応答全体
        """
        if system_prompt:
            # 新しいシステムプロンプトが提供された場合は会話をリセット
            self.context_manager.clear_conversation()
            self.context_manager.add_message("system", system_prompt)
        
        self.context_manager.add_message("user", message)
        
        messages = self.context_manager.get_conversation_messages()
        
        content = self.connector.streaming_chat_completion(messages, callback=callback)
        
        self.context_manager.add_message("assistant", content)
        
        return content
