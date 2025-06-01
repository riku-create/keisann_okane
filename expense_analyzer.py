import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib as mpl
import tempfile
import os
import re
import matplotlib.font_manager as fm
import urllib.request

# --- 日本語フォント設定（IPAexGothicとNoto Sans CJK JPを自動DL＆優先適用） ---
def get_japanese_font_paths():
    font_paths = []
    # IPAexGothic
    ipaex_url = "https://github.com/googlefonts/ipafont/raw/main/fonts/ttf/ipaexg.ttf"
    ipaex_path = os.path.join(tempfile.gettempdir(), "ipaexg.ttf")
    if not os.path.exists(ipaex_path):
        try:
            urllib.request.urlretrieve(ipaex_url, ipaex_path)
        except Exception:
            pass
    if os.path.exists(ipaex_path):
        font_paths.append(ipaex_path)
    # Noto Sans CJK JP
    noto_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
    noto_path = os.path.join(tempfile.gettempdir(), "NotoSansCJKjp-Regular.otf")
    if not os.path.exists(noto_path):
        try:
            urllib.request.urlretrieve(noto_url, noto_path)
        except Exception:
            pass
    if os.path.exists(noto_path):
        font_paths.append(noto_path)
    return font_paths

font_paths = get_japanese_font_paths()
font_names = []
for path in font_paths:
    try:
        font_names.append(fm.FontProperties(fname=path).get_name())
    except Exception:
        pass
# フォールバック英語フォントも追加
font_names += ["Arial", "sans-serif"]
plt.rcParams['font.family'] = font_names
mpl.rcParams['axes.unicode_minus'] = False

def get_fontproperties():
    # 最初に見つかった日本語フォントを優先
    for path in font_paths:
        try:
            return fm.FontProperties(fname=path)
        except Exception:
            continue
    return fm.FontProperties()

