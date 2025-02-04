## Getting started
Project này để nghiên cứu đo performance theo từng scope, như:
- Đo theo function (có thể là dưới dạng decorator)
- Đo theo từng cell trong jupiter notebook
- Đo theo cả một notebook
- Đo theo một python script

Các metrics sẽ tìm hiểu:
- RAM usage
- Time to execute
- Số lượng vCPU sử dụng

Expect đầu ra:
- Dưới dạng file JSON
- Trường hợp lý tưởng: Tạo ra được thêm một dashboard để đo system performance, tích hợp vào hệ thống Mlops Observation đã có sẵn


## Code Snippet

system_performance = SystemPerformanceResult()
stop_thread = threading.Event()
monitor_thread = threading.Thread(target=log_resource_usage, args=(10,), daemon=True)
monitor_thread.start()

stop_monitoring()