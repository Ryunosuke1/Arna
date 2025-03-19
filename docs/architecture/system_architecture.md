# Arna システムアーキテクチャ設計

## 1. 概要

Arnaは、MetaGPTベースでDevinのような複雑なソフトウェア開発能力を持つ汎用AIエージェントです。Webブラウザやテキストエディタを操作でき、複雑なプログラムの開発とテストを自律的に行うことができます。KivyによるデスクトップアプリケーションとしてUIを実装し、OpenAI Compatible APIを使用してLLMと連携します。

### 主要機能
- 複雑なソフトウェア開発とテスト機能
- Webブラウザやテキストエディタの操作機能
- タスクの超細分化機能
- Code Structure Toolsによるコード構造管理
- YAMLベースのコード構造定義と管理
- スウェーデン風ミニマリズムに基づくUI

## 2. アーキテクチャ概要

Arnaは4層アーキテクチャを採用し、各層の責任を明確に分離します：

1. **UI層**: ユーザーとの対話を担当（スウェーデン風ミニマリズムデザイン）
2. **アプリケーション層**: ビジネスロジックとワークフローを管理
3. **サービス層**: 外部サービスとの連携や共通機能を提供
4. **インフラ層**: データ永続化や外部システムとの通信を担当

## 3. コンポーネント構成

### 3.1 コアコンポーネント

#### AgentCore
- **TaskStatus**: タスクの状態を管理するクラス
- **Task**: タスクの基本単位を表現するクラス
- **TaskPlanner**: タスクの計画と分割を行うクラス
- **MemoryManager**: エージェントの記憶と状態を管理するクラス
- **ExecutionEngine**: タスクの実行を制御するクラス

#### CodeStructureManager
- **ProjectStructure**: プロジェクト全体の構造を管理
- **FunctionDefinition**: 関数定義を管理
- **ParameterDefinition**: パラメータ定義を管理
- **ReturnDefinition**: 戻り値定義を管理
- **LogicDefinition**: 関数ロジック定義を管理
- **YAMLSerializer**: 構造データのYAML形式シリアライズ/デシリアライズ
- **CodeGenerator**: 構造データからコードを生成

### 3.2 UIコンポーネント（スウェーデン風ミニマリズム）

#### KivyApplication
- メインアプリケーションウィンドウ
- 全体レイアウトの管理
- テーマとスタイルの適用

#### ProjectView
- プロジェクト構造の表示
- ファイルツリーの管理
- コンテキストメニュー

#### CodeEditor
- コードの編集機能
- シンタックスハイライト
- 自動補完

#### OutputConsole
- 実行結果の表示
- ログ出力
- エラーメッセージの表示

### 3.3 サービスコンポーネント

#### LLMService
- **LLMConnector**: OpenAI Compatible APIとの通信
- **PromptGenerator**: 効果的なプロンプトの生成
- **ResponseParser**: LLMレスポンスの解析

#### ToolIntegration
- **BrowserController**: Webブラウザの操作
- **EditorController**: テキストエディタの操作
- **FileSystemController**: ファイルシステムの操作

#### TestingService
- **TestRunner**: テストの実行
- **TestResultAnalyzer**: テスト結果の分析
- **CoverageReporter**: コードカバレッジの報告

### 3.4 連携・拡張コンポーネント

#### EventBus
- コンポーネント間の疎結合な通信を実現
- イベント駆動型アーキテクチャのサポート

#### DependencyInjection
- コンポーネントの依存関係を管理
- テスト容易性の向上

#### PluginSystem
- 機能拡張のためのプラグインシステム
- サードパーティ統合のサポート

## 4. データフロー

1. **ユーザー入力** → UI層 → アプリケーション層
2. アプリケーション層 → **タスク生成** → TaskPlanner
3. TaskPlanner → **タスク分割** → 複数のサブタスク
4. サブタスク → **実行** → ExecutionEngine
5. ExecutionEngine → **ツール呼び出し** → ToolIntegration
6. ToolIntegration → **外部操作** → ブラウザ/エディタ/ファイルシステム
7. ExecutionEngine → **LLM呼び出し** → LLMService
8. LLMService → **API通信** → OpenAI Compatible API
9. 実行結果 → **状態更新** → MemoryManager
10. 実行結果 → **UI更新** → UI層 → **ユーザーへのフィードバック**

