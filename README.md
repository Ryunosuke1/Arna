# Arna

metagptベースでDevinのような複雑なソフトウェア開発能力を持つ汎用Agent

## 概要

Manus Agentは、Webブラウザやテキストエディタを操作でき、複雑なプログラムの開発とテストを自律的に行うことができる汎用AIエージェントです。Kivyによるデスクトップアプリケーションとして実装され、OpenAI Compatible APIを使用してLLMと連携します。

## 主要機能

- 複雑なソフトウェア開発とテスト機能
- Webブラウザやテキストエディタの操作機能
- タスクの超細分化機能
- Code Structure Toolsによるコード構造管理
- YAMLベースのコード構造定義と管理

## システム要件

- Python 3.8以上
- インターネット接続
- OpenAI互換APIへのアクセス

## インストール方法

```bash
# リポジトリをクローン
git clone https://github.com/your-username/manus-agent.git
cd manus-agent

# 依存パッケージのインストール
pip install -e .
```

## 使用方法

```bash
# アプリケーションの起動
python main.py
```

## プロジェクト構造

```
manus_agent/
├── docs/                  # ドキュメント
├── src/                   # ソースコード
│   ├── core/              # エージェントコアコンポーネント
│   ├── services/          # サービスコンポーネント
│   ├── tools/             # ツールコンポーネント
│   └── ui/                # UIコンポーネント
├── templates/             # テンプレート
├── tests/                 # テストコード
├── main.py                # メインエントリーポイント
├── setup.py               # セットアップスクリプト
└── README.md              # READMEファイル
```

## 開発者向け情報

### テストの実行

```bash
# すべてのテストを実行
pytest

# 特定のテストを実行
pytest tests/test_code_structure.py
```

### パッケージの作成

```bash
# ソースディストリビューションの作成
python setup.py sdist

# ホイールの作成
python setup.py bdist_wheel
```

## ライセンス

MIT License

## 謝辞

このプロジェクトは以下のオープンソースプロジェクトを使用しています：

- Kivy
- KivyMD
- PyYAML
- Jinja2
- Pytest
