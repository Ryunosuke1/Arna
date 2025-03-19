#!/usr/bin/env python3
"""
Arna - Project View

このモジュールはプロジェクト構造を表示するためのUIコンポーネントを提供します。
スウェーデン風ミニマリズムに基づいたデザインを適用し、
プロジェクト内の関数、パラメータ、戻り値などの構造を階層的に表示します。
"""

from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
from kivy.lang import Builder

# 自作モジュールのインポート
from src.ui.theme import SwedishMinimalistTheme

# KVファイルの読み込み
Builder.load_string('''
#:kivy 2.0.0

<ProjectView>:
    canvas.before:
        Color:
            rgba: app.theme.colors.OFF_WHITE
        Rectangle:
            pos: self.pos
            size: self.size
    
    hide_root: True
    indent_level: dp(20)
    size_hint: 1, 1

<ProjectTreeLabel>:
    color: app.theme.colors.DARK_GREY
    font_name: app.theme.FONT_FAMILY_REGULAR
    font_size: app.theme.FONT_SIZE_BODY
    height: dp(30)
    padding: [app.theme.PADDING_MEDIUM, 0]
    
    canvas.before:
        Color:
            rgba: app.theme.colors.OFF_WHITE if not self.is_selected else app.theme.colors.LIGHT_GREY
        Rectangle:
            pos: self.pos
            size: self.size

<AddFunctionDialog>:
    title: 'Add Function'
    size_hint: None, None
    size: dp(400), dp(300)
    
    BoxLayout:
        orientation: 'vertical'
        padding: app.theme.PADDING_MEDIUM
        spacing: app.theme.PADDING_MEDIUM
        
        Label:
            text: 'Function Name:'
            size_hint_y: None
            height: dp(30)
            color: app.theme.colors.DARK_GREY
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
            halign: 'left'
            text_size: self.size
        
        TextInput:
            id: function_name
            size_hint_y: None
            height: dp(40)
            multiline: False
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
        
        Label:
            text: 'Description:'
            size_hint_y: None
            height: dp(30)
            color: app.theme.colors.DARK_GREY
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
            halign: 'left'
            text_size: self.size
        
        TextInput:
            id: function_description
            size_hint_y: None
            height: dp(80)
            multiline: True
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            spacing: app.theme.PADDING_MEDIUM
            
            Button:
                text: 'Cancel'
                size_hint_x: 0.5
                background_color: app.theme.colors.LIGHT_GREY
                color: app.theme.colors.DARK_GREY
                font_name: app.theme.FONT_FAMILY_REGULAR
                font_size: app.theme.FONT_SIZE_BODY
                on_release: root.dismiss()
            
            Button:
                text: 'Add'
                size_hint_x: 0.5
                background_color: app.theme.colors.SWEDISH_BLUE
                color: app.theme.colors.OFF_WHITE
                font_name: app.theme.FONT_FAMILY_REGULAR
                font_size: app.theme.FONT_SIZE_BODY
                on_release: root.add_function()

<AddParameterDialog>:
    title: 'Add Parameter'
    size_hint: None, None
    size: dp(400), dp(300)
    
    BoxLayout:
        orientation: 'vertical'
        padding: app.theme.PADDING_MEDIUM
        spacing: app.theme.PADDING_MEDIUM
        
        Label:
            text: 'Parameter Name:'
            size_hint_y: None
            height: dp(30)
            color: app.theme.colors.DARK_GREY
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
            halign: 'left'
            text_size: self.size
        
        TextInput:
            id: parameter_name
            size_hint_y: None
            height: dp(40)
            multiline: False
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
        
        Label:
            text: 'Description:'
            size_hint_y: None
            height: dp(30)
            color: app.theme.colors.DARK_GREY
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
            halign: 'left'
            text_size: self.size
        
        TextInput:
            id: parameter_description
            size_hint_y: None
            height: dp(80)
            multiline: True
            font_name: app.theme.FONT_FAMILY_REGULAR
            font_size: app.theme.FONT_SIZE_BODY
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            spacing: app.theme.PADDING_MEDIUM
            
            Button:
                text: 'Cancel'
                size_hint_x: 0.5
                background_color: app.theme.colors.LIGHT_GREY
                color: app.theme.colors.DARK_GREY
                font_name: app.theme.FONT_FAMILY_REGULAR
                font_size: app.theme.FONT_SIZE_BODY
                on_release: root.dismiss()
            
            Button:
                text: 'Add'
                size_hint_x: 0.5
                background_color: app.theme.colors.SWEDISH_BLUE
                color: app.theme.colors.OFF_WHITE
                font_name: app.theme.FONT_FAMILY_REGULAR
                font_size: app.theme.FONT_SIZE_BODY
                on_release: root.add_parameter()
''')


class ProjectTreeLabel(TreeViewLabel):
    """プロジェクトツリーのラベル"""
    
    node_type = StringProperty('')
    node_id = StringProperty('')
    
    def __init__(self, **kwargs):
        self.node_type = kwargs.pop('node_type', '')
        self.node_id = kwargs.pop('node_id', '')
        super(ProjectTreeLabel, self).__init__(**kwargs)