# --- ページ設定とカスタムCSS ---
st.set_page_config(
    page_title="支出分析・削減提案システム",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
<style>
body, .stApp {
    background-color: #FFFDE7 !important;
}
.main-title {
    font-size: clamp(1.2rem, 6vw, 2.2rem);
    font-weight: bold;
    color: #1E88E5;
    text-align: center;
    padding: 0.5rem 0 0.5rem 0;
    margin-bottom: 1.2rem;
    border-bottom: 2px solid #1E88E5;
    white-space: nowrap;
    overflow: visible;
    text-overflow: unset;
}
.sub-title {
    font-size: 1.2rem;
    color: #424242;
    margin: 0.5rem 0 0.5rem 0;
}
.stButton>button {
    width: 100%;
    background-color: #1E88E5;
    color: white;
}
.stButton>button:hover {
    background-color: #1565C0;
}
.stMarkdown, .stTextInput, .stDataFrame, .stFileUploader, .stAlert {
    background-color: #FFFDE7 !important;
}
</style>
""", unsafe_allow_html=True)

def detect_header_row(df_preview):
    """列名として最適な行を検出する"""
    best_row = 0
    max_score = 0
    
    for i, row in df_preview.iterrows():
        score = 0
        # 空白でないセル数をスコアに加算
        score += row.notnull().sum()
        
        # 文字列型のセル数をスコアに加算
        str_count = sum(isinstance(x, str) for x in row if pd.notnull(x))
        score += str_count * 2
        
        # 日付っぽい文字列があれば加点
        date_keywords = ['日付', 'date', 'DATE', '日', '年月日', '取引日', '日時', 'timestamp', '日付/時間']
        if any(any(kw in str(x).lower() for kw in date_keywords) for x in row if pd.notnull(x)):
            score += 3
            
        # 金額っぽい文字列があれば加点
        amount_keywords = ['金額', '金', 'amount', 'AMOUNT', '円', '¥', '支出', '支払', '合計', 'total', 'price', '価格']
        if any(any(kw in str(x).lower() for kw in amount_keywords) for x in row if pd.notnull(x)):
            score += 3
            
        if score > max_score:
            max_score = score
            best_row = i
            
    return best_row

def find_date_and_amount_columns(df):
    """日付と金額の列を探す（より広い範囲で検索）"""
    date_col = None
    amount_col = None
    
    # 列名の直接検索
    for col in df.columns:
        col_str = str(col).lower()
        if any(k in col_str for k in ['日付', 'date', '日', '年月日', '取引日', '日時', 'timestamp', '日付/時間']):
            date_col = col
        elif any(k in col_str for k in ['金額', '金', 'amount', '円', '¥', '支出', '支払', '合計', 'total', 'price', '価格']):
            amount_col = col
    
    # 列名で見つからない場合、データの内容で検索
    if not (date_col and amount_col):
        for col in df.columns:
            # 最初の100行のデータを確認
            sample_data = df[col].head(100).astype(str)
            
            # 日付っぽいデータを探す
            if not date_col:
                date_patterns = [
                    r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY-MM-DD
                    r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD-MM-YYYY
                    r'\d{4}年\d{1,2}月\d{1,2}日',     # 日本語形式
                ]
                if any(any(re.search(pattern, str(x)) for x in sample_data) for pattern in date_patterns):
                    date_col = col
            
            # 金額っぽいデータを探す
            if not amount_col:
                amount_patterns = [
                    r'[¥￥]?\d+[,\d]*円?',  # 日本円
                    r'\d+[,\d]*\.?\d*',     # 数値
                ]
                if any(any(re.search(pattern, str(x)) for x in sample_data) for pattern in amount_patterns):
                    amount_col = col
    
    return date_col, amount_col

def read_excel_with_auto_header(uploaded_file):
    """Excelファイルを読み込み、最適なヘッダー行を自動検出"""
    # 先頭20行を仮読み込み（検索範囲を拡大）
    df_preview = pd.read_excel(uploaded_file, header=None, nrows=20)
    
    # 最適なヘッダー行を検出
    header_row = detect_header_row(df_preview)
    
    # 検出したヘッダー行を使用して全体を読み込み
    df = pd.read_excel(uploaded_file, header=header_row)
    
    return df

# --- ページ遷移用ヘルパー ---
def get_page():
    query = st.experimental_get_query_params()
    return query.get("page", ["main"])[0]

def set_page(page_name):
    st.experimental_set_query_params(page=page_name)

def main():
    page = get_page()
    if page == "main":
        st.markdown('<h1 class="main-title">支出分析・削減提案システム</h1>', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-title">PDF→Excel変換手順</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 0.7rem; border-radius: 5px; font-size: 1rem;'>
        1. スマホやパソコンで<a href="https://smallpdf.com/jp/pdf-to-excel" target="_blank">Smallpdf</a>や<a href="https://www.adobe.com/jp/acrobat/online/pdf-to-excel.html" target="_blank">Adobe Acrobat</a>などの無料Webサービスを開きます。<br>
        2. 変換したいPDFファイルをアップロードします。<br>
        3. 変換ボタンを押してExcel（.xlsx）ファイルをダウンロードします。<br>
        4. 下の「Excelファイルをアップロード」から変換したExcelファイルを選択してください。
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="margin: 1.2rem 0;">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx", "xls"])
        st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_file:
            try:
                df = read_excel_with_auto_header(uploaded_file)
                st.success(f"データ読み込み完了！{len(df)}件のデータを処理しました。")
                with st.expander("検出された列名", expanded=False):
                    st.write(df.columns.tolist())
                st.markdown('<h2 class="sub-title">支出データの可視化</h2>', unsafe_allow_html=True)
                date_col, amount_col = find_date_and_amount_columns(df)
                if date_col and amount_col:
                    df = df[[date_col, amount_col]].dropna()
                    df.columns = ['日付', '金額']
                    try:
                        df['日付'] = pd.to_datetime(df['日付'], errors='coerce')
                    except:
                        df['日付'] = pd.to_datetime(df['日付'].astype(str).str.replace('年', '-').str.replace('月', '-').str.replace('日', ''), errors='coerce')
                    try:
                        df['金額'] = pd.to_numeric(df['金額'].astype(str).str.replace('¥', '').str.replace('￥', '').str.replace(',', '').str.replace('円', ''), errors='coerce')
                    except:
                        df['金額'] = pd.to_numeric(df['金額'], errors='coerce')
                    df = df.dropna()
                    if len(df) == 0:
                        st.error("有効なデータが見つかりませんでした。データの形式を確認してください。")
                        return
                    # --- グラフを一画面に表示（余白最小化） ---
                    st.markdown('<div style="display: flex; flex-direction: column; gap: 0.5rem;">', unsafe_allow_html=True)
                    # 月次支出の推移
                    try:
                        st.subheader("月次支出の推移")
                        fp = get_fontproperties()
                        fig1, ax1 = plt.subplots(figsize=(6, 2.5))
                        monthly = df.groupby(df['日付'].dt.strftime('%Y-%m'))['金額'].sum()
                        monthly.plot(kind='bar', ax=ax1, color="#1976D2")
                        ax1.set_title('月次支出の推移', fontsize=13, fontproperties=fp)
                        ax1.set_xlabel('', fontproperties=fp)
                        ax1.set_ylabel('金額', fontproperties=fp)
                        plt.xticks(rotation=45, fontsize=9, fontproperties=fp)
                        plt.yticks(fontsize=9, fontproperties=fp)
                        plt.tight_layout()
                        st.pyplot(fig1)
                        plt.close(fig1)
                    except Exception as e:
                        st.error(f"月次支出の推移グラフの描画でエラー: {e}")
                    # 日次支出の分布
                    try:
                        st.subheader("日次支出の分布")
                        fp = get_fontproperties()
                        fig2, ax2 = plt.subplots(figsize=(6, 2.5))
                        sns.histplot(df['金額'], bins=30, ax=ax2, color="#43A047")
                        ax2.set_title('日次支出の分布', fontsize=13, fontproperties=fp)
                        ax2.set_xlabel('金額', fontproperties=fp)
                        ax2.set_ylabel('件数', fontproperties=fp)
                        plt.xticks(fontsize=9, fontproperties=fp)
                        plt.yticks(fontsize=9, fontproperties=fp)
                        plt.tight_layout()
                        st.pyplot(fig2)
                        plt.close(fig2)
                    except Exception as e:
                        st.error(f"日次支出の分布グラフの描画でエラー: {e}")
                    # 曜日別の平均支出
                    try:
                        st.subheader("曜日別の平均支出")
                        fp = get_fontproperties()
                        fig3, ax3 = plt.subplots(figsize=(6, 2.5))
                        df['曜日'] = df['日付'].dt.day_name()
                        weekday = df.groupby('曜日')['金額'].mean().reindex(
                            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
                        weekday.plot(kind='bar', ax=ax3, color="#FBC02D")
                        ax3.set_title('曜日別の平均支出', fontsize=13, fontproperties=fp)
                        ax3.set_xlabel('', fontproperties=fp)
                        ax3.set_ylabel('平均金額', fontproperties=fp)
                        plt.xticks(fontsize=9, fontproperties=fp)
                        plt.yticks(fontsize=9, fontproperties=fp)
                        plt.tight_layout()
                        st.pyplot(fig3)
                        plt.close(fig3)
                    except Exception as e:
                        st.error(f"曜日別の平均支出グラフの描画でエラー: {e}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    # --- 基本統計量 ---
                    st.subheader("支出の基本統計量")
                    st.dataframe(df['金額'].describe().to_frame())
                else:
                    st.error("日付や金額の列が見つかりませんでした。Excelの列名を確認してください。")
                    with st.expander("検出された列名", expanded=False):
                        st.write(df.columns.tolist())
                    st.write("データの最初の5行:", df.head())
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
                st.write("ファイルの形式や内容を確認してください。")
        st.markdown("<div style='text-align:center; margin-top:2rem;'>", unsafe_allow_html=True)
        if st.button("AIと相談", key="consult_btn", help="AIと一緒に支出管理を考える"):
            set_page("consult")
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif page == "consult":
        st.markdown('<h2 class="sub-title">あなたの支出について教えてください</h2>', unsafe_allow_html=True)
        if 'advice_submitted' not in st.session_state:
            st.session_state['advice_submitted'] = False
        with st.form("user_input_form"):
            high_expense_purpose = st.text_input("高額支出は主にどのような用途でしたか？", value=st.session_state.get('high_expense_purpose', ''))
            high_expense_necessity = st.text_input("これらの支出は必要不可欠なものですか？", value=st.session_state.get('high_expense_necessity', ''))
            high_expense_future = st.text_input("今後同様の支出を予定していますか？", value=st.session_state.get('high_expense_future', ''))
            current_concerns = st.text_input("現在、特に気になっている支出項目はありますか？", value=st.session_state.get('current_concerns', ''))
            future_goals = st.text_input("今後、支出を増やしたい（または減らしたい）項目はありますか？", value=st.session_state.get('future_goals', ''))
            saving_goal = st.text_input("具体的な節約目標はありますか？（例：月額で¥10,000削減したいなど）", value=st.session_state.get('saving_goal', ''))
            lifestyle_improvements = st.text_input("現在の支出で、特に改善したい生活習慣はありますか？", value=st.session_state.get('lifestyle_improvements', ''))
            submitted = st.form_submit_button("アドバイスを表示")
            if submitted:
                st.session_state['advice_submitted'] = True
                st.session_state['high_expense_purpose'] = high_expense_purpose
                st.session_state['high_expense_necessity'] = high_expense_necessity
                st.session_state['high_expense_future'] = high_expense_future
                st.session_state['current_concerns'] = current_concerns
                st.session_state['future_goals'] = future_goals
                st.session_state['saving_goal'] = saving_goal
                st.session_state['lifestyle_improvements'] = lifestyle_improvements
        # アドバイス表示
        if st.session_state.get('advice_submitted', False):
            st.header("支出を抑えるためのアドバイス")
            st.markdown("### 回答まとめ")
            table = {
                "高額支出の用途": st.session_state.get('high_expense_purpose', ''),
                "必要性": st.session_state.get('high_expense_necessity', ''),
                "今後の予定": st.session_state.get('high_expense_future', ''),
                "気になる支出": st.session_state.get('current_concerns', ''),
                "将来の目標": st.session_state.get('future_goals', ''),
                "節約目標": st.session_state.get('saving_goal', ''),
                "改善したい習慣": st.session_state.get('lifestyle_improvements', '')
            }
            st.table(pd.DataFrame(table.items(), columns=["項目", "内容"]))
            st.markdown("### アドバイス")
            if st.session_state.get('high_expense_necessity', '') and ('必要' in st.session_state.get('high_expense_necessity', '') or '必須' in st.session_state.get('high_expense_necessity', '')):
                st.write(f"・{st.session_state.get('high_expense_purpose', '')}に関する支出は必要不可欠とのことですが、以下のような代替案を検討してみてはいかがでしょうか：")
                st.write("- まとめ買いによる割引の活用\n- ポイントカードやクレジットカードの特典の活用\n- 季節や時期を考慮した購入タイミングの調整")
            elif st.session_state.get('high_expense_purpose', ''):
                st.write(f"・{st.session_state.get('high_expense_purpose', '')}に関する支出について、以下のような削減案を提案します：")
                st.write("- 支出の優先順位付けの見直し\n- 代替手段の検討\n- 支出の頻度の調整")
            if st.session_state.get('current_concerns', ''):
                st.write(f"【{st.session_state.get('current_concerns', '')}に関するアドバイス】\n- 支出の詳細な記録と分析\n- 予算の設定と管理\n- 定期的な見直しと調整")
            if st.session_state.get('future_goals', ''):
                st.write(f"【{st.session_state.get('future_goals', '')}の実現に向けたアドバイス】\n- 目標達成のための具体的なステップ\n- 進捗管理の方法\n- モチベーション維持のための工夫")
            if st.session_state.get('saving_goal', ''):
                st.write(f"【{st.session_state.get('saving_goal', '')}の達成に向けたアドバイス】\n- 目標金額の達成に向けた具体的なアクションプラン\n- 支出の優先順位付け\n- 節約の進捗管理方法")
            if st.session_state.get('lifestyle_improvements', ''):
                st.write(f"【{st.session_state.get('lifestyle_improvements', '')}の改善に向けたアドバイス】\n- 習慣化のための具体的なステップ\n- 継続的なモチベーション維持の方法\n- 進捗の可視化と振り返り")
            st.write("【総合的なアドバイス】\n1. 支出の記録と分析\n2. 予算管理の徹底\n3. 継続的な改善")

if __name__ == "__main__":
    main() 
