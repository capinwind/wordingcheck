import streamlit as st
import pandas as pd
from pathlib import Path

# Storage location (per-app)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PERSIST_PATH = DATA_DIR / "df_word_rule.pkl"

st.title("Wording Rules — 管理")

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

st.subheader("現在のルールDB (df_word_rule)")
if st.session_state.get("df_word_rule") is None:
    st.info("No rule DB loaded yet.")
else:
    df = st.session_state["df_word_rule"]
    st.write(f"Loaded: {len(df)} rows, {len(df.columns)} columns")
    st.dataframe(df.head())

st.markdown("---")
st.subheader("Excelから読み込んで永続化する")
col1, col2 = st.columns([3, 1])

with col1:
    path_input = st.text_input("ローカルExcelパスを入力 (例: ./data/rules.xlsx)", key="rule_path")
    uploaded = st.file_uploader("またはファイルをアップロード", type=["xlsx", "xls"])

with col2:
    if st.button("Load from path"):
        rp = (path_input or "").strip()
        if not rp:
            st.warning("パスを入力するかファイルをアップロードしてください")
        else:
            try:
                df = pd.read_excel(rp)
                st.session_state["df_word_rule"] = df
                df.to_pickle(PERSIST_PATH)
                st.success("Excel を読み込み、永続化しました")
            except Exception:
                st.error("cannot read the file, please check you link or the file behind your link")

    if st.button("Load from upload"):
        if uploaded is None:
            st.warning("アップロードされたファイルがありません")
        else:
            try:
                df = pd.read_excel(uploaded)
                st.session_state["df_word_rule"] = df
                df.to_pickle(PERSIST_PATH)
                st.success("アップロードを読み込み、永続化しました")
            except Exception:
                st.error("cannot read the file, please check you link or the file behind your link")

st.markdown("---")
st.subheader("永続化操作")
col3, col4 = st.columns(2)
with col3:
    if st.button("Save current df_word_rule to disk"):
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
    if st.button("Delete persisted DB"):
        try:
            if PERSIST_PATH.exists():
                PERSIST_PATH.unlink()
            st.session_state["df_word_rule"] = None
            st.success("永続データを削除しました")
        except Exception as e:
            st.error(f"削除に失敗しました: {e}")

st.markdown("---")
st.subheader("ダウンロード / 表示")
df = st.session_state.get("df_word_rule")
if df is None:
    st.info("No data to show or download")
else:
    st.write("編集可能なルールテーブル（編集後は適用してください）")
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
        st.info("編集をセッションに反映しました。保存するには下のボタンを押してください。")

    csv = st.session_state.get("df_word_rule").to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="df_word_rule.csv", mime="text/csv")

    col_apply, col_revert = st.columns([1, 1])
    with col_apply:
        if st.button("Apply changes / Save"):
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
        if st.button("Revert to persisted"):
            persisted = load_persisted()
            st.session_state["df_word_rule"] = persisted
            st.experimental_rerun()
