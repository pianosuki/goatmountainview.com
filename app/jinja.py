from typing import Optional, List
from datetime import datetime
import app.crud as crud


def extend_env(env):
    env.filters["split_string"] = split_string
    env.globals["find_item_index"] = find_item_index
    env.globals["column_is_nullable"] = crud.column_is_nullable
    env.globals["get_table_row_column"] = crud.get_table_row_column
    env.globals["current_date_time"] = current_date_time
    env.globals["slideshow_speed_constant"] = 128


def split_string(value, delimiter) -> List[str]:
    return value.split(delimiter)


def find_item_index(items: list, item_name: str) -> Optional[int]:
    index = None
    for i, item in enumerate(items):
        if item == item_name:
            index = i
            break
    return index


def current_date_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
