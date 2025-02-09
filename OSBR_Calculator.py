import streamlit as st
import pandas as pd

# Title of the app
st.title("COGM Calculator")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your COGM CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

        # Display the uploaded data
        st.write("Uploaded Data Preview:")
        st.dataframe(df.head())

        # Print column names for debugging
        st.write("Columns in the uploaded file:")
        st.write(df.columns.tolist())

        # Check if the required columns exist
        required_columns = [
            "Years", "Scenario", "Draft", "Demand Type", "Product Code", "Plant", "Mfg Code",
            "Lots", "Volumetric Grams Manufactured", "Active Gram Manufactured", "Units Manufactured",
            "Raw Material Cost", "Site inventoriable expenses", "Non Site inventoriable expenses",
            "Normal Scrap", "Contractor Spend", "COGM Judgement", "Carry Over Cost", "Wip Cost COGM",
            "COGM Cost", "_Product", "_Mfg Stage", "_Site", "_DP/SP type", "_Pres Type", "_Presentation"
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if not missing_columns:
            st.write("✅ All required columns are present.")
        else:
            st.error(f"❌ The following required columns are missing: {', '.join(missing_columns)}")
            st.stop()

        # Dropdown for Year Range
        year_list = sorted(df["Years"].unique())
        start_year, end_year = st.select_slider(
            "Select Year Range",
            options=year_list,
            value=(min(year_list), max(year_list))
        )
        st.write(f"Selected Year Range: {start_year} to {end_year}")

        # Dropdown for Scenario
        scenario_list = df["Scenario"].unique()
        selected_scenario = st.selectbox("Select Scenario", scenario_list)
        st.write(f"Selected Scenario: {selected_scenario}")

        # Dropdown for Product Code
        product_list = df["Product Code"].unique()
        selected_product = st.selectbox("Select Product Code", product_list)
        st.write(f"Selected Product Code: {selected_product}")

        # Dropdown for Plant
        plant_list = df["Plant"].unique()
        selected_plant = st.selectbox("Select Plant", plant_list)
        st.write(f"Selected Plant: {selected_plant}")

        # Dropdown for Mfg Code
        mfg_code_list = df["Mfg Code"].unique()
        selected_mfg_code = st.selectbox("Select Mfg Code", mfg_code_list)
        st.write(f"Selected Mfg Code: {selected_mfg_code}")

        # Filter data based on selections
        filtered_data = df[
            (df["Years"] >= start_year) &
            (df["Years"] <= end_year) &
            (df["Scenario"] == selected_scenario) &
            (df["Product Code"] == selected_product) &
            (df["Plant"] == selected_plant) &
            (df["Mfg Code"] == selected_mfg_code)
        ]

        if not filtered_data.empty:
            st.write("✅ Filtered Data:")
            st.dataframe(filtered_data)

            # Perform calculations
            # 1. Average Cost/Lot ($M)
            total_cogm_cost = filtered_data["COGM Cost"].sum()
            total_lots = filtered_data["Lots"].sum()
            average_cost_per_lot = (total_cogm_cost / total_lots) / 1_000_000 if total_lots != 0 else 0  # Convert to $M

            # 2. Average Raw Materials (RM) Cost/Lot ($M)
            total_raw_material_cost = filtered_data["Raw Material Cost"].sum()
            average_rm_cost_per_lot = (total_raw_material_cost / total_lots) / 1_000_000 if total_lots != 0 else 0  # Convert to $M

            # 3. Cost per Sold Unit for a given year
            selected_year = st.selectbox("Select Year for Cost per Sold Unit", year_list)
            yearly_data = filtered_data[filtered_data["Years"] == selected_year]
            total_cogm_cost_year = yearly_data["COGM Cost"].sum()
            total_units_manufactured_year = yearly_data["Units Manufactured"].sum()
            cost_per_sold_unit = total_cogm_cost_year / total_units_manufactured_year if total_units_manufactured_year != 0 else 0

            # Display results
            st.write("### Calculation Results")
            st.write(f"**Average Cost/Lot ($M) for {start_year}-{end_year}:** ${average_cost_per_lot:,.2f}M")
            st.write(f"**Average Raw Materials (RM) Cost/Lot ($M) for {start_year}-{end_year}:** ${average_rm_cost_per_lot:,.2f}M")
            st.write(f"**Cost per Sold Unit for {selected_year}:** ${cost_per_sold_unit:,.2f}")
        else:
            st.warning("❌ No data found for the selected filters.")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the file: {e}")
else:
    st.info("ℹ️ Please upload a CSV file to get started.")
