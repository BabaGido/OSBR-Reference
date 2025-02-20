import streamlit as st
import pandas as pd

# Title of the app
st.title("COGM Calculator")

# Informational Guide
st.sidebar.title("Plant Site Information")
st.sidebar.write("""
### Categories of Products and Plant Sites

#### **Drug Substance (DS) Plants**
- **Location**: AML6, AML7, ARI30, ARI5, ASM1, ASM2, ANC1, ANC2, ATO23, ATO 07
- **Description**: DS plants are responsible for the production of active pharmaceutical ingredients (APIs).

#### **Drug Product (DP) Plants**
- **Location**: ATO20, ADL, AML14
- **Description**: DP plants handle the formulation and packaging of drug products.

#### **Finished Drug Product (FDP) Plants**
- **Location**: AML, ABR, AOH
- **Description**: FDP plants manage the final packaging and distribution of finished drug products.
""")

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

        # Year Selection (Multi-Select Dropdown)
        year_list = sorted(df["years"].unique())
        selected_years = st.multiselect(
            "Select Years",
            options=year_list,
            default=year_list  # Default to all years
        )

        # Scenario Selection (Multi-Select Dropdown with "Select All" option)
        scenario_list = df["scenario"].unique()
        if st.checkbox("Select All Scenarios"):
            selected_scenarios = scenario_list
        else:
            selected_scenarios = st.multiselect(
                "Select Scenarios",
                options=scenario_list,
                default=scenario_list  # Default to all scenarios
            )

        # Dropdown for Product Code
        product_list = df["productcode"].unique()
        selected_product = st.selectbox("Select Product Code", [""] + list(product_list))

        # Dropdown for Plant
        plant_list = df["plant"].unique()
        selected_plant = st.selectbox("Select Plant", [""] + list(plant_list))

        # Dropdown for Mfg Code
        mfg_code_list = df["mfgcode"].unique()
        selected_mfg_code = st.selectbox("Select Mfg Code", [""] + list(mfg_code_list))

        # Dropdown for Product
        product_name_list = df["product"].unique()
        selected_product_name = st.selectbox("Select Product", [""] + list(product_name_list))

        # Dropdown for DP/SP Type
        dpsp_type_list = df["dpsptype"].unique()
        selected_dpsp_type = st.selectbox("Select DP/SP Type", [""] + list(dpsp_type_list))

        # Dropdown for Pres Type
        pres_type_list = df["prestype"].unique()
        selected_pres_type = st.selectbox("Select Pres Type", [""] + list(pres_type_list))

        # Dropdown for Presentation
        presentation_list = df["presentation"].unique()
        selected_presentation = st.selectbox("Select Presentation", [""] + list(presentation_list))

        # Filter data based on selections
        if selected_years:
            filtered_data = df[
                (df["years"].isin(selected_years)) &
                (df["scenario"].isin(selected_scenarios)) &
                (df["productcode"] == (selected_product if selected_product else df["productcode"])) &
                (df["plant"] == (selected_plant if selected_plant else df["plant"])) &
                (df["mfgcode"] == (selected_mfg_code if selected_mfg_code else df["mfgcode"])) &
                (df["product"] == (selected_product_name if selected_product_name else df["product"])) &
                (df["dpsptype"] == (selected_dpsp_type if selected_dpsp_type else df["dpsptype"])) &
                (df["prestype"] == (selected_pres_type if selected_pres_type else df["prestype"])) &
                (df["presentation"] == (selected_presentation if selected_presentation else df["presentation"]))
            ]
        else:
            filtered_data = pd.DataFrame()  # Empty DataFrame if no years are selected

        if not filtered_data.empty:
            st.write("✅ Filtered Data:")
            st.dataframe(filtered_data)

            # Calculation Selector
            calculation_options = ["Average COGM Cost/Lot", "Average RM Cost/Lot", "DS Cost per Gram", "DP/FDP: Cost per Unit"]
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
                
            elif selected_calculation == "DS Cost per Gram":
                #Perform DS: Cost per Gram Calculation
                total_cogm_cost = filtered_data["cogmcost"].sum()
                total_active_grams = filtered_data["activegramsmanufactured"].sum()
                cost_per_gram = (total_cogm_cost / total_active_grams) if total_active_grams != 0 else 0

                #Display results
                st.write("### Calculation Results")
                st.write(f"**Total COGM Cost for Selected Product ({selected_product_name}):** ${total_cogm_cost:,.2f}")
                st.write(f"**Total Active Grams for Selected Product ({selected_product_name}):** {total_active_grams:,}")
                st.write(f"**Cost per Gram for Selected Product ({selected_product_name}):** ${cost_per_gram:,.2f}")

            elif selected_calculation == "DP/FDP: Cost per Unit":
                #Perfrom DP/FDP: Cost per Unit Calculation
                total_cogm_cost = filtered_data["cogmcost"].sum()
                total_units = filtered_data["unitsmanufactured"].sum()
                cost_per_unit = (total_cogm_cost / total_units) if total_units != 0 else 0

                #Display results
                st.write("### Calculation Results")
                st.write(f"**Total COGM Cost for Selected Product ({selected_product_name}):** ${total_cogm_cost:,.2f}")
                st.write(f"**Total Manufactured Units for Selected Product ({selected_product_name}):** {total_units:,}")
                st.write(f"**Cost per Unit for Selected Product ({selected_product_name}):** ${cost_per_unit:,.2f}")

        else:
            st.warning("❌ No data found for the selected filters.")
    except Exception as e:
        st.error(f"❌ An error occurred while processing the file: {e}")
else:
    st.info("ℹ️ Please upload a CSV file to get started.")
