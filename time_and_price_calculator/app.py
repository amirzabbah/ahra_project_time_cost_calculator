import pandas as pd
import streamlit as st


# Load the Excel file
file_path = "data/TP Calculator Dataset.xlsx"
data = pd.read_excel(file_path, sheet_name=None)

# Extract relevant tables from the Excel file
pages_df = data["DAX Measurements and Visualizat"]
power_query_df = data["Data Integration (ETL)"]
deployment_df = data["Project Deployment"]
proj_managers_df = data["Project Managers"]
developers_df = data["Developers"]


def create_glossary_selector(pages_df: pd.DataFrame, page_id_col_name: str = 'Page ID', 
                             page_name_col_name: str = 'Page Name', page_group_col_name: str = 'Category Name',
                             estimated_time_col_name: str = 'Estimated Time'):
    # page_dfs = []
    # categories = pages_df[page_group_col_name].unique()

    # for cat in categories:
    #     temp_df = pages_df[pages_df[page_group_col_name] == cat].reset_index(drop=False)
    #     temp_df = temp_df[[page_id_col_name, page_name_col_name]]
    #     temp_df['Favorite'] = False
    #     page_dfs.append(temp_df)
    
    # return page_dfs

    selector_page_df = pages_df[[page_group_col_name, page_name_col_name, estimated_time_col_name]]
    selector_page_df['Percent of Total'] = selector_page_df[estimated_time_col_name] / selector_page_df[estimated_time_col_name].sum()
    # selector_page_df['Percent of Total'] = round(selector_page_df['Percent of Total'] * 100, 2).astype('str') + ' %'
    selector_page_df['Favorite'] = False
    return selector_page_df



# Main Function to Run Streamlit App
def main():
    st.set_page_config(page_title='AHRA Time & Price Calculator', layout="wide")
    st.title("AHRA Dashboard Time and Cost Calculator")

    # Step 1: Display Checklist for Dashboard Pages
    st.header("1. Select Dashboard Pages", divider=True)
    with st.expander("Select Dashboard Pages", expanded=True):
        
        selector_page_df = create_glossary_selector(pages_df=pages_df)

        page_df_result = st.data_editor(
                selector_page_df,
                column_config={
                    "Favorite": st.column_config.CheckboxColumn(
                        "Your favorite?",
                        help="Select your **favorite** page",
                        default=False,
                    ),
                    "Percent of Total": st.column_config.ProgressColumn(
                            "Percentage of Total", min_value=0, max_value=1
                        ),
                },
                disabled=["Category Name", "Page Name", "Estimated Time", "Percent of Total"],
                hide_index=True,
                num_rows='dynamic',
                use_container_width=True,
                height=2140
            )
        
        selected_pages = page_df_result[page_df_result['Favorite'] == True]

    # Step 2: Data Modeling time (fixed)
    # st.header("2. Data Modeling")
    # st.write("Data Modeling time is fixed at 10 hours for all projects.")
    data_modeling_time = 10

    if len(selected_pages) > 0:
        
        selected_pages = selected_pages['Page Name'].unique()

        # Step 3: Power Query (SRC time depending on selected pages)
        st.header("2. Power Query Tasks", divider=True)
        power_query_time = calculate_power_query_time(selected_pages, power_query_df, pages_df)
        st.write(f"Total Power Query time based on selection: {power_query_time} hours")

        # Step 4: Project Deployment Options Checklist
        st.header("3. Project Deployment Tasks", divider=True)
        selected_deployment_tasks = st.multiselect(
            "Select any additional deployment tasks:",
            options=deployment_df["Dev Name"].tolist(),
        )

        # Developer and Project Manager Selection
        st.header("4. Developer and Project Manager Selection", divider=True)

        # developer_rate = st.slider("Set Developer Hourly Rate ($)", min_value=10, max_value=150, value=50)
        # manager_rate = st.slider("Set Project Manager Hourly Rate ($)", min_value=10, max_value=150, value=75)
            
        selected_proj_manager = st.selectbox(
            "Choose a Project Manager:",
            options=(proj_managers_df["Project Manager Name"]+ " - " + proj_managers_df["Salary Rate per Hour"].astype('str') + ' $ per hour').tolist(),
        )

        selected_developer = st.selectbox(
            "Choose a Developer:",
            options=(developers_df["Developer Name"]+ " - " + developers_df["Salary Rate per Hour"].astype('str') + ' $ per hour').tolist(),
        )

        proj_manager = selected_proj_manager.split(' - ')[0]
        developer = selected_developer.split(' - ')[0]

        proj_manager_hourly_rate = int(proj_managers_df[proj_managers_df['Project Manager Name'] == proj_manager]['Salary Rate per Hour'])
        developer_hourly_rate = int(developers_df[developers_df['Developer Name'] == developer]['Salary Rate per Hour'])

        # Calculate Total Time and Cost
        total_project_time = calculate_total_time(selected_pages, selected_deployment_tasks, pages_df, deployment_df) + data_modeling_time + power_query_time
        total_cost = calculate_cost(total_project_time, proj_manager_hourly_rate, developer_hourly_rate)

        # Display Summary
        st.header("Project Summary", divider=True)
        st.write(f"**Total Estimated Time:** {total_project_time} hours")
        st.write(f"**Total Estimated Cost:** ${total_cost:.2f}")

        hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Helper Functions
def calculate_power_query_time(selected_pages, power_query_df, pages_df):
    # Sum time from Power Query tasks related to selected pages
    selected_sections = []
    selected_section_ids = list(pages_df[pages_df["Page Name"].isin(selected_pages)]['Section IDs'])

    for sections in selected_section_ids:
        if ',' in str(sections):
            section_ids = sections.split(',')
        else:
            section_ids = [sections]
        for sec in section_ids:
            if int(sec) not in selected_sections:
                selected_sections.append(int(sec))

    return power_query_df[power_query_df["Section ID"].isin(selected_sections)]["Estimated Time"].sum()

def calculate_total_time(selected_pages, selected_deployment_tasks, pages_df, deployment_df):
    # Sum time for selected pages and deployment tasks
    page_time = pages_df[pages_df["Page Name"].isin(selected_pages)]["Estimated Time"].sum()
    deployment_time = deployment_df[deployment_df["Dev Name"].isin(selected_deployment_tasks)]["Estimated Time"].sum()
    return page_time + deployment_time

def calculate_cost(total_time, developer_rate, manager_rate):
    # # Assume 60% of time is developer time and 40% is project manager time
    # developer_time = total_time * 0.6
    # manager_time = total_time * 0.4
    return total_time * (developer_rate + manager_rate)

# Run the Streamlit app
if __name__ == "__main__":
    main()