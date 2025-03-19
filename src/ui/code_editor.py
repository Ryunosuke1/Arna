#!/usr/bin/env python3
"""
Arna - Code Editor

このモジュールはコードエディタUIコンポーネントを提供します。
スウェーデン風ミニマリズムに基づいたデザインを適用し、
コードの編集、シンタックスハイライト、自動補完などの機能を実装します。
"""

from kivy.uix.codeinput import CodeInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.lang import Builder
from pygments.lexers import PythonLexer

# 自作モジュールのインポート
from src.ui.theme import SwedishMinimalistTheme

# KVファイルの読み込み
Builder.load_string('''
#:kivy 2.0.0

<CodeEditor>:
    background_color: app.theme.colors.OFF_WHITE
    foreground_color: app.theme.colors.DARK_GREY
    font_name: app.theme.FONT_FAMILY_MONO
    font_size: app.theme.FONT_SIZE_BODY
    padding: [app.theme.PADDING_MEDIUM, app.theme.PADDING_MEDIUM]
    
    canvas.before:
        Color:
            rgba: app.theme.colors.OFF_WHITE
        Rectangle:
            pos: self.pos
            size: self.size

<CodeEditorToolbar>:
    orientation: 'horizontal'
    size_hint_y: None
    height: app.theme.TOOLBAR_HEIGHT
    padding: [app.theme.PADDING_MEDIUM, app.theme.PADDING_SMALL]
    spacing: app.theme.PADDING_MEDIUM
    canvas.before:
        Color:
            rgba: app.theme.colors.LIGHT_GREY
        Rectangle:
            pos: self.pos
            size: self.size
    
    Button:
        text: 'Save'
        size_hint_x: None
        width: dp(80)
        background_color: app.theme.colors.SWEDISH_BLUE
        color: app.theme.colors.OFF_WHITE
        font_name: app.theme.FONT_FAMILY_REGULAR
        font_size: app.theme.FONT_SIZE_BODY
        on_release: root.save_code()
    
    Button:
        text: 'Format'
        size_hint_x: None
        width: dp(80)
        background_color: app.theme.colors.SWEDISH_BLUE
        color: app.theme.colors.OFF_WHITE
        font_name: app.theme.FONT_FAMILY_REGULAR
        font_size: app.theme.FONT_SIZE_BODY
        on_release: root.format_code()
    
    Button:
        text: 'Run'
        size_hint_x: None
        width: dp(80)
        background_color: app.theme.colors.SWEDISH_BLUE
        color: app.theme.colors.OFF_WHITE
        font_name: app.theme.FONT_FAMILY_REGULAR
        font_size: app.theme.FONT_SIZE_BODY
        on_release: root.run_code()
    
    Label:
        text: root.status_text
        color: app.theme.colors.DARK_GREY
        font_name: app.theme.FONT_FAMILY_REGULAR
        font_size: app.theme.FONT_SIZE_SMALL
        text_size: self.size
        halign: 'right'
        valign: 'middle'

<CodeEditorContainer>:
    orientation: 'vertical'
    
    CodeEditorToolbar:
        id: toolbar
        editor: editor
    
    CodeEditor:
        id: editor
''')


class CodeEditor(CodeInput):
    """コードエディタコンポーネント"""
    
    file_path = StringProperty('')
    is_modified = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        # デフォルトでPythonレキサーを使用
        kwargs['lexer'] = PythonLexer()
        super(CodeEditor, self).__init__(**kwargs)
        
        # テキスト変更時のコールバックを設定
        self.bind(text=self.on_text_changed)
    
    def on_text_changed(self, instance, value):
        """テキストが変更されたときのコールバック"""
        self.is_modified = True
    
    def load_file(self, file_path):
        """
        ファイルを読み込みます。
        
        Args:
            file_path: 読み込むファイルのパス
            
        Returns:
            読み込みに成功したかどうか
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.text = f.read()
            
            self.file_path = file_path
            self.is_modified = False
            return True
        except Exception as e:
            print(f"ファイル読み込みエラー: {str(e)}")
            return False
    
    def save_file(self, file_path=None):
        """
        ファイルを保存します。
        
        Args:
            file_path: 保存先のファイルパス（省略時は現在のファイルパス）
            
        Returns:
            保存に成功したかどうか
        """
        file_path = file_path or self.file_path
        
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text)
            
            self.file_path = file_path
            self.is_modified = False
            return True
        except Exception as e:
            print(f"ファイル保存エラー: {str(e)}")
            return False
    
    def format_code(self):
        """
        コードを整形します。
        
        Returns:
            整形に成功したかどうか
        """
        try:
            import black
            
            # Blackを使用してコードを整形
            formatted_code = black.format_str(self.text, mode=black.FileMode())
            self.text = formatted_code
            return True
        except ImportError:
            print("blackがインストールされていません。pip install blackを実行してください。")
            return False
        except Exception as e:
            print(f"コード整形エラー: {str(e)}")
            return False


class CodeEditorToolbar(BoxLayout):
    """コードエディタのツールバー"""
    
    editor = None
    status_text = StringProperty('')
    
    def save_code(self):
        """コードを保存します"""
        if not self.editor:
            return
        
        if self.editor.save_file():
            self.status_text = f"保存しました: {self.editor.file_path}"
        else:
            self.status_text = "保存に失敗しました"
    
    def format_code(self):
        """コードを整形します"""
        if not self.editor:
            return
        
        if self.editor.format_code():
            self.status_text = "コードを整形しました"
        else:
            self.status_text = "コード整形に失敗しました"
    
    def run_code(self):
        """コードを実行します"""
        if not self.editor:
            return
        
        # 実行前に保存
        if self.editor.is_modified:
            if not self.editor.save_file():
                self.status_text = "保存に失敗しました"
                return
        
        # 実行はメインアプリケーションに委譲
        app = self.get_root_window().children[0]
        if hasattr(app, 'run_code'):
            app.run_code(self.editor.file_path)
            self.status_text = f"実行中: {self.editor.file_path}"
        else:
            self.status_text = "実行機能が利用できません"


class CodeEditorContainer(BoxLayout):
    """コードエディタとツールバーを含むコンテナ"""
    
    def __init__(self, **kwargs):
        super(CodeEditorContainer, self).__init__(**kwargs)
        
        # ツールバーとエディタの関連付け
        self.ids.toolbar.editor = self.ids.editor
    
    def get_editor(self):
        """エディタインスタンスを取得します"""
        return self.ids.editor
    
    def load_file(self, file_path):
        """
        ファイルを読み込みます。
        
        Args:
            file_path: 読み込むファイルのパス
            
        Returns:
            読み込みに成功したかどうか
        """
        result = self.ids.editor.load_file(file_path)
        if result:
            self.ids.toolbar.status_text = f"読み込みました: {file_path}"
        else:
            self.ids.toolbar.status_text = "読み込みに失敗しました"
        return result
