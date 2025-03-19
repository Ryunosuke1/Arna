#!/usr/bin/env python3
"""
Arna - Data Storage Service

このモジュールはArnaアプリケーションのデータ永続化機能を提供します。
プロジェクト構造、コード構造、設定などのデータを保存・読み込みする機能を実装しています。
"""

import os
import json
import yaml
import logging
import shutil
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile

# ロガーの設定
logger = logging.getLogger(__name__)


class DataStorageService:
    """データ永続化機能を提供するクラス"""
    
    def __init__(self, storage_dir: str = None):
        """
        DataStorageServiceを初期化します。
        
        Args:
            storage_dir: データ保存ディレクトリ（省略時はユーザーホームディレクトリ下の.arna）
        """
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            home_dir = os.path.expanduser("~")
            self.storage_dir = os.path.join(home_dir, ".arna")
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # サブディレクトリの作成
        self.projects_dir = os.path.join(self.storage_dir, "projects")
        self.config_dir = os.path.join(self.storage_dir, "config")
        self.cache_dir = os.path.join(self.storage_dir, "cache")
        
        os.makedirs(self.projects_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 設定ファイルのパス
        self.config_file = os.path.join(self.config_dir, "config.yaml")
        
        # 設定の読み込み
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        設定を読み込みます。
        
        Returns:
            設定の辞書
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"設定読み込みエラー: {str(e)}")
                return {}
        else:
            # デフォルト設定
            default_config = {
                "theme": "swedish_minimalist",
                "editor": {
                    "font_size": 14,
                    "tab_size": 4,
                    "auto_save": True
                },
                "llm": {
                    "api_url": "https://api.openai.com/v1",
                    "model": "gpt-4",
                    "temperature": 0.7
                },
                "recent_projects": []
            }
            
            # デフォルト設定の保存
            self._save_config(default_config)
            
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        設定を保存します。
        
        Args:
            config: 保存する設定の辞書
            
        Returns:
            保存に成功したかどうか
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            logger.error(f"設定保存エラー: {str(e)}")
            return False
    
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
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def set_config(self, key: str, value: Any) -> bool:
        """
        設定を変更します。
        
        Args:
            key: 変更する設定のキー
            value: 設定値
            
        Returns:
            変更に成功したかどうか
        """
        keys = key.split('.')
        config = self.config
        
        # 最後のキー以外を辿る
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            
            if not isinstance(config[k], dict):
                config[k] = {}
            
            config = config[k]
        
        # 最後のキーに値を設定
        config[keys[-1]] = value
        
        # 設定の保存
        return self._save_config(self.config)
    
    def save_project(self, project_data: Dict[str, Any], project_name: str) -> bool:
        """
        プロジェクトデータを保存します。
        
        Args:
            project_data: プロジェクトデータの辞書
            project_name: プロジェクト名
            
        Returns:
            保存に成功したかどうか
        """
        # プロジェクトディレクトリの作成
        project_dir = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # プロジェクトファイルのパス
        project_file = os.path.join(project_dir, "project.yaml")
        
        try:
            # プロジェクトデータの保存
            with open(project_file, 'w', encoding='utf-8') as f:
                yaml.dump(project_data, f, default_flow_style=False)
            
            # 最近使用したプロジェクトリストの更新
            recent_projects = self.config.get("recent_projects", [])
            
            # 既に存在する場合は削除して先頭に追加
            if project_name in recent_projects:
                recent_projects.remove(project_name)
            
            recent_projects.insert(0, project_name)
            
            # 最大10件まで保持
            self.config["recent_projects"] = recent_projects[:10]
            self._save_config(self.config)
            
            return True
        except Exception as e:
            logger.error(f"プロジェクト保存エラー: {str(e)}")
            return False
    
    def load_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        プロジェクトデータを読み込みます。
        
        Args:
            project_name: プロジェクト名
            
        Returns:
            プロジェクトデータの辞書、エラーの場合はNone
        """
        # プロジェクトファイルのパス
        project_file = os.path.join(self.projects_dir, project_name, "project.yaml")
        
        if not os.path.exists(project_file):
            logger.error(f"プロジェクトファイルが存在しません: {project_file}")
            return None
        
        try:
            # プロジェクトデータの読み込み
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = yaml.safe_load(f)
            
            # 最近使用したプロジェクトリストの更新
            recent_projects = self.config.get("recent_projects", [])
            
            # 既に存在する場合は削除して先頭に追加
            if project_name in recent_projects:
                recent_projects.remove(project_name)
            
            recent_projects.insert(0, project_name)
            
            # 最大10件まで保持
            self.config["recent_projects"] = recent_projects[:10]
            self._save_config(self.config)
            
            return project_data
        except Exception as e:
            logger.error(f"プロジェクト読み込みエラー: {str(e)}")
            return None
    
    def list_projects(self) -> List[str]:
        """
        プロジェクト一覧を取得します。
        
        Returns:
            プロジェクト名のリスト
        """
        try:
            # プロジェクトディレクトリ内のサブディレクトリを取得
            return [d for d in os.listdir(self.projects_dir)
                   if os.path.isdir(os.path.join(self.projects_dir, d))]
        except Exception as e:
            logger.error(f"プロジェクト一覧取得エラー: {str(e)}")
            return []
    
    def get_recent_projects(self) -> List[str]:
        """
        最近使用したプロジェクト一覧を取得します。
        
        Returns:
            プロジェクト名のリスト
        """
        return self.config.get("recent_projects", [])
    
    def delete_project(self, project_name: str) -> bool:
        """
        プロジェクトを削除します。
        
        Args:
            project_name: プロジェクト名
            
        Returns:
            削除に成功したかどうか
        """
        # プロジェクトディレクトリのパス
        project_dir = os.path.join(self.projects_dir, project_name)
        
        if not os.path.exists(project_dir):
            logger.error(f"プロジェクトディレクトリが存在しません: {project_dir}")
            return False
        
        try:
            # プロジェクトディレクトリの削除
            shutil.rmtree(project_dir)
            
            # 最近使用したプロジェクトリストから削除
            recent_projects = self.config.get("recent_projects", [])
            
            if project_name in recent_projects:
                recent_projects.remove(project_name)
                self.config["recent_projects"] = recent_projects
                self._save_config(self.config)
            
            return True
        except Exception as e:
            logger.error(f"プロジェクト削除エラー: {str(e)}")
            return False
    
    def export_project(self, project_name: str, export_path: str) -> bool:
        """
        プロジェクトをエクスポートします。
        
        Args:
            project_name: プロジェクト名
            export_path: エクスポート先のパス
            
        Returns:
            エクスポートに成功したかどうか
        """
        # プロジェクトディレクトリのパス
        project_dir = os.path.join(self.projects_dir, project_name)
        
        if not os.path.exists(project_dir):
            logger.error(f"プロジェクトディレクトリが存在しません: {project_dir}")
            return False
        
        try:
            # ディレクトリの場合はコピー
            if os.path.isdir(export_path):
                export_file = os.path.join(export_path, f"{project_name}.yaml")
            else:
                export_file = export_path
            
            # プロジェクトファイルのコピー
            project_file = os.path.join(project_dir, "project.yaml")
            shutil.copy2(project_file, export_file)
            
            return True
        except Exception as e:
            logger.error(f"プロジェクトエクスポートエラー: {str(e)}")
            return False
    
    def import_project(self, import_path: str, project_name: str = None) -> bool:
        """
        プロジェクトをインポートします。
        
        Args:
            import_path: インポート元のパス
            project_name: プロジェクト名（省略時はファイル名から自動生成）
            
        Returns:
            インポートに成功したかどうか
        """
        if not os.path.exists(import_path):
            logger.error(f"インポートファイルが存在しません: {import_path}")
            return False
        
        try:
            # プロジェクト名の決定
            if project_name is None:
                # ファイル名から拡張子を除いた部分をプロジェクト名とする
                project_name = os.path.splitext(os.path.basename(import_path))[0]
            
            # プロジェクトディレクトリの作成
            project_dir = os.path.join(self.projects_dir, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            # プロジェクトファイルのパス
            project_file = os.path.join(project_dir, "project.yaml")
            
            # プロジェクトファイルのコピー
            shutil.copy2(import_path, project_file)
            
            # 最近使用したプロジェクトリストの更新
            recent_projects = self.config.get("recent_projects", [])
            
            # 既に存在する場合は削除して先頭に追加
            if project_name in recent_projects:
                recent_projects.remove(project_name)
            
            recent_projects.insert(0, project_name)
            
            # 最大10件まで保持
            self.config["recent_projects"] = recent_projects[:10]
            self._save_config(self.config)
            
            return True
        except Exception as e:
            logger.error(f"プロジェクトインポートエラー: {str(e)}")
            return False
    
    def save_cache(self, key: str, data: Any) -> bool:
        """
        キャッシュデータを保存します。
        
        Args:
            key: キャッシュキー
            data: 保存するデータ
            
        Returns:
            保存に成功したかどうか
        """
        # キャッシュファイルのパス
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            # データの保存
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {str(e)}")
            return False
    
    def load_cache(self, key: str) -> Optional[Any]:
        """
        キャッシュデータを読み込みます。
        
        Args:
            key: キャッシュキー
            
        Returns:
            キャッシュデータ、エラーの場合はNone
        """
        # キャッシュファイルのパス
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            # データの読み込み
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"キャッシュ読み込みエラー: {str(e)}")
            return None
    
    def clear_cache(self, key: str = None) -> bool:
        """
        キャッシュを削除します。
        
        Args:
            key: 削除するキャッシュキー（省略時は全キャッシュ）
            
        Returns:
            削除に成功したかどうか
        """
        try:
            if key is None:
                # 全キャッシュの削除
                for file in os.listdir(self.cache_dir):
                    if file.endswith(".json"):
                        os.remove(os.path.join(self.cache_dir, file))
            else:
                # 指定キャッシュの削除
                cache_file = os.path.join(self.cache_dir, f"{key}.json")
                
                if os.path.exists(cache_file):
                    os.remove(cache_file)
            
            return True
        except Exception as e:
            logger.error(f"キャッシュ削除エラー: {str(e)}")
            return False
    
    def backup_project(self, project_name: str) -> Optional[str]:
        """
        プロジェクトのバックアップを作成します。
        
        Args:
            project_name: プロジェクト名
            
        Returns:
            バックアップファイルのパス、エラーの場合はNone
        """
        # プロジェクトディレクトリのパス
        project_dir = os.path.join(self.projects_dir, project_name)
        
        if not os.path.exists(project_dir):
            logger.error(f"プロジェクトディレクトリが存在しません: {project_dir}")
            return None
        
        try:
            # バックアップディレクトリの作成
            backup_dir = os.path.join(self.storage_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # タイムスタンプの取得
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # バックアップファイルのパス
            backup_file = os.path.join(backup_dir, f"{project_name}_{timestamp}.zip")
            
            # プロジェクトディレクトリのZIP圧縮
            shutil.make_archive(
                os.path.splitext(backup_file)[0],  # 拡張子を除いたパス
                'zip',
                self.projects_dir,
                project_name
            )
            
            return backup_file
        except Exception as e:
            logger.error(f"プロジェクトバックアップエラー: {str(e)}")
            return None
    
    def restore_backup(self, backup_file: str) -> Optional[str]:
        """
        バックアップからプロジェクトを復元します。
        
        Args:
            backup_file: バックアップファイルのパス
            
        Returns:
            復元されたプロジェクト名、エラーの場合はNone
        """
        if not os.path.exists(backup_file):
            logger.error(f"バックアップファイルが存在しません: {backup_file}")
            return None
        
        try:
            # 一時ディレクトリの作成
            with tempfile.TemporaryDirectory() as temp_dir:
                # バックアップファイルの解凍
                shutil.unpack_archive(backup_file, temp_dir)
                
                # プロジェクト名の取得
                project_dirs = [d for d in os.listdir(temp_dir)
                               if os.path.isdir(os.path.join(temp_dir, d))]
                
                if not project_dirs:
                    logger.error("バックアップファイルにプロジェクトが含まれていません")
                    return None
                
                project_name = project_dirs[0]
                
                # プロジェクトディレクトリの作成
                project_dir = os.path.join(self.projects_dir, project_name)
                
                # 既存のプロジェクトディレクトリがある場合は削除
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
                
                # プロジェクトディレクトリのコピー
                shutil.copytree(
                    os.path.j<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>