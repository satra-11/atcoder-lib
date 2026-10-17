# atcoder Library

## 目的

atcoderで使うライブラリをまとめ、テンプレートごとに展開できるようにする。

```bash
chmod +x .githooks/pre-push
git config core.hooksPath .githooks
```

## サンプルデータ自動テストコマンド (`actest`)

AtCoderのWebサイトから入力例・出力例をコピーして貼り付けるだけで、ローカル実行・自動判定（AC / WA / RE）を行います。

### 使い方

1. **テストの実行**

   ```bash
   actest a       # workspace/a.py を workspace/samples/a/ でテスト
   actest         # 引数省略時は直近更新されたスクリプトを自動テスト
   ```

2. **サンプルファイルの形式 (`workspace/samples/{問題名}/`)**
   入力と出力を別々のファイルにして保存できます：

   ```
   workspace/samples/a/
   ├── 1_in.txt    # 入力1（AtCoderの入力欄の[Copy]をそのまま貼り付け）
   ├── 1_out.txt   # 出力1（AtCoderの出力欄の[Copy]をそのまま貼り付け）
   ├── 2_in.txt
   ├── 2_out.txt
   ├── 3_in.txt
   └── 3_out.txt
   ```

   - **見出し不要**: 純粋な入力データ・期待出力データだけを貼るだけで動作します。
   - **柔軟なファイル名**: `1_in.txt` / `1_out.txt` のほか、`in1.txt` / `out1.txt` や `1.in` / `1.out` にも対応しています。
   - **同一ファイル形式**: これまで通り `1.txt`, `2.txt` にまとめて貼る形式や、`a.txt` に全サンプルをまとめて書く形式も引き続きサポートしています。

3. **主なオプション**
   - `--case <番号>`: 特定のケースのみ実行（例: `actest a --case 1`）
   - `-c`, `--clip`: ファイル保存せずクリップボードの内容から即座にテスト

## サンプルファイル自動生成コマンド (`cio`)

指定した問題の入力・出力ペアファイルを一括作成します。

```bash
# 問題aのサンプルペアを3組（1_in.txt, 1_out.txt ... 3_out.txt）作成
cio a 3

# ケース数を省略した場合はデフォルトで3組作成
cio b

# 既存ファイルを空ファイルで上書きしたい場合
cio a 3 --force
```

実行後、生成された各ファイルに AtCoder の入力・出力を貼り付ければ、すぐに `actest <問題名>` を実行できます。
