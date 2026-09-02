import streamlit as st
import pandas as pd

st.set_page_config(page_title="HOSO Production & MC Database", layout="wide")

st.title("🦐 HOSO Master Carton & Production Database Tracker")
st.markdown("Enter your **Input Ice Qty (pieces)** below. Track species, view visual charts, monitor target variance, and export reports instantly.")

# Sidebar settings
st.sidebar.header("Settings / নির্ধারিত মান / মান")

# Species & Grade Selection
species = st.sidebar.selectbox("Select Species / প্রজাতি", ["Black Tiger", "Sea Tiger"])
grade = st.sidebar.selectbox("Select Grade / গ্রেড", ["Grade A", "Standard", "Export Quality"])

ice_weight = st.sidebar.number_input("Ice weight per piece (g) / প্রতি ice-এর ওজন", value=450.0, step=10.0)
target_mc_weight = st.sidebar.number_input("Master carton target (kg) / প্রতি MC-এর লক্ষ্য", value=9.0, step=0.5)
pieces_per_mc = st.sidebar.number_input("Ice per master carton (pcs) / প্রতি MC-তে ice", value=20.0, step=1.0)

daily_target_kg = st.sidebar.number_input("Daily Target Weight (kg) / দৈনিক লক্ষ্য (কেজি)", value=5000.0, step=100.0)

# Default data matching your layout
data = [
    {"Count": "4/6", "Input Ice Qty": 43},
    {"Count": "6/8", "Input Ice Qty": 1604},
    {"Count": "8/10", "Input Ice Qty": 3437},
    {"Count": "8/12", "Input Ice Qty": 12765},
    {"Count": "13/15", "Input Ice Qty": 6018},
    {"Count": "16/20", "Input Ice Qty": 7164},
    {"Count": "21/25", "Input Ice Qty": 1862},
    {"Count": "26/30", "Input Ice Qty": 1960},
    {"Count": "31/40", "Input Ice Qty": 160},
]

df = pd.DataFrame(data)

st.subheader(f"Production Log for: {species} ({grade})")

# Interactive table editor
edited_df = st.data_editor(df, num_rows="fixed", use_container_width=True)

# Calculations
edited_df["Species"] = species
edited_df["Grade"] = grade
edited_df["Ice Weight (g)"] = ice_weight
edited_df["MC Target (kg)"] = target_mc_weight
edited_df["Ice / MC (pcs)"] = pieces_per_mc

edited_df["Total Received Weight (kg)"] = (edited_df["Input Ice Qty"] * edited_df["Ice Weight (g)"]) / 1000.0
edited_df["Complete MC (পূর্ণ MC)"] = edited_df["Input Ice Qty"] // edited_df["Ice / MC (pcs)"]
edited_df["Remaining Ice (বাকি)"] = edited_df["Input Ice Qty"] % edited_df["Ice / MC (pcs)"]
edited_df["Remaining Weight (kg)"] = (edited_df["Remaining Ice (বাকি)"] * edited_df["Ice Weight (g)"]) / 1000.0

total_ice_calc = edited_df["Input Ice Qty"].sum()
if total_ice_calc > 0:
    edited_df["Share (%)"] = (edited_df["Input Ice Qty"] / total_ice_calc) * 100
else:
    edited_df["Share (%)"] = 0.0

edited_df["Status / অবস্থা"] = edited_df["Remaining Ice (বাকি)"].apply(lambda x: "Complete MC / সম্পূর্ণ" if x == 0 else "Partial MC / অসম্পূর্ণ")

# Reorder columns
display_cols = [
    "Count", "Species", "Grade", "Ice Weight (g)", "MC Target (kg)", "Ice / MC (pcs)",
    "Input Ice Qty", "Share (%)", "Total Received Weight (kg)", "Complete MC (পূর্ণ MC)",
    "Remaining Ice (বাকি)", "Remaining Weight (kg)", "Status / অবস্থা"
]
final_view_df = edited_df[display_cols]

st.dataframe(final_view_df.style.format({"Share (%)": "{:.2f}%"}), use_container_width=True)

# Summary calculations
total_ice = final_view_df["Input Ice Qty"].sum()
total_complete_mc = final_view_df["Complete MC (পূর্ণ MC)"].sum()
partial_mc_eq = (final_view_df["Remaining Ice (বাকি)"].sum()) / pieces_per_mc
total_mc_eq = total_complete_mc + partial_mc_eq
total_received_weight = final_view_df["Total Received Weight (kg)"].sum()
total_remaining_ice = final_view_df["Remaining Ice (বাকি)"].sum()
total_remaining_weight = final_view_df["Remaining Weight (kg)"].sum()

# Target Variance Calculations
weight_variance = total_received_weight - daily_target_kg

st.markdown("---")
st.subheader("OVERALL SUMMARY & TARGET VARIANCE / সর্বমোট হিসাব ও লক্ষ্যমাত্রা")

col1, col2, col3 = st.columns(3)
col1.metric("Total Ice Received / মোট ice", f"{total_ice:,.2f} pcs")
col2.metric("Total Complete MC / মোট পূর্ণ MC", f"{total_complete_mc:,.2f}")
col3.metric("Total MC Equivalent / মোট MC সমতুল্য", f"{total_mc_eq:,.2f}")

col4, col5, col6 = st.columns(3)
col4.metric("Total Weight / মোট weight", f"{total_received_weight:,.2f} kg")
col5.metric("Daily Target / দৈনিক লক্ষ্য", f"{daily_target_kg:,.2f} kg")
col6.metric("Variance / লক্ষ্য থেকে পার্থক্য", f"{weight_variance:,.2f} kg", delta=f"{weight_variance:,.2f} kg")

# Added remaining breakdown metrics row
col7, col8 = st.columns(2)
col7.metric("Total Remaining Ice / মোট বাকি ice", f"{total_remaining_ice:,.2f} pcs")
col8.metric("Total Remaining Weight / মোট বাকি weight", f"{total_remaining_weight:,.2f} kg")

# Visual Charts Section
st.markdown("---")
st.subheader("📊 Visual Analytics / ভিজ্যুয়াল অ্যানালিটিক্স")

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.markdown("**Weight Distribution by Count (kg)**")
    chart_data = final_view_df.set_index("Count")["Total Received Weight (kg)"]
    st.bar_chart(chart_data)

with chart_col2:
    st.markdown("**Share Percentage by Count (%)**")
    share_data = final_view_df.set_index("Count")["Share (%)"]
    st.bar_chart(share_data)

# Export Button Section
st.markdown("---")
st.subheader("📥 Export Report / রিপোর্ট ডাউনলোড করুন")

csv = final_view_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Report as CSV / CSV ডাউনলোড করুন",
    data=csv,
    file_name=f"HOSO_Production_Report_{species}_{grade}.csv",
    mime="text/css" if False else "text/csv",
)
