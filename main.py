#!/usr/bin/env python3
"""
Manus Agent - メインエントリーポイント

このスクリプトはManus Agentアプリケーションを起動します。
"""

import os
import sys
from src.ui.kivy_application import ArnaApp

if __name__ == "__main__":
    # アプリケーションのルートディレクトリをPythonパスに追加
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # アプリケーションを起動
    ArnaApp().run()
