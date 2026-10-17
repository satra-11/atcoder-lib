# `todo.md`の拡充およびADR更新計画

AtCoder用のライブラリ展開ツール（Expander）の開発、およびライブラリ自体の拡充に向けて、現在の`todo.md`のタスクを詳細化します。
ユーザーからのフィードバックに基づき、パッケージ管理には `uv` を使用し、インポート検知には `AST` を採用します。

## Proposed Changes

### 1. ドキュメントの更新 (ADR)

#### [MODIFY] [docs/adrs/001-identify-import.md](file:///Users/satron/Desktop/atcoder-lib/docs/adrs/001-identify-import.md)

- インポート検知方式として「3. 抽象構文木 (AST: Abstract Syntax Tree)」を採用する旨を追記し、決定事項（Decision）として明記します。

### 2. `todo.md` の拡充

#### [MODIFY] [todo.md](file:///Users/satron/Desktop/atcoder-lib/todo.md)

以下のセクションとタスクを追加・再構築します。

**1. 競技プログラミング用ライブラリの実装 (Algorithms & Data Structures)** _(新規追加)_
AtCoderで頻出となるアルゴリズムやデータ構造を自作ライブラリとして実装するためのタスクを追加します。

- データ構造 (Data Structures)
  - [ ] Union-Find (Disjoint Set Union)
  - [ ] セグメント木 (Segment Tree) / 遅延評価セグメント木 (Lazy Segment Tree)
  - [ ] フェニック木 (Fenwick Tree / Binary Indexed Tree)
- グラフアルゴリズム (Graph)
  - [ ] ダイクストラ法 (Dijkstra's Algorithm)
  - [ ] ベルマンフォード法 / ワーシャルフロイド法
  - [ ] 最小全域木 (Kruskal法 / Prim法)
  - [ ] トポロジカルソート
- 整数・数学 (Math)
  - [ ] 拡張ユークリッドの互除法 (Extended GCD)
  - [ ] 繰り返し二乗法 (Mod Pow) / 逆元 (Mod Inv)
  - [ ] 素数判定 / エラトステネスの篩 (Sieve of Eratosthenes)
  - [ ] 組み合わせ計算 (nCr, nPr, 階乗)

**2. インポート検知・依存解決の実装 (Import Detection & Resolution)**

- [ ] 抽象構文木 (AST) を用いたインポート文の検知処理を実装する
- [ ] 展開対象の自作ライブラリと、標準ライブラリ（`sys`など）を区別するロジックを実装する
- [ ] 複数モジュールから同じライブラリがインポートされた際の「依存関係の重複排除」を実装する

**3. 展開用コードの実装 (Expander CLI/Core)**

- [ ] `atcoder-python-snippets-expander` を参考に要件を整理する
- [ ] 外部からライブラリとして呼び出せるインターフェース設計
- [ ] CLIツールとして実行できるようエントリーポイントを作成する (例: `argparse` で入出力ファイルを受け取る)
- [ ] 「ブロック分割型」の展開ロジック実装（標準import -> 自作ライブラリ展開 -> メインコード）

**4. テストの充実化 (Testing)**

- [ ] `uv` を用いたパッケージ・依存関係の管理設定 ( `pytest` 等の導入 )
- [ ] pytestのセットアップとディレクトリ構成の作成
- [ ] ASTを用いたインポート検知ロジックの単体テスト
- [ ] 依存解決・重複排除の単体テスト
- [ ] 実際のAtCoderの解答コードを模した結合テスト（展開後のコードが正常に実行できるか）
- [ ] 自動テスト環境（CI/CD または pre-commit 等）の構築

**5. 開発環境・コード品質 (DevEnv & Linting)**

- [ ] Linter/Formatterの導入と設定 (例: ruff, mypy)

**6. ドキュメント (Documentation)**

- [ ] `README.md` にツールの使い方やインストール方法を追記する
- [ ] ライブラリを追加する際のディレクトリ構成やルールのドキュメント化

## Verification Plan

### Manual Verification

- `todo.md` に追加するライブラリ（アルゴリズム群）のラインナップについて、優先して追加したいものや不要なものがないかご確認いただきます。
- 問題がなければ、この計画通りにファイルを更新します。