class ProjectView(TreeView):
    """プロジェクト構造を表示するツリービュー"""
    
    def __init__(self, **kwargs):
        super(ProjectView, self).__init__(**kwargs)
        
        # ルートノードの追加
        self.root_node = self.add_node(ProjectTreeLabel(
            text='Project',
            node_type='project',
            node_id='root',
            is_open=True
        ))
        
        # サンプルデータの追加（実際のアプリケーションでは動的に生成）
        self.add_sample_data()
    
    def add_sample_data(self):
        """サンプルデータを追加します（デモ用）"""
        # サンプル関数の追加
        main_func = self.add_function('main', 'Main entry point of the application')
        process_func = self.add_function('process_data', 'Process input data and return results')
        
        # サンプルパラメータの追加
        self.add_parameter(process_func, 'data', 'Input data to process')
        self.add_parameter(process_func, 'options', 'Processing options')
        
        # サンプル戻り値の追加
        self.add_return(process_func, 'Processed data results')
        
        # サンプルロジックの追加
        self.add_logic(process_func, 'Validate input data, apply processing algorithms, return results')
    
    def add_function(self, name, description, parent=None):
        """
        関数ノードを追加します。
        
        Args:
            name: 関数名
            description: 関数の説明
            parent: 親ノード（省略時はルートノード）
            
        Returns:
            追加された関数ノード
        """
        parent = parent or self.root_node
        
        # 関数ノードの追加
        function_node = self.add_node(ProjectTreeLabel(
            text=f'{name}()',
            node_type='function',
            node_id=name,
            is_open=True
        ), parent)
        
        # 説明ノードの追加
        self.add_node(ProjectTreeLabel(
            text=f'Description: {description}',
            node_type='description',
            node_id=f'{name}_desc'
        ), function_node)
        
        return function_node
    
    def add_parameter(self, function_node, name, description):
        """
        パラメータノードを追加します。
        
        Args:
            function_node: 親関数ノード
            name: パラメータ名
            description: パラメータの説明
            
        Returns:
            追加されたパラメータノード
        """
        # パラメータセクションの取得または作成
        params_node = None
        for node in self.iterate_all_nodes():
            if (node.parent_node == function_node and 
                getattr(node, 'node_type', '') == 'parameters'):
                params_node = node
                break
        
        if not params_node:
            params_node = self.add_node(ProjectTreeLabel(
                text='Parameters',
                node_type='parameters',
                node_id=f'{function_node.node_id}_params',
                is_open=True
            ), function_node)
        
        # パラメータノードの追加
        param_node = self.add_node(ProjectTreeLabel(
            text=f'{name}',
            node_type='parameter',
            node_id=f'{function_node.node_id}_{name}'
        ), params_node)
        
        # 説明ノードの追加
        self.add_node(ProjectTreeLabel(
            text=f'Description: {description}',
            node_type='description',
            node_id=f'{function_node.node_id}_{name}_desc'
        ), param_node)
        
        return param_node
    
    def add_return(self, function_node, description):
        """
        戻り値ノードを追加します。
        
        Args:
            function_node: 親関数ノード
            description: 戻り値の説明
            
        Returns:
            追加された戻り値ノード
        """
        # 戻り値ノードの追加
        return_node = self.add_node(ProjectTreeLabel(
            text='Returns',
            node_type='returns',
            node_id=f'{function_node.node_id}_returns'
        ), function_node)
        
        # 説明ノードの追加
        self.add_node(ProjectTreeLabel(
            text=f'Description: {description}',
            node_type='description',
            node_id=f'{function_node.node_id}_returns_desc'
        ), return_node)
        
        return return_node
    
    def add_logic(self, function_node, description):
        """
        ロジックノードを追加します。
        
        Args:
            function_node: 親関数ノード
            description: ロジックの説明
            
        Returns:
            追加されたロジックノード
        """
        # ロジックノードの追加
        logic_node = self.add_node(ProjectTreeLabel(
            text='Logic',
            node_type='logic',
            node_id=f'{function_node.node_id}_logic'
        ), function_node)
        
        # 説明ノードの追加
        self.add_node(ProjectTreeLabel(
            text=f'Description: {description}',
            node_type='description',
            node_id=f'{function_node.node_id}_logic_desc'
        ), logic_node)
        
        return logic_node
    
    def clear_project(self):
        """プロジェクトツリーをクリアします"""
        self.clear_widgets()
        
        # ルートノードの再追加
        self.root_node = self.add_node(ProjectTreeLabel(
            text='Project',
            node_type='project',
            node_id='root',
            is_open=True
        ))


class AddFunctionDialog(Popup):
    """関数追加ダイアログ"""
    
    project_view = ObjectProperty(None)
    parent_node = ObjectProperty(None)
    
    def __init__(self, project_view, parent_node=None, **kwargs):
        super(AddFunctionDialog, self).__init__(**kwargs)
        self.project_view = project_view
        self.parent_node = parent_node
    
    def add_function(self):
        """ダイアログの入力から関数を追加します"""
        name = self.ids.function_name.text.strip()
        description = self.ids.function_description.text.strip()
        
        if name:
            self.project_view.add_function(name, description, self.parent_node)
            self.dismiss()


class AddParameterDialog(Popup):
    """パラメータ追加ダイアログ"""
    
    project_view = ObjectProperty(None)
    function_node = ObjectProperty(None)
    
    def __init__(self, project_view, function_node, **kwargs):
        super(AddParameterDialog, self).__init__(**kwargs)
        self.project_view = project_view
        self.function_node = function_node
    
    def add_parameter(self):
        """ダイアログの入力からパラメータを追加します"""
        name = self.ids.parameter_name.text.strip()
        description = self.ids.parameter_description.text.strip()
        
        if name and self.function_node:
            self.project_view.add_parameter(self.function_node, name, description)
            self.dismiss()
