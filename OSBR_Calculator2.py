import streamlit as st
import pandas as pd

# Title of the app
st.title("COGM Calculator")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your COGM Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file, engine="openpyxl")

        # Display the uploaded data
        st.write("Uploaded Data Preview:")
        st.dataframe(df.head())

        # Check if the required columns exist
        required_columns = [
            "Years", "Scenario", "Draft", "Demand Type", "Product Code", "Plant", "Mfg Code",
            "Lots", "Volumetric Grams Manufactured", "Active Gram Manufactured", "Units Manufactured",
            "Raw Material Cost", "Site inventoriable expenses", "Non Site inventoriable expenses",
            "Normal Scrap", "Contractor Spend", "COGM Judgement", "Carry Over Cost", "Wip Cost COGM",
            "COGM Cost", "_Product", "_Mfg Stage", "_Site", "_DP/SP type", "_Pres Type", "_Presentation"
        ]
        if all(col in df.columns for col in required_columns):
            # Dropdown for Year Range
            year_list = sorted(df["Years"].unique())
            start_year, end_year = st.select_slider(
                "Select Year Range",
                options=year_list,
                value=(min(year_list), max(year_list))
            )

            # Dropdown for Scenario
            scenario_list = df["Scenario"].unique()
            selected_scenario = st.selectbox("Select Scenario", scenario_list)

            # Dropdown for Product Code
            product_list = df["Product Code"].unique()
            selected_product = st.selectbox("Select Product Code", product_list)

            # Dropdown for Plant
            plant_list = df["Plant"].unique()
            selected_plant = st.selectbox("Select Plant", plant_list)

            # Dropdown for Mfg Code
            mfg_code_list = df["Mfg Code"].unique()
            selected_mfg_code = st.selectbox("Select Mfg Code", mfg_code_list)

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
                # Display filtered data
                st.write("Filtered Data:")
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
                st.warning("No data found for the selected filters.")
        else:
            st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Please upload an Excel file to get started.")