## 展開用コードの実装 (Expander)

- [ ] `atcoder-python-snippets-expander` を参考に、どのような関数が必要か要件を整理する
- [ ] 外部からライブラリとして呼び出せるようなインターフェースを設計する
- [ ] 「ブロック分割型」の展開ロジックを実装する
  - 1. 標準ライブラリのimport群 (import sys, collections など)
  - 2. 展開された自作ライブラリ群 (安全性を担保する配置)
  - 3. ユーザーのメインコード (一番下に配置し、読み飛ばしやすくする)

## テスト自動化 (pytest)

- [ ] pytestが自動で実行される環境（CI/CD または pre-commit 等）を構築する

Warshall-ford
Bellman-Ford
二部マッチング
Dyijkstra
最大フロー問題、最小全域問題
Union Find木
ゲーム　ニム
Grundy数
半分全列挙
木DP
ダブリンぐ
最大公約数
MODの累乗　二進数
ゲーム　必勝法
