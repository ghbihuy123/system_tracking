from .core import SystemPerformanceResult
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import InputData
from evidently.renderers.html_widgets import BaseWidgetInfo
from evidently.renderers.html_widgets import header_text
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import plotly_figure
from typing import List
from typing import Optional
from typing import Dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_resource_by_time(data: pd.DataFrame) -> go.Figure:
    # Create a figure with two subplots arranged side-by-side
    fig = make_subplots(
        rows=1, cols=2,  # One row, two columns
        shared_yaxes=False,  # Separate y-axes for memory and CPU
        column_titles=["Memory Usage (MiB)", "CPU Usage"],  # Titles for each subplot
        horizontal_spacing=0.1  # Spacing between subplots
    )

    # Left subplot: current_memory
    fig.add_trace(go.Scatter(
        x=data["timestamp"],
        y=data["current_memory"],
        mode='lines',
        name='Current Memory (MiB)',
        line=dict(color='#0B60B0'),
        showlegend=False
    ), row=1, col=1)

    # Right subplot: current_cpu_percent
    fig.add_trace(go.Scatter(
        x=data["timestamp"],
        y=data["current_cpu_usage"],
        mode='lines',
        name='Current CPU Percent',
        line=dict(color='#0B60B0'),
        showlegend=False
    ), row=1, col=2)

    # Update layout
    fig.update_layout(
        title="System Resource Usage Over Time",
        xaxis=dict(
            title="Time",
            showgrid=False,
            zeroline=False,
        ),  # X-axis for memory usage
        xaxis2=dict(
            # title="Time",
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title="Memory Usage (MiB)", 
            showgrid=False,
            zeroline=False,
        ),  # Y-axis for memory usage
        yaxis2=dict(
            title="CPU Usage", 
            showgrid=False,
            zeroline=False,
        ),  # Y-axis for CPU usage
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

class SystemPerformanceMetricResult(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:SystemPerformanceMetricResult"
    sys_performance_summary: Dict[str, SystemPerformanceResult]
    resource_logs_table_dict: Dict[str, pd.DataFrame]

class SystemPerformanceMetric(Metric[SystemPerformanceMetricResult]):
    class Config:
        type_alias = "evidently:metric:SystemPerformanceMetric"
    

    def calculate(self, data: InputData):
        df_dict = self.split_dataframe_by_name(data.current_data)
        sys_performance_summary = {}
        resource_logs_table_dict = {}
        # print(df_dict)
        for key in df_dict.keys():
            df = df_dict[key]
            resource_logs_table = df.drop(['peak_cpu_global', 'total_cpus', 'total_time', 'peak_memory_global'], axis=1)
            resource_logs_table_dict[key] = resource_logs_table

            peak_cpu_global=df['peak_cpu_global'].unique()[0]
            total_cpus=df['total_cpus'].unique()[0]
            total_time=df['total_time'].unique()[0]
            peak_memory_global=df['peak_memory_global'].unique()[0]
            sys_performance = SystemPerformanceResult(
                peak_cpu_global=peak_cpu_global,
                total_cpus=total_cpus,
                total_time=total_time,
                peak_memory_global=peak_memory_global,
            )
            sys_performance_summary[key] = sys_performance
        
        return SystemPerformanceMetricResult(
            sys_performance_summary=sys_performance_summary,
            resource_logs_table_dict=resource_logs_table_dict
        )
    def split_dataframe_by_name(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Splits a DataFrame into multiple DataFrames based on unique values in the 'name' column.

        Args:
            df (pd.DataFrame): The input DataFrame containing a 'name' column.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary where keys are unique names from the 'name' column
                                    and values are DataFrames corresponding to each name.
        """
        result = {name: group.drop('name', axis=1) for name, group in df.groupby("name")}
        return result


@default_renderer(wrap_type=SystemPerformanceMetric)
class PeriodMissingValueRender(MetricRenderer):
    def generate_performance_summary(self, performance_summary: SystemPerformanceResult):
        counters = [
            CounterData.int("Total CPU", performance_summary.total_cpus),
            CounterData.string("Peak CPU Usage", f'{round(performance_summary.peak_cpu_global, 2)}/{performance_summary.total_cpus}'),
            CounterData.string("Peak Memory Usage (MB)", f'{round(performance_summary.peak_memory_global, 2)}'),
            CounterData.string("Total Execute Time (Minute)",f'{round(performance_summary.total_time / 60, 2)}'),
        ]
        return [
            counter(counters=counters)
        ]

    def generate_resource_logs(logs: pd.DataFrame):
        fig = plot_resource_by_time(logs)
        return fig

    def render_html(self, obj: SystemPerformanceMetric) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        color_options = self.color_options
        report_names = results.sys_performance_summary.keys()
        all_widgets = []
        for report_name in report_names:
            all_widgets.append(
                header_text(label=f"System Performance for {report_name}")
            )
            summary_lst = self.generate_performance_summary(results.sys_performance_summary[report_name])
            fig = plot_resource_by_time(results.resource_logs_table_dict[report_name])
            fig_widget = [plotly_figure(title='', figure=fig)]
            all_widgets += summary_lst + fig_widget
        return all_widgets