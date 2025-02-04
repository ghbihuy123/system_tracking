import psutil
import pandas as pd
import os
import time
import threading
from typing import Dict
from dataclasses import dataclass, field
import json


@dataclass
class SystemPerformanceResult:
    resource_logs: Dict[str, Dict[str, float]] = field(default_factory=dict)  # Logs of resource usage
    peak_memory_global: float = 0.0  # Peak memory usage in MiB
    peak_cpu_global: float = 0.0  # Peak CPU usage in terms of cores
    total_cpus: int = 0  # Total logical CPUs
    total_time: float = 0.0  # Total execution time
    def save_json(self, file_name: str):
        """
        Save the SystemPerformanceResult instance as a JSON file.
        Args:
            file_name (str): The name of the JSON file to save the data to.
        """
        try:
            with open(file_name, 'w') as file:
                json.dump({
                    "resource_logs": self.resource_logs,
                    "peak_memory_global": self.peak_memory_global,
                    "peak_cpu_global": self.peak_cpu_global,
                    "total_cpus": self.total_cpus,
                    "total_time": self.total_time
                }, file, indent=4)
            print(f"System performance data saved to {file_name}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")


# Function to monitor resource usage
def log_resource_usage(duration_minutes=10, interval_seconds=1):
    """
    duration_minutes: Khung thời gian tối đa mà resource logs được lưu, mặc định là 10 phút
    interval_seconds: Checkpoint của resource logs sẽ được lưu sau mỗi 'interval_seconds' giây
    """
    global system_performance
    process = psutil.Process(os.getpid())
    system_performance.total_cpus = psutil.cpu_count(logical=True)  # Total logical CPUs
    start_time = time.time()

    while not stop_thread.is_set() and (time.time() - start_time) < (duration_minutes * 60):
        current_memory = process.memory_info().rss / (1024 * 1024)  # Memory in MiB
        current_cpu_percent = psutil.cpu_percent(interval=None)  # Total CPU usage in percentage
        current_cpu_usage = (current_cpu_percent / 100) * system_performance.total_cpus  # CPUs utilized
        system_performance.peak_memory_global = max(system_performance.peak_memory_global, current_memory)  # Peak memory
        system_performance.peak_cpu_global = max(system_performance.peak_cpu_global, current_cpu_usage)  # Peak CPU usage

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp
        system_performance.resource_logs[timestamp] = {
            "current_memory": current_memory,
            "current_cpu_percent": current_cpu_percent,
            "current_cpu_usage": current_cpu_usage,
            "total_cpus": system_performance.total_cpus
        }

        print(
            f"[{timestamp}] Memory: {current_memory:.2f} MiB, CPU: {current_cpu_usage:.2f}/{system_performance.total_cpus} cores, "
            f"Peak Memory: {system_performance.peak_memory_global:.2f} MiB, Peak CPU: {system_performance.peak_cpu_global:.2f} cores",
            end="\r"
        )
        system_performance.total_time = time.time() - start_time
        time.sleep(interval_seconds)

    print(f"\nTotal Execution Time: {system_performance.total_time:.2f} seconds")
    print(f"Peak Memory Usage: {system_performance.peak_memory_global:.2f} MiB")
    print(f"Peak CPU Usage: {system_performance.peak_cpu_global:.2f} cores out of {system_performance.total_cpus} cores")


# Function to stop the thread
def stop_monitoring():
    stop_thread.set()
    monitor_thread.join()  # Wait for the thread to finish
    print("\nMonitoring stopped.")


system_performance = SystemPerformanceResult()

def start_tracking(duration_minutes=10, interval_seconds=1):
    """
    duration_minutes: Khung thời gian tối đa mà resource logs được lưu, mặc định là 10 phút
    interval_seconds: Checkpoint của resource logs sẽ được lưu sau mỗi 'interval_seconds' giây
    """
    global monitor_thread, stop_thread
    print('Start tracking!')
    stop_thread = threading.Event()
    monitor_thread = threading.Thread(target=log_resource_usage, args=(duration_minutes, interval_seconds), daemon=True)
    monitor_thread.start()