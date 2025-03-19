#!/usr/bin/env python3
"""
Arna - Output Console

このモジュールは出力コンソールUIコンポーネントを提供します。
スウェーデン風ミニマリズムに基づいたデザインを適用し、
コマンド実行結果、ログメッセージ、エラーメッセージなどを表示します。
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
import time
import re

# 自作モジュールのインポート
from src.ui.theme import SwedishMinimalistTheme

# KVファイルの読み込み
Builder.load_string('''
#:kivy 2.0.0

<ConsoleOutput>:
    readonly: True
    background_color: app.theme.colors.OFF_WHITE
    foreground_color: app.theme.colors.DARK_GREY
    font_name: app.theme.FONT_FAMILY_MONO
    font_size: app.theme.FONT_SIZE_SMALL
    padding: [app.theme.PADDING_MEDIUM, app.theme.PADDING_MEDIUM]
    
    canvas.before:
        Color:
            rgba: app.theme.colors.OFF_WHITE
        Rectangle:
            pos: self.pos
            size: self.size

<OutputConsole>:
    orientation: 'vertical'
    
    BoxLayout:
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
            text: 'Clear'
            size_hint_x: None
            width: dp(80)
            background_color: app.theme.colors.SWEDISH_BLUE
            color: app.theme.colors.OFF_WHITE
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
            on_release: root.clear_output()
        
        Button:
            text: 'Copy'
            size_hint_x: None
            width: dp(80)
            background_color: app.theme.colors.SWEDISH_BLUE
            color: app.theme.colors.OFF_WHITE
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
            on_release: root.copy_output()
        
        Label:
            text: root.status_text
            color: app.theme.colors.DARK_GREY
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_SMALL
            text_size: self.size
            halign: 'right'
            valign: 'middle'
    
    ScrollView:
        id: scroll_view
        do_scroll_x: False
        
        ConsoleOutput:
            id: console_output
            size_hint: 1, None
            height: max(self.minimum_height, scroll_view.height)
''')


class ConsoleOutput(TextInput):
    """コンソール出力を表示するテキスト入力ウィジェット"""
    
    def __init__(self, **kwargs):
        super(ConsoleOutput, self).__init__(**kwargs)
        self.bind(focus=self.on_focus)
    
    def on_focus(self, instance, value):
        """フォーカスが変更されたときのコールバック"""
        # 読み取り専用のため、フォーカスを解除
        if value:
            self.focus = False


class OutputConsole(BoxLayout):
    """出力コンソールコンポーネント"""
    
    status_text = StringProperty('')
    message_colors = {
        'info': SwedishMinimalistTheme.colors.DARK_GREY,
        'success': SwedishMinimalistTheme.colors.SUCCESS,
        'warning': SwedishMinimalistTheme.colors.WARNING,
        'error': SwedishMinimalistTheme.colors.ERROR,
    }
    
    def __init__(self, **kwargs):
        super(OutputConsole, self).__init__(**kwargs)
        self.message_history = []
    
    def add_message(self, message, message_type='info'):
        """
        メッセージを追加します。
        
        Args:
            message: 追加するメッセージ
            message_type: メッセージの種類（'info', 'success', 'warning', 'error'）
        """
        # タイムスタンプの追加
        timestamp = time.strftime('%H:%M:%S')
        
        # メッセージの整形
        formatted_message = f"[{timestamp}] {message}\n"
        
        # メッセージの保存
        self.message_history.append((formatted_message, message_type))
        
        # メッセージの表示
        self._update_console_output()
        
        # スクロールを最下部に移動
        Clock.schedule_once(self._scroll_to_end, 0.1)
    
    def add_command_output(self, command, output, exit_code=0):
        """
        コマンド実行結果を追加します。
        
        Args:
            command: 実行したコマンド
            output: コマンドの出力
            exit_code: 終了コード
        """
        # タイムスタンプの追加
        timestamp = time.strftime('%H:%M:%S')
        
        # コマンドの表示
        command_message = f"[{timestamp}] $ {command}\n"
        self.message_history.append((command_message, 'info'))
        
        # 出力の表示
        if output:
            # 長い出力は省略
            if len(output) > 1000:
                output = output[:1000] + "...\n(output truncated)"
            
            self.message_history.append((output + "\n", 'info'))
        
        # 終了コードの表示
        message_type = 'success' if exit_code == 0 else 'error'
        exit_message = f"[{timestamp}] Exit code: {exit_code}\n"
        self.message_history.append((exit_message, message_type))
        
        # メッセージの表示
        self._update_console_output()
        
        # スクロールを最下部に移動
        Clock.schedule_once(self._scroll_to_end, 0.1)
    
    def clear_output(self):
        """出力をクリアします"""
        self.message_history = []
        self.ids.console_output.text = ""
        self.status_text = "出力をクリアしました"
    
    def copy_output(self):
        """出力をクリップボードにコピーします"""
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.ids.console_output.text)
        self.status_text = "出力をコピーしました"
    
    def _update_console_output(self):
        """コンソール出力を更新します"""
        # テキストの更新
        self.ids.console_output.text = "".join([msg[0] for msg in self.message_history])
    
    def _scroll_to_end(self, dt):
        """スクロールを最下部に移動します"""
        self.ids.console_output.cursor = (0, len(self.ids.console_output.text))
        self.ids.scroll_view.scroll_y = 0
    
    def get_output_text(self):
        """出力テキストを取得します"""
        return self.ids.console_output.text
