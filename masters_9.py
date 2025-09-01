import streamlit as st
import pandas as pd
import math   # Needed for your calculations

st.title("📱 Masters 80% Rule Minimums")

# --- Helpers ---
def safe_number_input(label, default=None, integer=False):
    key = label.replace(" ", "_")
    if key not in st.session_state:
        st.session_state[key] = str(default) if default is not None else ""
    user_input = st.text_input(label, value=st.session_state[key], key=key)
    try:
        value = float(user_input)
        if integer and not value.is_integer():
            return None
        return int(value) if integer else value
    except ValueError:
        return None

def maybe_clear_inputs():
    if st.session_state.get("clear_trigger"):
        for key in ["Declared_Snatch", "Declared_CJ", "Declared_Entry_Total", "Snatch_Taken", "Start_No."]:
            st.session_state[key] = ""
        st.session_state.clear_trigger = False
        st.session_state["row_loaded"] = False

maybe_clear_inputs()

# --- Initialize session state ---
if "data_table" not in st.session_state:
    st.session_state.data_table = pd.DataFrame(columns=[
        "Start No.", "Snatch", "CJ", "ET",
        "Snatch +/-", "Min Snatch", "Snatch Taken",
        "CJ +/-", "Min CJ"
    ])
if "page" not in st.session_state:
    st.session_state.page = "Calculator"
if "selected_start" not in st.session_state:
    st.session_state.selected_start = None
if "row_loaded" not in st.session_state:
    st.session_state.row_loaded = False

# --- Handle navigation trigger before sidebar renders ---
if "nav_trigger" in st.session_state and st.session_state.nav_trigger:
    st.session_state["page"] = "Calculator"
    st.session_state.nav_trigger = False


# --- Sidebar navigation ---
st.sidebar.radio(
    "Choose a page", ["Calculator", "Table"],
    key="page"
)

# --- Page logic ---
page = st.session_state.page

if page == "Calculator":
    st.header("🔢 Input Values")

    # Prefill if a row was selected, only once
    if st.session_state.selected_start and not st.session_state.row_loaded:
        df = st.session_state.data_table
        selected_row_data = df[df["Start No."] == st.session_state.selected_start]
        if not selected_row_data.empty:
            selected_row_data = selected_row_data.iloc[0]
            st.session_state["Start_No."] = selected_row_data["Start No."]
            st.session_state["Declared_Snatch"] = str(selected_row_data["Snatch"])
            st.session_state["Declared_CJ"] = str(selected_row_data["CJ"])
            st.session_state["Declared_Entry_Total"] = str(selected_row_data["ET"])
            st.session_state["Snatch_Taken"] = str(selected_row_data["Snatch Taken"]) if pd.notna(selected_row_data["Snatch Taken"]) else ""
            st.session_state.row_loaded = True

    # --- Start No / Name ---
    start_number = st.text_input(
        "Start No. / Name",
        value=st.session_state.get("Start_No.", ""),
        key="Start_No."
    )

    # --- Declared Entry Values ---
    st.subheader("Declared Entry Values")
    col1, col2, col3 = st.columns(3)
    with col1:
        a = safe_number_input("Declared Snatch", integer=True)
    with col2:
        b = safe_number_input("Declared CJ", integer=True)
    with col3:
        c = safe_number_input("Declared Entry Total", integer=True)

    if any(v is None for v in [a, b, c]):
        st.warning("Enter Declared Snatch, CJ, and Entry Total.")

    # --- Snatch Metrics ---
    if all(v is not None for v in [a, b, c]):
        sum_abc = (a + b) - (math.ceil(c * 0.8))
        prod_abc = a - sum_abc

        st.subheader("Snatch Evaluation")
        col4, col5 = st.columns(2)
        col4.metric("Snatch Plus/Minus", sum_abc)
        col5.metric("Minimum Snatch", prod_abc)

        st.markdown("---")

        # --- CJ Evaluation + Snatch Taken ---
        st.subheader("CJ Evaluation")
        col6, col7, col8 = st.columns(3)
        with col6:
            if "Snatch_Taken" not in st.session_state:
                st.session_state["Snatch_Taken"] = ""

            d_input = st.text_input("Snatch Taken", key="Snatch_Taken")
            try:
                d = int(d_input)
            except ValueError:
                d = None
                if d_input != "":
                    st.warning("Enter First Snatch Taken ")

        if d is not None:
            sum_plus_d = (b + d) - (math.ceil(c * 0.8))
            prod_div_d = b - sum_plus_d
            col7.metric("CJ Plus/Minus", sum_plus_d)
            col8.metric("Minimum CJ", prod_div_d)
        else:
            sum_plus_d = None
            prod_div_d = None

        st.markdown("---")

        # --- Save Entry Button ---
        if st.button("Save Entry"):
            new_row = {
                "Start No.": start_number,
                "Snatch": a,
                "CJ": b,
                "ET": c,
                "Snatch +/-": sum_abc,
                "Min Snatch": prod_abc,
                "Snatch Taken": d,
                "CJ +/-": sum_plus_d,
                "Min CJ": prod_div_d
            }

            df = st.session_state.data_table
            if start_number in df["Start No."].values:
                row_index = df[df["Start No."] == start_number].index
                for col in df.columns:
                    st.session_state.data_table.at[row_index[0], col] = new_row[col]
                st.success("Entry updated!")
            else:
                st.session_state.data_table = pd.concat(
                    [df, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                st.success("Entry saved!")

            st.session_state.clear_trigger = True
            st.session_state.selected_start = None
            st.session_state.row_loaded = False
            st.rerun()

elif page == "Table":
    st.header("📋 Results Table")

    df = st.session_state.data_table
    if not df.empty:
        st.dataframe(df)
        selected_row = st.selectbox(
            "Select a Start Number to input Snatch Taken",
            df["Start No."].unique()
        )
        if st.button("Go to Calculator to update"):
            st.session_state.selected_start = selected_row
            st.session_state.nav_trigger = True 
            st.rerun()
    else:
        st.warning("No entries yet. Go to Calculator to add data.")