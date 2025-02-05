# Tổng quan về System Tracking
System Tracking được thiết kế để đo tài nguyên sử dụng của một job python sử dụng hết bao nhiêu tài nguyên hệ thống theo từng giây và tổng hợp lại vào file log hoặc dashboard.
## Các metrics hỗ trợ đo:
- RAM usage
- Time to execute
- Số lượng vCPU sử dụng
- Peak RAM Usage
- Peak CPU Usage
## Ý tưởng
- System Tracking sẽ tạo một thread chỉ dùng để monitor, và thread này sẽ capture lại tài nguyên hệ thống mỗi giây. 
    + Ta thực hiện khởi tạo thread monitor bằng `start_tracking(duration_minutes=10, interval_seconds=1)`
- Thread để monitor này có thể chạy đồng thời cùng với process, bất kể đang làm gì (ví dụ: đang train model, thread monitor vẫn chạy song song mà không bị gián đoạn)
- Đến cuối mỗi python script, ta `stop_monitor()` để dừng thread monitor lại, và ta truy cập biến global `system_performance` để lấy kết quả tổng hợp.

## Cấu trúc thư mục

```
├── dist/                       # Chứa file wheel đã được đóng gói thành package
├── docs/                       # Tài liệu hướng dẫn sử dụng và API
├── examples/                   # Các file ví dụ
├── notebook/                   # Chứa các Jupyter Notebook dùng cho kiểm tra và phân tích
├── source/                     # Thư mục chính chứa mã nguồn của package
│   ├── system_tracking/        # Thư mục chính của package
│   │   ├── core.py             # Thực hiện phần core dự án, monitor hệ thống bằng multi threading
│   │   ├── load.py             # Chứa các hàm load file log ra nhiều định dạng khác nhau
│   │   ├── metric.py           # Evidently metric, sử dụng để tạo ra dashboard
│   │   ├── __init__.py         # File khởi tạo package Python
├── test/                       # Unit test và kiểm thử
├── .gitignore
├── MANIFEST.in                 # Khai báo các file cần đóng gói
├── README.md                   # Tài liệu hướng dẫn sử dụng dự án
├── requirements.txt
├── setup.py                    # Script thiết lập đóng gói package
```


## Hướng dẫn sử dụng
Ta thực hiện train một model đơn giản, và tracking system performance như ở bên dưới
```python
from system_tracking.core import start_tracking
from system_tracking.core import stop_monitoring
from system_tracking.core import system_performance
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from system_tracking.core import system_performance
from system_tracking.core import stop_monitoring

start_tracking(duration_minutes=10, interval_seconds=1)

# Generate data
X, y = make_classification(n_samples=10000, n_features=20, random_state=42)
# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

stop_monitoring()
system_performance.save_json('file_name.json')
```

## Xuất ra Dashboard
Ta kết hợp cùng với package mlops_observation để xuất ra dashboard
+ Load các file log đã được lưu
+ Có thể tổng hợp nhiều dataframe (đại diện cho file log của nhiều job) để xuất ra một dashboard tổng hợp

```python
from mlops_observation import Report
from system_tracking.load import load_dataframe
from system_tracking.load import concat_dataframe_dict_to_dataframe
from system_tracking.metric import SystemPerformanceMetric

# Load các file log
df1 = load_dataframe('save1.json')
df2 = load_dataframe('save2.json')
df_dict = {'Feature Engineering Job': df1, 'Inference Job': df2}
df = concat_dataframe_dict_to_dataframe(df_dict)

report = Report([
    SystemPerformanceMetric()
])
report.run(reference_data=None, current_data=df)
report.show()
report.save_html('report.html')
```
