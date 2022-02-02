import pandas as pd


def plot_change_proneness_per_file(proj_paths: ProjectPaths, min_date: str, max_date:str):
    conn = sqlite3.connect(proj_paths.get_path_to_project_db())
    
    sql_statement = """select * from change_proneness_file"""
    df = pd.read_sql_query(sql_statement, con_graph_db)

    df.style.background_gradient(cmap ='viridis')\
        .set_properties(**{'font-size': '5px'})
