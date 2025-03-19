#!/usr/bin/env python3
"""
Arna - Tool Integration

このモジュールはArnaエージェントの外部ツール連携機能を提供します。
Webブラウザの操作、テキストエディタの操作、ファイルシステムの操作などの
機能を実装しています。
"""

import os
import re
import time
import logging
import subprocess
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import tempfile
import shutil

# ブラウザ自動化のためのSeleniumをインポート
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, WebDriverException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# ロガーの設定
logger = logging.getLogger(__name__)


class BrowserController:
    """Webブラウザの操作を行うクラス"""
    
    def __init__(self, headless: bool = False, browser_type: str = "chrome"):
        """
        BrowserControllerを初期化します。
        
        Args:
            headless: ヘッドレスモードで実行するかどうか
            browser_type: ブラウザの種類（"chrome"または"firefox"）
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Seleniumがインストールされていません。pip install seleniumを実行してください。")
        
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.driver = None
        self.wait_timeout = 10  # 要素待機のデフォルトタイムアウト（秒）
    
    def start_browser(self) -> bool:
        """
        ブラウザを起動します。
        
        Returns:
            起動に成功したかどうか
        """
        try:
            if self.driver:
                # すでに起動している場合は何もしない
                return True
            
            if self.browser_type == "chrome":
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.driver = webdriver.Chrome(options=options)
            elif self.browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Firefox(options=options)
            else:
                raise ValueError(f"サポートされていないブラウザタイプ: {self.browser_type}")
            
            self.driver.maximize_window()
            return True
        
        except Exception as e:
            logger.error(f"ブラウザ起動エラー: {str(e)}")
            return False
    
    def close_browser(self) -> None:
        """ブラウザを閉じます。"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"ブラウザ終了エラー: {str(e)}")
            finally:
                self.driver = None
    
    def navigate_to(self, url: str) -> bool:
        """
        指定されたURLに移動します。
        
        Args:
            url: 移動先のURL
            
        Returns:
            移動に成功したかどうか
        """
        if not self.driver:
            if not self.start_browser():
                return False
        
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"ナビゲーションエラー: {str(e)}")
            return False
    
    def get_page_content(self) -> str:
        """
        現在のページのHTMLコンテンツを取得します。
        
        Returns:
            ページのHTMLコンテンツ
        """
        if not self.driver:
            return ""
        
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"ページコンテンツ取得エラー: {str(e)}")
            return ""
    
    def get_page_text(self) -> str:
        """
        現在のページのテキストコンテンツを取得します。
        
        Returns:
            ページのテキストコンテンツ
        """
        if not self.driver:
            return ""
        
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception as e:
            logger.error(f"ページテキスト取得エラー: {str(e)}")
            return ""
    
    def find_element(self, selector: str, by: str = By.CSS_SELECTOR, 
                    wait: bool = True) -> Optional[Any]:
        """
        要素を検索します。
        
        Args:
            selector: 要素のセレクタ
            by: 検索方法（デフォルトはCSS_SELECTOR）
            wait: 要素が見つかるまで待機するかどうか
            
        Returns:
            見つかった要素、見つからない場合はNone
        """
        if not self.driver:
            return None
        
        try:
            if wait:
                element = WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                return element
            else:
                return self.driver.find_element(by, selector)
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"要素が見つかりません: {selector} ({str(e)})")
            return None
        except Exception as e:
            logger.error(f"要素検索エラー: {str(e)}")
            return None
    
    def find_elements(self, selector: str, by: str = By.CSS_SELECTOR) -> List[Any]:
        """
        複数の要素を検索します。
        
        Args:
            selector: 要素のセレクタ
            by: 検索方法（デフォルトはCSS_SELECTOR）
            
        Returns:
            見つかった要素のリスト
        """
        if not self.driver:
            return []
        
        try:
            return self.driver.find_elements(by, selector)
        except Exception as e:
            logger.error(f"要素検索エラー: {str(e)}")
            return []
    
    def click_element(self, selector: str, by: str = By.CSS_SELECTOR, 
                     wait: bool = True) -> bool:
        """
        要素をクリックします。
        
        Args:
            selector: 要素のセレクタ
            by: 検索方法（デフォルトはCSS_SELECTOR）
            wait: 要素が見つかるまで待機するかどうか
            
        Returns:
            クリックに成功したかどうか
        """
        element = self.find_element(selector, by, wait)
        if not element:
            return False
        
        try:
            element.click()
            return True
        except Exception as e:
            logger.error(f"クリックエラー: {str(e)}")
            
            # JavaScriptを使用して強制的にクリック
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_e:
                logger.error(f"JavaScriptクリックエラー: {str(js_e)}")
                return False
    
    def input_text(self, selector: str, text: str, by: str = By.CSS_SELECTOR, 
                  clear_first: bool = True, submit: bool = False) -> bool:
        """
        テキストを入力します。
        
        Args:
            selector: 要素のセレクタ
            text: 入力するテキスト
            by: 検索方法（デフォルトはCSS_SELECTOR）
            clear_first: 入力前にフィールドをクリアするかどうか
            submit: 入力後にEnterキーを押すかどうか
            
        Returns:
            入力に成功したかどうか
        """
        element = self.find_element(selector, by)
        if not element:
            return False
        
        try:
            if clear_first:
                element.clear()
            
            element.send_keys(text)
            
            if submit:
                element.send_keys(Keys.RETURN)
            
            return True
        except Exception as e:
            logger.error(f"テキスト入力エラー: {str(e)}")
            return False
    
    def execute_script(self, script: str, *args) -> Any:
        """
        JavaScriptを実行します。
        
        Args:
            script: 実行するJavaScriptコード
            *args: スクリプトに渡す引数
            
        Returns:
            スクリプトの実行結果
        """
        if not self.driver:
            return None
        
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            logger.error(f"スクリプト実行エラー: {str(e)}")
            return None
    
    def take_screenshot(self, file_path: str) -> bool:
        """
        スクリーンショットを撮影します。
        
        Args:
            file_path: 保存先のファイルパス
            
        Returns:
            撮影に成功したかどうか
        """
        if not self.driver:
            return False
        
        try:
            self.driver.save_screenshot(file_path)
            return True
        except Exception as e:
            logger.error(f"スクリーンショット撮影エラー: {str(e)}")
            return False
    
    def scroll_to(self, x: int = 0, y: int = 0) -> bool:
        """
        指定された位置にスクロールします。
        
        Args:
            x: X座標
            y: Y座標
            
        Returns:
            スクロールに成功したかどうか
        """
        if not self.driver:
            return False
        
        try:
            self.driver.execute_script(f"window.scrollTo({x}, {y});")
            return True
        except Exception as e:
            logger.error(f"スクロールエラー: {str(e)}")
            return False
    
    def scroll_to_element(self, selector: str, by: str = By.CSS_SELECTOR) -> bool:
        """
        指定された要素までスクロールします。
        
        Args:
            selector: 要素のセレクタ
            by: 検索方法（デフォルトはCSS_SELECTOR）
            
        Returns:
            スクロールに成功したかどうか
        """
        element = self.find_element(selector, by)
        if not element:
            return False
        
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            return True
        except Exception as e:
            logger.error(f"要素へのスクロールエラー: {str(e)}")
            return False
    
    def wait_for_element(self, selector: str, by: str = By.CSS_SELECTOR, 
                        timeout: int = None) -> bool:
        """
        要素が表示されるまで待機します。
        
        Args:
            selector: 要素のセレクタ
            by: 検索方法（デフォルトはCSS_SELECTOR）
            timeout: タイムアウト（秒）、Noneの場合はデフォルト値を使用
            
        Returns:
            要素が見つかったかどうか
        """
        if not self.driver:
            return False
        
        if timeout is None:
            timeout = self.wait_timeout
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except TimeoutException:
            logger.warning(f"要素待機タイムアウト: {selector}")
            return False
        except Exception as e:
            logger.error(f"要素待機エラー: {str(e)}")
            return False


