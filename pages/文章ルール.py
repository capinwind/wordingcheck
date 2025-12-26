import streamlit as st
import pandas as pd
from pathlib import Path

# Storage location (per-app)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PERSIST_PATH = DATA_DIR / "df_word_rule.pkl"

st.set_page_config(
        page_title="文章ルール",
)


st.title("文章確認ルール管理")
st.markdown("""
            :green_heart: 令和７年度のルール(48点ほど)をあらかじめ導入しています。</br>
            :green_heart: ベースファイル：PTA文書の書式ルール_令和7年度.xlsx</br>
            :green_heart: ファイル読み込む前に、まず最後の表を確認してみてください。</br>
            :green_heart: 変更が必要の場合のみ、編集又はファイルのインポートを行ってください。</br>
        """, unsafe_allow_html=True)

def load_persisted():
    if PERSIST_PATH.exists():
        try:
            return pd.read_pickle(PERSIST_PATH)
        except Exception as e:
            st.error(f"Failed to load persisted DB: {e}")
            return None
    return None

if "df_word_rule" not in st.session_state:
    st.session_state["df_word_rule"] = load_persisted()

# st.subheader("現在のルールDB (df_word_rule)")
# if st.session_state.get("df_word_rule") is None:
#     st.info("No rule DB loaded yet.")
# else:
#     df = st.session_state["df_word_rule"]
#     st.write(f"Loaded: {len(df)} rows, {len(df.columns)} columns")
#     st.dataframe(df.head())

st.markdown("---")
st.subheader("1.文章ルールの読込み(Excel形式)")

uploaded = st.file_uploader("またはファイルをアップロード", type=["xlsx", "xls"], label_visibility="collapsed")


st.markdown("---")
st.subheader("2. 文章ルールの保存・操作")
col1, col3, col4 = st.columns(3)
with col1:
    if st.button("(1)ファイル読込み", icon="💿", width=200):
        if uploaded is None:
            st.warning("アップロードされたファイルがありません")
        else:
            try:
                df = pd.read_excel(uploaded)
                st.session_state["df_word_rule"] = df
                df.to_pickle(PERSIST_PATH)
                st.success("ファイル読込みました")
            except Exception:
                st.error("cannot read the file, please check you link or the file behind your link")
with col3:
    if st.button("(2)システム保存", icon="💾", width=200):
        df = st.session_state.get("df_word_rule")
        if df is None:
            st.warning("保存する df_word_rule がありません")
        else:
            try:
                df.to_pickle(PERSIST_PATH)
                st.success("保存しました")
            except Exception as e:
                st.error(f"保存に失敗しました: {e}")

with col4:
    if st.button("(3)データ削除", icon="🗑️", width=200):
        try:
            if PERSIST_PATH.exists():
                PERSIST_PATH.unlink()
            st.session_state["df_word_rule"] = None
            st.success("データを削除しました")
        except Exception as e:
            st.error(f"削除に失敗しました: {e}")

st.markdown("---")
st.subheader("3. 文章ルールの確認・編集・ダウンロード")
with st.expander("文章ルールの説明と注意点", expanded=False):
    st.markdown("""
                :green_heart: 現状の文章ルール表。スクロールして確認可能。</br>
                :green_heart: 直接セルを編集できます。</br>
                :green_heart: 編集後必ず最後の【編集内容保存】をボタンを押してください。</br>
            """, unsafe_allow_html=True)
df = st.session_state.get("df_word_rule")


if df is None:
    st.info("No data to show or download")
else:
 # col_apply, col_revert = st.columns([1, 1])
    col_apply, col_revert, col_download = st.columns([1, 1, 1])
    with col_apply:
        if st.button("編集内容保存",icon="💾", width=200):
            df_to_save = st.session_state.get("df_word_rule")
            if df_to_save is None:
                st.warning("保存するデータがありません")
            else:
                try:
                    df_to_save.to_pickle(PERSIST_PATH)
                    st.success("変更をディスクに保存しました")
                except Exception as e:
                    st.error(f"保存に失敗しました: {e}")
    with col_revert:
        if st.button("編集内容破棄",icon="🗑️", width=200):
            persisted = load_persisted()
            st.session_state["df_word_rule"] = persisted
            # Try to trigger a rerun; if the Streamlit runtime doesn't expose experimental_rerun,
            # fall back to instructing the user to refresh the page.
            try:
                if hasattr(st, "experimental_rerun"):
                    st.experimental_rerun()
                else:
                    raise AttributeError("experimental_rerun not available")
            except Exception:
                st.success("編集内容を破棄しました。ページを再読み込みしてください。")
                # Stop execution so the user can refresh safely
                st.stop()
            
    
    # Use Streamlit's data editor (fall back to experimental name if needed)
    try:
        edited = st.data_editor(df, num_rows="dynamic")
    except Exception:
        edited = st.experimental_data_editor(df, num_rows="dynamic")

    # If edited differs, update session state (but don't persist until user saves)
    try:
        changed = not edited.equals(df)
    except Exception:
        # If equals fails due to dtype differences, assume changed
        changed = True

    if changed:
        st.session_state["df_word_rule"] = edited
        st.info("編集をセッションに反映しました。保存するには保存ボタンを押してください。")

    csv = st.session_state.get("df_word_rule").to_csv(index=False).encode("utf-8")
    # st.download_button("ダウンロード(CSV)", data=csv, file_name="df_word_rule.csv", mime="text/csv")
    with col_download:
            st.download_button("ダウンロード(CSV)", data=csv, file_name="df_word_rule.csv", mime="text/csv", icon="📥", width=200)
    