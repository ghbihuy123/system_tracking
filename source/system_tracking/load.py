from .core import SystemPerformanceResult
import json
from typing import Dict
import pandas as pd
from typing import Dict

def load_data(file_name: str) -> SystemPerformanceResult:
    """
    Load data from a JSON file and populate a SystemPerformanceResult instance.
    Args:
        file_name (str): The name of the JSON file to load data from.
    Returns:
        SystemPerformanceResult: A new instance populated with the loaded data.
    """
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            # Create and return a new instance
            return SystemPerformanceResult(
                resource_logs=data.get("resource_logs", {}),
                peak_memory_global=data.get("peak_memory_global", 0.0),
                peak_cpu_global=data.get("peak_cpu_global", 0.0),
                total_cpus=data.get("total_cpus", 0),
                total_time=data.get("total_time", 0.0)
            )
    except Exception as e:
        print(f"Định dạng không đúng, kiểm tra lại file đã save. File đã save cần phải được save từ SystemPerformanceResult.save_json()")
        raise e  # Re-raise the exception for further handling

def load_dict(file_name: str) -> Dict:
    """
    Load dict from a JSON file into a dictionary.
    Args:
        file_name (str): The name of the JSON file to load data from.
    Returns:
        Dict: The data loaded from the JSON file as a dictionary.
    """
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}

def load_dataframe(file_name) -> pd.DataFrame:
    system_performance = load_data(file_name)
    resource_logs = system_performance.resource_logs
    df = pd.DataFrame.from_dict(resource_logs, orient="index")

    df.reset_index(inplace=True)
    df.rename(columns={"index": "timestamp"}, inplace=True)

    df["peak_memory_global"] = system_performance.peak_memory_global
    df["peak_cpu_global"] = system_performance.peak_cpu_global
    df["total_cpus"] = system_performance.total_cpus
    df["total_time"] = system_performance.total_time
    return df


def concat_dataframe_dict_to_dataframe(df_dict: Dict[str, pd.DataFrame]):
    df_list  = []
    for key in df_dict.keys():
        df_dict[key]['name'] = key
        df_list.append(df_dict[key])
    result = pd.concat(df_list)
    return result