## 5. Code Structure Tools設計

### 5.1 機能一覧

- **create_project(name, description)**: 新しいプロジェクト構造を作成
- **add_function(name, description, parent_path?)**: 関数定義を追加
- **add_parameter(function_path, name, description)**: 関数にパラメータを追加
- **add_return(function_path, description)**: 関数に戻り値の説明を追加
- **add_logic(function_path, description)**: 関数にロジックの説明を追加
- **show_structure()**: 現在のコード構造を表示
- **show_summary()**: プロジェクトの概要を表示
- **save_yaml(file_path)**: 構造をYAMLファイルに保存
- **load_yaml(file_path)**: YAMLファイルから構造を読み込み
- **generate_code(output_path)**: Pythonコードを生成

### 5.2 YAML構造定義

```yaml
name: <name>
description: <description>
code_structure:
  - function:
      name: <name>
      description: <description>
      parameters:
        - name: <name>
          description: <description>
      returns:
        description: <description>
      logic:
        description: <description>
      code_structure:
        - nested functions/classes
```

### 5.3 コード生成プロセス

1. YAML構造の解析
2. テンプレートエンジン（Jinja2）による変換
3. コードフォーマット（Black）の適用
4. 出力ファイルへの書き込み

## 6. スウェーデン風ミニマリズムUIデザイン原則

### 6.1 デザイン原則

- **シンプルさ**: 不必要な要素を排除し、本質的な機能に焦点
- **機能性**: 美しさと実用性の両立
- **一貫性**: 統一されたデザイン言語の使用
- **自然素材の表現**: デジタル空間での自然素材の質感の再現
- **余白の活用**: 適切な余白によるコンテンツの強調
- **モノクロベース**: 限られたアクセントカラーの効果的な使用

### 6.2 カラーパレット

- **ベースカラー**: オフホワイト (#F9F9F9)
- **テキスト**: ダークグレー (#333333)
- **アクセント**: スウェーデンブルー (#006AA7)、スウェーデンイエロー (#FECC02)
- **背景**: ライトグレー (#F0F0F0)
- **セカンダリ**: ミディアムグレー (#CCCCCC)

### 6.3 タイポグラフィ

- **プライマリフォント**: Roboto（サンセリフ）
- **セカンダリフォント**: Roboto Mono（コードエディタ用）
- **階層的サイズ**: 明確な視覚的階層を作るフォントサイズの使い分け

### 6.4 コンポーネントデザイン

- **フラットデザイン**: 過度な装飾や影を避ける
- **境界線の最小化**: 必要な場合のみ薄い境界線を使用
- **アイコン**: シンプルで直感的なアイコンセット
- **インタラクション**: 控えめながらも明確なフィードバック

## 7. 技術スタック

- **フロントエンド**: Kivy, KivyMD
- **バックエンド**: Python
- **テンプレートエンジン**: Jinja2
- **データシリアライゼーション**: PyYAML
- **コード品質**: Black, isort, mypy, flake8
- **テスト**: pytest
- **外部連携**: OpenAI Compatible API

## 8. 拡張性と将来の展望

- **プラグインシステム**: サードパーティによる機能拡張
- **多言語サポート**: 複数のプログラミング言語への対応
- **チーム協業機能**: 複数エージェントの協調作業
- **クラウド連携**: クラウドベースのリソース活用
- **継続的学習**: エージェントの経験からの学習メカニズム

## 9. セキュリティ考慮事項

- **APIキー管理**: 安全なAPIキーの保存と管理
- **コード実行の分離**: サンドボックス環境でのコード実行
- **データ保護**: ローカルデータの暗号化
- **権限管理**: 最小権限の原則に基づくアクセス制御