class EditorController:
    """テキストエディタの操作を行うクラス"""
    
    def __init__(self, editor_command: str = None):
        """
        EditorControllerを初期化します。
        
        Args:
            editor_command: エディタコマンド（省略時はシステムのデフォルトエディタ）
        """
        self.editor_command = editor_command or os.environ.get("EDITOR", "nano")
    
    def open_file(self, file_path: str) -> bool:
        """
        ファイルをエディタで開きます。
        
        Args:
            file_path: 開くファイルのパス
            
        Returns:
            オープンに成功したかどうか
        """
        try:
            # ファイルが存在しない場合は作成
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    pass
            
            # エディタでファイルを開く
            subprocess.run([self.editor_command, file_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"エディタ起動エラー: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"ファイルオープンエラー: {str(e)}")
            return False
    
    def create_temp_file(self, content: str = "", suffix: str = ".txt") -> Optional[str]:
        """
        一時ファイルを作成します。
        
        Args:
            content: ファイルの初期内容
            suffix: ファイル拡張子
            
        Returns:
            作成された一時ファイルのパス、失敗した場合はNone
        """
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix)
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return temp_path
        except Exception as e:
            logger.error(f"一時ファイル作成エラー: {str(e)}")
            return None
    
    def edit_content(self, content: str, suffix: str = ".txt") -> Optional[str]:
        """
        テキストコンテンツをエディタで編集します。
        
        Args:
            content: 編集する初期コンテンツ
            suffix: 一時ファイルの拡張子
            
        Returns:
            編集後のコンテンツ、キャンセルまたはエラーの場合はNone
        """
        temp_path = self.create_temp_file(content, suffix)
        if not temp_path:
            return None
        
        try:
            # エディタでファイルを開く
            if not self.open_file(temp_path):
                return None
            
            # 編集後のコンテンツを読み込む
            with open(temp_path, 'r') as f:
                edited_content = f.read()
            
            # 一時ファイルを削除
            os.unlink(temp_path)
            
            return edited_content
        except Exception as e:
            logger.error(f"コンテンツ編集エラー: {str(e)}")
            
            # エラー時も一時ファイルを削除
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return None


class FileSystemController:
    """ファイルシステムの操作を行うクラス"""
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        ファイルの内容を読み込みます。
        
        Args:
            file_path: 読み込むファイルのパス
            
        Returns:
            ファイルの内容、エラーの場合はNone
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # バイナリファイルの場合はバイナリモードで読み込み
            try:
                with open(file_path, 'rb') as f:
                    return f"<バイナリファイル: {len(f.read())} バイト>"
            except Exception as e:
                logger.error(f"バイナリファイル読み込みエラー: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {str(e)}")
            return None
    
    def write_file(self, file_path: str, content: str, append: bool = False) -> bool:
        """
        ファイルに内容を書き込みます。
        
        Args:
            file_path: 書き込むファイルのパス
            content: 書き込む内容
            append: 追記モードで書き込むかどうか
            
        Returns:
            書き込みに成功したかどうか
        """
        mode = 'a' if append else 'w'
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"ファイル書き込みエラー: {str(e)}")
            return False
    
    def copy_file(self, source_path: str, dest_path: str) -> bool:
        """
        ファイルをコピーします。
        
        Args:
            source_path: コピー元のファイルパス
            dest_path: コピー先のファイルパス
            
        Returns:
            コピーに成功したかどうか
        """
        try:
            # コピー先のディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            
            shutil.copy2(source_path, dest_path)
            return True
        except Exception as e:
            logger.error(f"ファイルコピーエラー: {str(e)}")
            return False
    
    def move_file(self, source_path: str, dest_path: str) -> bool:
        """
        ファイルを移動します。
        
        Args:
            source_path: 移動元のファイルパス
            dest_path: 移動先のファイルパス
            
        Returns:
            移動に成功したかどうか
        """
        try:
            # 移動先のディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            
            shutil.move(source_path, dest_path)
            return True
        except Exception as e:
            logger.error(f"ファイル移動エラー: {str(e)}")
            return<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>