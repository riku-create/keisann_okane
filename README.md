# 支出分析・削減提案システム

このシステムは、支出明細データ（Excel形式）をアップロードし、分析・可視化・削減提案を行うWebアプリケーションです。  
GitHubとStreamlit Cloudで公開でき、PCやスマホのブラウザから利用できます。

## 主な機能

- 支出データ（Excelファイル）のアップロード・自動解析
- 支出データの可視化（グラフ・統計）
- 対話形式での削減提案生成
- Googleスプレッドシートへの出力（任意）

---

## セットアップ手順（ローカル実行の場合）

1. **必要なソフトウェアのインストール**
   - Python 3.10 または 3.11（3.13は非対応）
   - Git

2. **リポジトリのクローン**
   ```bash
   git clone [リポジトリURL]
   cd [リポジトリ名]
   ```

3. **仮想環境の作成と有効化**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

4. **依存パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   ```

5. **Google連携機能を使う場合のみ**
   - Google Cloud Consoleでプロジェクト作成
   - Google Drive APIとGoogle Sheets APIを有効化
   - サービスアカウントを作成し、JSONキーをダウンロード
   - ダウンロードしたJSONキーを`credentials.json`としてプロジェクトのルートディレクトリに配置

6. **アプリケーションの起動**
   ```bash
   streamlit run expense_analyzer.py
   ```

---

## Streamlit Cloudでの公開・利用方法

1. **GitHubにリポジトリを作成し、必要ファイルをpush**
   - `expense_analyzer.py`
   - `requirements.txt`
   - `runtime.txt`（内容は `python-3.10` または `python-3.11`、必ずルートに配置）

2. **Streamlit Cloudで新規アプリ作成**
   - GitHubリポジトリを指定
   - デプロイ後、Web上でアプリが利用可能

3. **利用者はExcelファイルをアップロードして分析開始**
   - PDF→Excel変換は各自ローカルで行い、Excelファイルをアップロードしてください

---

## 使用方法

1. ブラウザでアプリにアクセス（例: `https://[your-app].streamlit.app`）
2. Excelファイル（支出明細）をアップロード
3. 表示される質問に回答
4. 生成された提案を確認
5. 必要に応じてGoogleスプレッドシートに出力（Google連携設定済みの場合）

---

## 注意事項

- **PDFファイルは直接アップロードできません。**  
  必要に応じて、PDF→Excel変換（例: Adobe Acrobat, Smallpdf, Tabulaなど）を各自で行ってください。
- **Pythonバージョンは3.10または3.11を推奨**（3.13は非対応、`runtime.txt`で指定）
- **Googleスプレッドシート機能は任意**  
  利用する場合は`credentials.json`の配置とAPI有効化が必要です。
- **大量データの場合はPCのメモリに注意**

---

## トラブルシューティング

- **アプリが起動しない／エラーが出る場合**
  - Pythonバージョン、`requirements.txt`、`runtime.txt`の内容・配置を確認
  - Streamlit CloudでPython 3.13が選ばれてしまう場合は、`runtime.txt`のスペル・場所・内容を再確認し、再デプロイ

- **Excelファイルの読み込みに失敗する場合**
  - ファイル形式（.xlsx）やデータ内容を確認

- **Googleスプレッドシートへの出力に失敗する場合**
  - `credentials.json`の配置、API有効化、シートの共有設定を確認

---

## ライセンス

MIT License 
