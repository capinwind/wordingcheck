import streamlit as st
import pandas as pd
from pathlib import Path

# Storage location (per-app)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PERSIST_PATH = DATA_DIR / "df_word_rule.pkl"
PERSIST_LETTER = DATA_DIR / "df_rule_letter.pkl"
PERSIST_GREETING = DATA_DIR / "df_rule_greeting.pkl"

st.set_page_config(
        page_title="文章ルール",
)
logo = "images/品川学園シンボル.png"
st.logo(
    logo,
    size='large',
    icon_image=logo,
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

# load persisted auxiliary sheets if present
if "df_rule_letter" not in st.session_state:
    if PERSIST_LETTER.exists():
        try:
            st.session_state["df_rule_letter"] = pd.read_pickle(PERSIST_LETTER)
        except Exception as e:
            st.error(f"Failed to load persisted df_rule_letter: {e}")

if "df_rule_greeting" not in st.session_state:
    if PERSIST_GREETING.exists():
        try:
            st.session_state["df_rule_greeting"] = pd.read_pickle(PERSIST_GREETING)
        except Exception as e:
            st.error(f"Failed to load persisted df_rule_greeting: {e}")

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
                
            try:
                df_rule_letter = pd.read_excel(uploaded, sheet_name="2.書式と運用ルール")
                # save to session so it can be displayed elsewhere and persist to disk
                st.session_state["df_rule_letter"] = df_rule_letter
                try:
                    df_rule_letter.to_pickle(PERSIST_LETTER)
                    st.success("シート '2.書式と運用ルール' を読み込み、永続化しました。")
                except Exception as e:
                    st.error(f"df_rule_letter を永続化できませんでした: {e}")
            except ValueError:
                print("ファイルに「2.書式と運用ルール」というTabが見つかりませんでした。 シート名を確認してください。")
            except Exception as e:
                print("Failed to read Excel:", e)
                
            try:
                df_rule_greeting = pd.read_excel(uploaded, sheet_name="3.時候の挨拶")
                st.session_state["df_rule_greeting"] = df_rule_greeting
                try:
                    df_rule_greeting.to_pickle(PERSIST_GREETING)
                    st.success("シート '3.時候の挨拶' を読み込み、永続化しました。")
                except Exception as e:
                    st.error(f"df_rule_greeting を永続化できませんでした: {e}")
            except ValueError:
                print("ファイルに「3.時候の挨拶」というTabが見つかりませんでした。 シート名を確認してください。")
            except Exception as e:
                print("Failed to read Excel:", e)
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


st.markdown("---")
st.subheader("4. 添付ファイル書式と運用ルール")
# st.write(".   * 適用される文章ルールは別タブに表示しています。")
# st.write(".   * デフォルトは令和７年度版の文章ルールデータを使用しています。")
# st.write(".   * 別タブのテーブルデータを直接編集して、ルールの追加や編集できます")
# st.write(".   * 新しいルールファイルを読み込むことで、ルールデータを差し替えることもできます")

st.markdown("""
               :writing_hand: 配布物の書式など、チェックしてください。</br>
            """, unsafe_allow_html=True)

# If the uploaded Excel contained the "2.書式と運用ルール" sheet, show it here
df_rule_letter = st.session_state.get("df_rule_letter")
if df_rule_letter is not None:
    try:
        st.dataframe(df_rule_letter)
        csv = df_rule_letter.to_csv(index=False).encode("utf-8")
        st.download_button("Download this table (CSV)", data=csv, file_name="df_rule_letter.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Failed to display df_rule_letter: {e}")


st.markdown("---")
st.subheader("5. 時候の挨拶例")
# st.write(".   * 適用される文章ルールは別タブに表示しています。")
# st.write(".   * デフォルトは令和７年度版の文章ルールデータを使用しています。")
# st.write(".   * 別タブのテーブルデータを直接編集して、ルールの追加や編集できます")
# st.write(".   * 新しいルールファイルを読み込むことで、ルールデータを差し替えることもできます")

st.markdown("""
               :writing_hand: 正式文書冒頭の挨拶にご参考ください。</br>
            """, unsafe_allow_html=True)

# If the uploaded Excel contained the "3.時候の挨拶" sheet, show it here
df_rule_greeting = st.session_state.get("df_rule_greeting")
if df_rule_greeting is not None:
    try:
        st.dataframe(df_rule_greeting)
        csv = df_rule_greeting.to_csv(index=False).encode("utf-8")
        st.download_button("Download this table (CSV)", data=csv, file_name="df_rule_greeting.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Failed to display df_rule_greeting: {e}")
