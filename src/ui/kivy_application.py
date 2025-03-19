#!/usr/bin/env python3
"""
Arna - Kivy Application

このモジュールはArnaアプリケーションのメインウィンドウを提供します。
スウェーデン風ミニマリズムに基づいたUIデザインを適用し、
アプリケーション全体のレイアウトとナビゲーションを管理します。
"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.splitter import Splitter
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp

# 自作モジュールのインポート
from src.ui.theme import SwedishMinimalistTheme
from src.ui.project_view import ProjectView
from src.ui.code_editor import CodeEditor
from src.ui.output_console import OutputConsole

# KVファイルの読み込み
Builder.load_string('''
#:kivy 2.0.0

<ArnaMainWindow>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: app.theme.colors.OFF_WHITE
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        size_hint_y: None
        height: app.theme.TOOLBAR_HEIGHT
        canvas.before:
            Color:
                rgba: app.theme.colors.SWEDISH_BLUE
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: 'Arna'
            color: app.theme.colors.OFF_WHITE
            font_size: app.theme.FONT_SIZE_H2
            font_name: app.theme.FONT_FAMILY_MEDIUM
            size_hint_x: None
            width: dp(100)
            padding: [app.theme.PADDING_MEDIUM, 0]
        
        BoxLayout:
            orientation: 'horizontal'
            padding: [app.theme.PADDING_MEDIUM, 0]
            spacing: app.theme.PADDING_MEDIUM
            
            Button:
                text: 'New Project'
                size_hint_x: None
                width: dp(120)
                background_color: app.theme.colors.OFF_WHITE
                color: app.theme.colors.SWEDISH_BLUE
                font_name: app.theme.FONT_FAMILY_REGULAR
                font_size: app.theme.FONT_SIZE_BODY
            
            Button:
                text: 'Open Project'
                size_hint_x: None
                width: dp(120)
                background_color: app.theme.colors.OFF_WHITE
                color: app.theme.colors.SWEDISH_BLUE
                font_name: app.theme.FONT_FAMILY_REGULAR
                font_size: app.theme.FONT_SIZE_BODY
            
            Button:
                text: 'Save'
                size_hint_x: None
                width: dp(80)
                background_color: app.theme.colors.OFF_WHITE
                color: app.theme.colors.SWEDISH_BLUE
                font_name: app.theme.FONT_FAMILY_REGULAR
                font_size: app.theme.FONT_SIZE_BODY
    
    BoxLayout:
        orientation: 'horizontal'
        
        Splitter:
            sizable_from: 'right'
            min_size: dp(200)
            max_size: dp(400)
            size_hint_x: None
            width: dp(250)
            
            BoxLayout:
                orientation: 'vertical'
                canvas.before:
                    Color:
                        rgba: app.theme.colors.LIGHT_GREY
                    Rectangle:
                        pos: self.pos
                        size: self.size
                
                Label:
                    text: 'Project Structure'
                    size_hint_y: None
                    height: dp(40)
                    color: app.theme.colors.DARK_GREY
                    font_name: app.theme.FONT_FAMILY_MEDIUM
                    font_size: app.theme.FONT_SIZE_H3
                    canvas.before:
                        Color:
                            rgba: app.theme.colors.OFF_WHITE
                        Rectangle:
                            pos: self.pos
                            size: self.size
                
                ScrollView:
                    id: project_scroll
                    do_scroll_x: False
                    
                    # ProjectViewウィジェットはPythonコードで追加
        
        BoxLayout:
            orientation: 'vertical'
            
            TabbedPanel:
                id: editor_tabs
                do_default_tab: False
                tab_width: dp(150)
                tab_height: dp(40)
                background_color: app.theme.colors.OFF_WHITE
                
                # タブはPythonコードで追加
            
            Splitter:
                sizable_from: 'top'
                min_size: dp(100)
                max_size: dp(300)
                size_hint_y: None
                height: dp(200)
                
                BoxLayout:
                    orientation: 'vertical'
                    canvas.before:
                        Color:
                            rgba: app.theme.colors.LIGHT_GREY
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    
                    Label:
                        text: 'Console Output'
                        size_hint_y: None
                        height: dp(30)
                        color: app.theme.colors.DARK_GREY
                        font_name: app.theme.FONT_FAMILY_MEDIUM
                        font_size: app.theme.FONT_SIZE_BODY
                        canvas.before:
                            Color:
                                rgba: app.theme.colors.OFF_WHITE
                            Rectangle:
                                pos: self.pos
                                size: self.size
                    
                    # OutputConsoleウィジェットはPythonコードで追加

<CodeStructureToolbar>:
    orientation: 'horizontal'
    size_hint_y: None
    height: app.theme.TOOLBAR_HEIGHT
    padding: [app.theme.PADDING_MEDIUM, app.theme.PADDING_SMALL]
    spacing: app.theme.PADDING_MEDIUM
    canvas.before:
        Color:
            rgba: app.theme.colors.OFF_WHITE
        Rectangle:
            pos: self.pos
            size: self.size
    
    Button:
        text: 'Add Function'
        size_hint_x: None
        width: dp(120)
        background_color: app.theme.colors.SWEDISH_BLUE
        color: app.theme.colors.OFF_WHITE
        font_name: app.theme.FONT_FAMILY_REGULAR
        font_size: app.theme.FONT_SIZE_BODY
        on_release: app.add_function()
    
    Button:
        text: 'Add Parameter'
        size_hint_x: None
        width: dp(120)
        background_color: app.theme.colors.SWEDISH_BLUE
        color: app.theme.colors.OFF_WHITE
        font_name: app.theme.FONT_FAMILY_REGULAR
        font_size: app.theme.FONT_SIZE_BODY
        on_release: app.add_parameter()
    
    Button:
        text: 'Generate Code'
        size_hint_x: None
        width: dp(120)
        background_color: app.theme.colors.SWEDISH_BLUE
        color: app.theme.colors.OFF_WHITE
        font_name: app.theme.FONT_FAMILY_REGULAR
        font_size: app.theme.FONT_SIZE_BODY
        on_release: app.generate_code()
''')


class ArnaMainWindow(BoxLayout):
    """Arnaアプリケーションのメインウィンドウ"""
    
    def __init__(self, **kwargs):
        super(ArnaMainWindow, self).__init__(**kwargs)
        
        # プロジェクトビューの追加
        self.project_view = ProjectView()
        self.ids.project_scroll.add_widget(self.project_view)
        
        # コードエディタの初期タブを追加
        self.add_editor_tab("Welcome", "Welcome to Arna!")
        
        # コンソール出力の追加
        self.output_console = OutputConsole()
        self.ids.editor_tabs.parent.children[0].add_widget(self.output_console)
        
        # Code Structure Toolbarの追加
        self.code_structure_toolbar = CodeStructureToolbar()
        self.add_widget(self.code_structure_toolbar)
    
    def add_editor_tab(self, title, content=""):
        """
        エディタタブを追加します。
        
        Args:
            title: タブのタイトル
            content: 初期コンテンツ
        """
        tab_header = TabbedPanelHeader(text=title)
        editor = CodeEditor(text=content)
        tab_header.content = editor
        self.ids.editor_tabs.add_widget(tab_header)
        self.ids.editor_tabs.switch_to(tab_header)
        return editor


class CodeStructureToolbar(BoxLayout):
    """Code Structure Toolsのツールバー"""
    pass


class ArnaApp(App):
    """Arnaアプリケーションのメインクラス"""
    
    theme = SwedishMinimalistTheme
    
    def build(self):
        """アプリケーションのUIを構築します"""
        # テーマの適用
        self.theme.apply_theme()
        
        # ウィンドウサイズの設定
        Window.size = (1200, 800)
        Window.minimum_width = 800
        Window.minimum_height = 600
        
        # メインウィンドウの作成
        self.main_window = ArnaMainWindow()
        return self.main_window
    
    def add_function(self):
        """関数を追加するダイアログを表示します"""
        # 実装はこれから
        self.main_window.output_console.add_message("Add Function clicked", "info")
    
    def add_parameter(self):
        """パラメータを追加するダイアログを表示します"""
        # 実装はこれから
        self.main_window.output_console.add_message("Add Parameter clicked", "info")
    
    def generate_code(self):
        """コードを生成します"""
        # 実装はこれから
        self.main_window.output_console.add_message("Generate Code clicked", "info")


if __name__ == '__main__':
    ArnaApp().run()
