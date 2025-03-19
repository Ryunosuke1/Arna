#!/usr/bin/env python3
"""
Arna - UI Theme

このモジュールはArnaアプリケーションのUIテーマを定義します。
スウェーデン風ミニマリズムに基づいたカラーパレット、フォント、スタイルを提供します。
"""

from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.utils import platform
import os


# スウェーデン風ミニマリズムのカラーパレット
class SwedishMinimalistColors:
    """スウェーデン風ミニマリズムのカラーパレットを定義するクラス"""
    
    # ベースカラー
    OFF_WHITE = get_color_from_hex("#F9F9F9")
    
    # テキスト
    DARK_GREY = get_color_from_hex("#333333")
    MEDIUM_GREY = get_color_from_hex("#666666")
    
    # アクセント
    SWEDISH_BLUE = get_color_from_hex("#006AA7")
    SWEDISH_YELLOW = get_color_from_hex("#FECC02")
    
    # 背景
    LIGHT_GREY = get_color_from_hex("#F0F0F0")
    
    # セカンダリ
    MEDIUM_LIGHT_GREY = get_color_from_hex("#CCCCCC")
    
    # 状態表示
    SUCCESS = get_color_from_hex("#4CAF50")
    WARNING = get_color_from_hex("#FFC107")
    ERROR = get_color_from_hex("#F44336")
    INFO = get_color_from_hex("#2196F3")


class SwedishMinimalistTheme:
    """スウェーデン風ミニマリズムのUIテーマを定義するクラス"""
    
    # カラーパレット
    colors = SwedishMinimalistColors
    
    # フォント設定
    FONT_FAMILY_REGULAR = "Roboto"
    FONT_FAMILY_LIGHT = "Roboto-Light"
    FONT_FAMILY_MEDIUM = "Roboto-Medium"
    FONT_FAMILY_BOLD = "Roboto-Bold"
    FONT_FAMILY_MONO = "RobotoMono-Regular"
    
    # フォントサイズ
    FONT_SIZE_H1 = sp(24)
    FONT_SIZE_H2 = sp(20)
    FONT_SIZE_H3 = sp(18)
    FONT_SIZE_BODY = sp(14)
    FONT_SIZE_SMALL = sp(12)
    FONT_SIZE_TINY = sp(10)
    
    # パディング
    PADDING_SMALL = dp(4)
    PADDING_MEDIUM = dp(8)
    PADDING_LARGE = dp(16)
    PADDING_XLARGE = dp(24)
    
    # マージン
    MARGIN_SMALL = dp(4)
    MARGIN_MEDIUM = dp(8)
    MARGIN_LARGE = dp(16)
    MARGIN_XLARGE = dp(24)
    
    # 境界線
    BORDER_WIDTH = dp(1)
    BORDER_RADIUS = dp(4)
    
    # アイコンサイズ
    ICON_SIZE_SMALL = dp(16)
    ICON_SIZE_MEDIUM = dp(24)
    ICON_SIZE_LARGE = dp(32)
    
    # ウィジェットの高さ
    BUTTON_HEIGHT = dp(36)
    INPUT_HEIGHT = dp(36)
    TOOLBAR_HEIGHT = dp(48)
    
    @classmethod
    def apply_theme(cls):
        """テーマをアプリケーションに適用します"""
        # ウィンドウの背景色を設定
        Window.clearcolor = cls.colors.OFF_WHITE
        font_path = os.path.join(os.path.dirname(__file__))
        resource_add_path(font_path)
        
        # フォントの登録
        # 注: 実際のアプリケーションでは、フォントファイルが存在することを確認してください
        try:
            LabelBase.register(name=cls.FONT_FAMILY_REGULAR, 
                              fn_regular="fonts/Roboto-Black.ttf")
            LabelBase.register(name=cls.FONT_FAMILY_LIGHT, 
                              fn_regular="fonts/Roboto-Light.ttf")
            LabelBase.register(name=cls.FONT_FAMILY_MEDIUM, 
                              fn_regular="fonts/Roboto-Medium.ttf")
            LabelBase.register(name=cls.FONT_FAMILY_BOLD, 
                              fn_regular="fonts/Roboto-Bold.ttf")
            LabelBase.register(name=cls.FONT_FAMILY_MONO, 
                              fn_regular="fonts/RobotoMono-VariableFont_wght.ttf")
        except Exception as e:
            print(f"フォント登録エラー: {e}")
            print("デフォルトフォントを使用します")
    
    @classmethod
    def get_button_style(cls, primary=True, outline=False):
        """
        ボタンのスタイルを取得します。
        
        Args:
            primary: プライマリボタンかどうか
            outline: アウトラインスタイルかどうか
            
        Returns:
            ボタンスタイルの辞書
        """
        if primary:
            if outline:
                return {
                    "background_color": cls.colors.OFF_WHITE,
                    "color": cls.colors.SWEDISH_BLUE,
                    "border_color": cls.colors.SWEDISH_BLUE,
                    "border_width": cls.BORDER_WIDTH
                }
            else:
                return {
                    "background_color": cls.colors.SWEDISH_BLUE,
                    "color": cls.colors.OFF_WHITE,
                    "border_width": 0
                }
        else:
            if outline:
                return {
                    "background_color": cls.colors.OFF_WHITE,
                    "color": cls.colors.DARK_GREY,
                    "border_color": cls.colors.MEDIUM_LIGHT_GREY,
                    "border_width": cls.BORDER_WIDTH
                }
            else:
                return {
                    "background_color": cls.colors.LIGHT_GREY,
                    "color": cls.colors.DARK_GREY,
                    "border_width": 0
                }
    
    @classmethod
    def get_input_style(cls, focused=False, error=False):
        """
        入力フィールドのスタイルを取得します。
        
        Args:
            focused: フォーカス状態かどうか
            error: エラー状態かどうか
            
        Returns:
            入力フィールドスタイルの辞書
        """
        if error:
            return {
                "background_color": cls.colors.OFF_WHITE,
                "foreground_color": cls.colors.DARK_GREY,
                "border_color": cls.colors.ERROR,
                "border_width": cls.BORDER_WIDTH
            }
        elif focused:
            return {
                "background_color": cls.colors.OFF_WHITE,
                "foreground_color": cls.colors.DARK_GREY,
                "border_color": cls.colors.SWEDISH_BLUE,
                "border_width": cls.BORDER_WIDTH
            }
        else:
            return {
                "background_color": cls.colors.OFF_WHITE,
                "foreground_color": cls.colors.DARK_GREY,
                "border_color": cls.colors.MEDIUM_LIGHT_GREY,
                "border_width": cls.BORDER_WIDTH
            }
