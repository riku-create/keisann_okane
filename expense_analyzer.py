import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib as mpl
import tempfile
import os

# 日本語フォントの設定
plt.rcParams['font.family'] = 'DejaVu Sans'
mpl.rcParams['axes.unicode_minus'] = False

# ページ設定
st.set_page_config(
    page_title="支出分析・削減提案システム",
    page_icon="💰",
    layout="wide"
)

def main():
    st.title("支出分析・削減提案システム")

    st.header("PDF→Excel変換手順")
    st.markdown("""
1. スマホやパソコンで[Smallpdf](https://smallpdf.com/jp/pdf-to-excel)や[Adobe Acrobat](https://www.adobe.com/jp/acrobat/online/pdf-to-excel.html)などの無料Webサービスを開きます。
2. 変換したいPDFファイルをアップロードします。
3. 変換ボタンを押してExcel（.xlsx）ファイルをダウンロードします。
4. 下の「Excelファイルをアップロード」から変換したExcelファイルを選択してください。
    """)
    
    uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx", "xls"]) 
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success(f"データ読み込み完了！{len(df)}件のデータを処理しました。")
        st.header("支出データの可視化")
        # 日付・金額の列名推定
        date_col = None
        amount_col = None
        for col in df.columns:
            col_str = str(col)
            if any(k in col_str for k in ['日付', 'date', 'DATE']):
                    date_col = col
                elif any(k in col_str for k in ['金額', '金', 'amount', 'AMOUNT']):
                    amount_col = col
            if date_col and amount_col:
            df = df[[date_col, amount_col]].dropna()
            df.columns = ['日付', '金額']
            df['日付'] = pd.to_datetime(df['日付'], errors='coerce')
            df['金額'] = pd.to_numeric(df['金額'], errors='coerce')
            df = df.dropna()
            # 月次支出の推移
            st.subheader("月次支出の推移")
            monthly = df.groupby(df['日付'].dt.strftime('%Y-%m'))['金額'].sum()
            fig, ax = plt.subplots(figsize=(10, 6))
            monthly.plot(kind='bar', ax=ax)
            plt.title('月次支出の推移')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            # 日次支出の分布
            st.subheader("日次支出の分布")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(df['金額'], bins=30, ax=ax)
            plt.title('日次支出の分布')
            st.pyplot(fig)
            # 曜日別の平均支出
        st.subheader("曜日別の平均支出")
            df['曜日'] = df['日付'].dt.day_name()
            weekday = df.groupby('曜日')['金額'].mean().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
            fig, ax = plt.subplots(figsize=(10, 6))
        weekday.plot(kind='bar', ax=ax)
        plt.title('曜日別の平均支出')
        st.pyplot(fig)
            # 基本統計量
        st.subheader("支出の基本統計量")
            st.dataframe(df['金額'].describe().to_frame())
            # 対話形式の質問
        st.header("あなたの支出管理について教えてください")
        with st.form("user_input_form"):
                high_expense_days = df.groupby('日付')['金額'].sum()
            high_expense_days = high_expense_days[high_expense_days > high_expense_days.mean() + high_expense_days.std()]
            if not high_expense_days.empty:
                st.write("高額支出日:", ', '.join(high_expense_days.index.strftime('%Y-%m-%d')))
                st.write(f"これらの日の平均支出額: ¥{high_expense_days.mean():,.0f}")
                high_expense_purpose = st.text_input("これらの高額支出は主にどのような用途でしたか？")
                high_expense_necessity = st.text_input("これらの支出は必要不可欠なものですか？")
                high_expense_future = st.text_input("今後同様の支出を予定していますか？")
            else:
                high_expense_purpose = high_expense_necessity = high_expense_future = ""
            current_concerns = st.text_input("現在、特に気になっている支出項目はありますか？")
            future_goals = st.text_input("今後、支出を増やしたい（または減らしたい）項目はありますか？")
            saving_goal = st.text_input("具体的な節約目標はありますか？（例：月額で¥10,000削減したいなど）")
            lifestyle_improvements = st.text_input("現在の支出で、特に改善したい生活習慣はありますか？")
            submitted = st.form_submit_button("提案を表示")
        if submitted:
            st.header("あなたへの具体的な提案")
            st.markdown("### 回答まとめ")
            table = {
                "高額支出の用途": high_expense_purpose,
                "必要性": high_expense_necessity,
                "今後の予定": high_expense_future,
                "気になる支出": current_concerns,
                "将来の目標": future_goals,
                "節約目標": saving_goal,
                "改善したい習慣": lifestyle_improvements
            }
            st.table(pd.DataFrame(table.items(), columns=["項目", "内容"]))
            st.markdown("### 提案")
            if high_expense_necessity and ('必要' in high_expense_necessity or '必須' in high_expense_necessity):
                st.write(f"・{high_expense_purpose}に関する支出は必要不可欠とのことですが、以下のような代替案を検討してみてはいかがでしょうか：")
                st.write("- まとめ買いによる割引の活用\n- ポイントカードやクレジットカードの特典の活用\n- 季節や時期を考慮した購入タイミングの調整")
            elif high_expense_purpose:
                st.write(f"・{high_expense_purpose}に関する支出について、以下のような削減案を提案します：")
                st.write("- 支出の優先順位付けの見直し\n- 代替手段の検討\n- 支出の頻度の調整")
            if current_concerns:
                st.write(f"【{current_concerns}に関する提案】\n- 支出の詳細な記録と分析\n- 予算の設定と管理\n- 定期的な見直しと調整")
            if future_goals:
                st.write(f"【{future_goals}の実現に向けた提案】\n- 目標達成のための具体的なステップ\n- 進捗管理の方法\n- モチベーション維持のための工夫")
            if saving_goal:
                st.write(f"【{saving_goal}の達成に向けた提案】\n- 目標金額の達成に向けた具体的なアクションプラン\n- 支出の優先順位付け\n- 節約の進捗管理方法")
            if lifestyle_improvements:
                st.write(f"【{lifestyle_improvements}の改善に向けた提案】\n- 習慣化のための具体的なステップ\n- 継続的なモチベーション維持の方法\n- 進捗の可視化と振り返り")
            st.write("【総合的な提案】\n1. 支出の記録と分析\n2. 予算管理の徹底\n3. 継続的な改善")
                else:
            st.error("日付や金額の列が見つかりませんでした。Excelの列名を確認してください。")

if __name__ == "__main__":
    main() 