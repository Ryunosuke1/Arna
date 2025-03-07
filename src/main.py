"""
Arna - AIエージェントを用いたPythonコード生成アシスタント

チーム形式でAIエージェントが質問を通じてユーザーの要件を理解し、
段階的にコードを生成していきます。
"""

import flet as ft
from chat_ui import VyTheme
from application import Application

async def main(page: ft.Page):
    """アプリケーションのエントリーポイント"""
    # page.fonts = {

    # }
    # アプリケーション全体の設定
    page.theme = ft.Theme(
        color_scheme_seed=VyTheme.PRIMARY,
        page_transitions=ft.PageTransitionsTheme.macos
    )
    
    # アプリケーションの初期化
    app = Application()
    current_tab = 0
    
    # コンテナの参照
    view_container_ref = ft.Ref[ft.Container]()
    nav_bar_ref = ft.Ref[ft.NavigationBar]()
    
    def handle_nav_change(e):
        nonlocal current_tab
        current_tab = e.control.selected_index
        view_container_ref.current.content = get_current_view()
        page.update()
    
    def get_current_view():
        if current_tab == 0:
            return app.discussion_view.build()
        elif current_tab == 1:
            return app.download_view.build()
        else:
            return app.settings_view.build()
    
    # ナビゲーションバーの構築
    page.navigation_bar = ft.NavigationBar(
        ref=nav_bar_ref,
        bgcolor=VyTheme.CARD_BG,
        selected_index=current_tab,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CHAT, label="AI議論"),
            ft.NavigationBarDestination(icon=ft.Icons.DOWNLOAD, label="ダウンロード"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="設定")
        ],
        on_change=handle_nav_change
    )
    
    # メインコンテナの初期化
    main_container = ft.Container(
        bgcolor=VyTheme.BACKGROUND,
        content=ft.Column([
            ft.VerticalDivider(color=VyTheme.BORDER_COLOR),
            ft.Container(
                content=get_current_view(),
                padding=20,
                margin=ft.margin.only(bottom=60),  # ナビゲーションバーの高さ分マージン
                expand=True,
                ref=view_container_ref
            )
        ], expand=True),
        expand=True
    )
    
    # メインコンテナをページに追加（SafeAreaでラップ）
    page.add(ft.SafeArea(main_container))

def start():
    """アプリケーションを起動"""
    ft.app(main)

if __name__ == "__main__":
    start()
