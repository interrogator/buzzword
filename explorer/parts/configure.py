"""
buzzword explorer: .env processing
"""
import os

from dotenv import load_dotenv


def configure_buzzword():
    """
    Read .env, give defaults if missing

    Raise ValueError if .env not there
    """
    trues = {"1", "true", "True", "Y", "y", "yes", True}
    env_path = os.path.abspath(".env")
    if not os.path.isfile(env_path):
        raise ValueError(f'Please configure {env_path}')
    load_dotenv(dotenv_path=env_path)
    drop_columns = os.getenv("BUZZWORD_DROP_COLUMNS")
    if drop_columns:
        drop_columns = drop_columns.split(",")
    table_size = os.getenv("BUZZWORD_TABLE_SIZE")
    if table_size:
        table_size = [int(i) for i in table_size.split(",")]
    max_dataset_rows = os.getenv("BUZZWORD_MAX_DATASET_ROWS")
    if max_dataset_rows and max_dataset_rows.strip():
        max_dataset_rows = int(max_dataset_rows.strip())
    else:
        max_dataset_rows = None

    return dict(
        corpora_file=os.getenv("BUZZWORD_CORPORA_FILE", "corpora.json"),
        root=os.getenv("BUZZWORD_ROOT", "."),
        debug=os.getenv("BUZZWORD_DEBUG", True) in trues,
        load=os.getenv("BUZZWORD_LOAD", True) in trues,
        add_governor=os.getenv("BUZZWORD_ADD_GOVERNOR", False) in trues,
        title=os.getenv("BUZZWORD_TITLE"),
        page_size=int(os.getenv("BUZZWORD_PAGE_SIZE", 25)),
        max_dataset_rows=max_dataset_rows,
        drop_columns=drop_columns,
        table_size=table_size,
        load_layouts=os.getenv("BUZZWORD_LOAD_LAYOUTS", True) in trues
    )
