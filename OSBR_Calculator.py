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

        # Normalize column names: lowercase and remove spaces/special characters
        df.columns = df.columns.str.lower().str.replace(r"[\s_/]", "", regex=True)

        # Display the uploaded data
        st.write("Uploaded Data Preview:")
        st.dataframe(df.head())

        # Print normalized column names for debugging
        st.write("Normalized Columns in the uploaded file:")
        st.write(df.columns.tolist())

        # Define required columns (normalized)
        required_columns = [
            "years", "scenario", "draft", "demandtype", "productcode", "plant", "mfgcode",
            "lots", "volumetricgramsmanufactured", "activegrammanufactured", "unitsmanufactured",
            "rawmaterialcost", "siteinventoriableexpenses", "nonsiteinventoriableexpenses",
            "normalscrap", "contractorspend", "cogmjudgement", "carryovercost", "wipcostcogm",
            "cogmcost", "product", "mfgstage", "site", "dpsptype", "prestype", "presentation"
        ]

        # Check if the required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]

        if not missing_columns:
            st.write("✅ All required columns are present.")
        else:
            st.error(f"❌ The following required columns are missing: {', '.join(missing_columns)}")
            st.stop()

        # Dropdown for Year Range
        year_list = sorted(df["years"].unique())
        start_year, end_year = st.select_slider(
            "Select Year Range",
            options=year_list,
            value=(min(year_list), max(year_list))
        )
        st.write(f"Selected Year Range: {start_year} to {end_year}")

        # Dropdown for Scenario
        scenario_list = df["scenario"].unique()
        selected_scenario = st.selectbox("Select Scenario", scenario_list)

        # Dropdown for Product Code
        product_list = df["productcode"].unique()
        selected_product = st.selectbox("Select Product Code", product_list)

        # Dropdown for Plant
        plant_list = df["plant"].unique()
        selected_plant = st.selectbox("Select Plant", plant_list)

        # Dropdown for Mfg Code
        mfg_code_list = df["mfgcode"].unique()
        selected_mfg_code = st.selectbox("Select Mfg Code", mfg_code_list)

        # Dropdown for Product
        product_name_list = df["product"].unique()
        selected_product_name = st.selectbox("Select Product", product_name_list)

        # Dropdown for DP/SP Type
        dpsp_type_list = df["dpsptype"].unique()
        selected_dpsp_type = st.selectbox("Select DP/SP Type", dpsp_type_list)

        # Dropdown for Pres Type
        pres_type_list = df["prestype"].unique()
        selected_pres_type = st.selectbox("Select Pres Type", pres_type_list)

        # Dropdown for Presentation
        presentation_list = df["presentation"].unique()
        selected_presentation = st.selectbox("Select Presentation", presentation_list)

        # Filter data based on selections
        filtered_data = df[
            (df["years"] >= start_year) &
            (df["years"] <= end_year) &
            (df["scenario"] == selected_scenario) &
            (df["productcode"] == selected_product) &
            (df["plant"] == selected_plant) &
            (df["mfgcode"] == selected_mfg_code) &
            (df["product"] == selected_product_name) &
            (df["dpsptype"] == selected_dpsp_type) &
            (df["prestype"] == selected_pres_type) &
            (df["presentation"] == selected_presentation)
        ]

        if not filtered_data.empty:
            st.write("✅ Filtered Data:")
            st.dataframe(filtered_data)

            # Calculation Selector
            calculation_options = ["Average COGM Cost/Lot", "Average RM Cost/Lot"]
            selected_calculation = st.selectbox("Select Calculation", calculation_options)

            if selected_calculation == "Average COGM Cost/Lot":
                # Perform Average COGM Cost/Lot calculation
                average_cogm_cost = filtered_data["cogmcost"].mean() / 1_000_000  # Convert to $M
                total_lots = filtered_data["lots"].sum()
                average_cogm_cost_per_lot = (average_cogm_cost / total_lots) if total_lots != 0 else 0

                # Display results
                st.write("### Calculation Results")
                st.write(f"**Average COGM Cost for Selected Product ({selected_product_name}):** ${average_cogm_cost:,.2f}M")
                st.write(f"**Total Lots for Selected Product ({selected_product_name}):** {total_lots:,}")
                st.write(f"**Average COGM Cost/Lot for Selected Product ({selected_product_name}):** ${average_cogm_cost_per_lot:,.2f}M")

            elif selected_calculation == "Average RM Cost/Lot":
                # Perform Average RM Cost/Lot calculation
                average_rm_cost = filtered_data["rawmaterialcost"].mean() / 1_000_000  # Convert to $M
                total_lots = filtered_data["lots"].sum()
                average_rm_cost_per_lot = (average_rm_cost / total_lots) if total_lots != 0 else 0

                # Display results
                st.write("### Calculation Results")
                st.write(f"**Average Raw Material Cost for Selected Product ({selected_product_name}):** ${average_rm_cost:,.2f}M")
                st.write(f"**Total Lots for Selected Product ({selected_product_name}):** {total_lots:,}")
                st.write(f"**Average RM Cost/Lot for Selected Product ({selected_product_name}):** ${average_rm_cost_per_lot:,.2f}M")
        else:
            st.warning("❌ No data found for the selected filters.")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the file: {e}")
else:
    st.info("ℹ️ Please upload a CSV file to get started.")
