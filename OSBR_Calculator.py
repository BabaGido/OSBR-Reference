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

        # Clean numeric columns
        numeric_columns = [
            "cogmcost", "rawmaterialcost", "lots", "volumetricgramsmanufactured",
            "activegramsmanufactured", "unitsmanufactured", "siteinventoriableexpenses",
            "nonsiteinventoriableexpenses", "normalscrap", "contractorspend",
            "cogmjudgement", "carryovercost", "wipcostcogm"
        ]
        for col in numeric_columns:
            if col in df.columns:
                # Remove commas and other non-numeric characters
                df[col] = df[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
                # Convert to numeric, setting errors='coerce' to handle invalid values
                df[col] = pd.to_numeric(df[col], errors="coerce")
                # Fill NaN values with 0 (or handle them as needed)
                df[col] = df[col].fillna(0)

        # Define required columns (normalized)
        required_columns = [
            "years", "scenario", "draft", "demandtype", "productcode", "plant", "mfgcode",
            "lots", "volumetricgramsmanufactured", "activegramsmanufactured", "unitsmanufactured",
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

        # Dropdown for Product Name
        product_name_list = df["product"].unique()
        selected_product_name = st.selectbox("Select Product", product_name_list)

        # Auto-populate filters based on selected product
        if selected_product_name:
            product_data = df[df["product"] == selected_product_name]

            # Year Selection (Dropdown for one year at a time)
            year_list = sorted(product_data["years"].unique())
            selected_year = st.selectbox("Select Year", year_list)

            # Scenario Selection (Multi-Select Dropdown with "Select All" option)
            scenario_list = product_data["scenario"].unique()
            if st.checkbox("Select All Scenarios"):
                selected_scenarios = scenario_list
            else:
                selected_scenarios = st.multiselect(
                    "Select Scenarios",
                    options=scenario_list,
                    default=scenario_list  # Default to all scenarios
                )

            # Plant Selection (Include all sites)
            plant_list = product_data["plant"].unique()
            selected_plants = plant_list  # Include all plants by default

            # Mfg Code Selection
            mfg_code_list = product_data["mfgcode"].unique()
            selected_mfg_codes = mfg_code_list  # Include all Mfg Codes by default

            # DP/SP Type Selection
            dpsp_type_list = product_data["dpsptype"].unique()
            selected_dpsp_types = dpsp_type_list  # Include all DP/SP Types by default

            # Pres Type Selection
            pres_type_list = product_data["prestype"].unique()
            selected_pres_types = pres_type_list  # Include all Pres Types by default

            # Presentation Selection
            presentation_list = product_data["presentation"].unique()
            selected_presentations = presentation_list  # Include all Presentations by default

            # Filter data based on selections
            filtered_data = product_data[
                (product_data["years"] == selected_year) &
                (product_data["scenario"].isin(selected_scenarios)) &
                (product_data["plant"].isin(selected_plants)) &
                (product_data["mfgcode"].isin(selected_mfg_codes)) &
                (product_data["dpsptype"].isin(selected_dpsp_types)) &
                (product_data["prestype"].isin(selected_pres_types)) &
                (product_data["presentation"].isin(selected_presentations))
            ]

            if not filtered_data.empty:
                st.write("✅ Filtered Data:")
                st.dataframe(filtered_data)

                # Calculation Selector
                calculation_options = ["Average COGM Cost/Lot", "Average RM Cost/Lot", "Cost per Sold Unit"]
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

                elif selected_calculation == "Cost per Sold Unit":
                    # Perform Cost per Sold Unit calculation
                    total_cogm = filtered_data["cogmcost"].sum() / 1_000_000  # Convert to $M
                    total_lots = filtered_data["lots"].sum()
                    cost_per_sold_unit = (total_cogm / total_lots) if total_lots != 0 else 0

                    # Display results
                    st.write("### Calculation Results")
                    st.write(f"**Total COGM for Selected Product ({selected_product_name}) in {selected_year}:** ${total_cogm:,.2f}M")
                    st.write(f"**Total Lots for Selected Product ({selected_product_name}) in {selected_year}:** {total_lots:,}")
                    st.write(f"**Cost per Sold Unit for Selected Product ({selected_product_name}) in {selected_year}:** ${cost_per_sold_unit:,.2f}M")
            else:
                st.warning("❌ No data found for the selected filters.")
        else:
            st.warning("❌ Please select a product.")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the file: {e}")
else:
    st.info("ℹ️ Please upload a CSV file to get started.")
