# ColdChain UI

Tài liệu giải thích chi tiết app, từng màn hình/nút, đầu vào/đầu ra và các chỉ số: [Bản Word](docs/HUONG_DAN_CHI_TIET_COLDCHAIN.docx) hoặc [bản Markdown](docs/HUONG_DAN_CHI_TIET_COLDCHAIN.md). Nội dung đối chiếu bản local ngày 05/11/2026, gồm cả menu Warehouse bốn tab.

Chạy `start_ui.bat` hoặc `python start_ui.py`, rồi Enter system → Use demo user → Sign in → Simulation.

Đã hỗ trợ upload CSV/TSV từ máy: sensor multi-batch, inventory FEFO và regression dataset. Parser mới xử lý ô trống/quoted fields trong worker. Inference dùng kết quả backend thật; chẩn đoán regression dùng producer + independent checker local, không có PASS gán sẵn.

Đọc [HUONG_DAN_SU_DUNG.md](HUONG_DAN_SU_DUNG.md) để xem schema, timezone, tùy chọn, giới hạn và cách kiểm thử. Đóng server cũ rồi khởi động lại để nạp API mới.

Static Netlify không tự chạy checker Python; mặc định bản tích hợp đầy đủ chạy local. Workflow QA/Warehouse hoạt động trong cùng phiên tab; chưa lưu giao dịch lên cơ sở dữ liệu kho.

Sensor/inventory upload tự thay nguồn của Dashboard, Batches, Alerts và Reports trong phiên hiện tại. Model tự chạy nếu checkbox auto-inference bật; có thể tắt trước upload. Hỗ trợ CSV logger Nepal đã kiểm tra và tổng hợp về giờ, kèm cảnh báo dữ liệu thiếu. Regression là chức năng tùy chọn riêng. Đọc mục Dataset upload cho toàn app trong hướng dẫn.

QA/Warehouse dùng chung workflow trong cùng phiên tab: QA approve/reject, Warehouse request review → queue → confirm dispatch, có FEFO guards và audit JSON. Đổi vai trò hoặc model refresh không làm mất quyết định; đổi dataset/reload khởi tạo lại. Xem hướng dẫn để biết giới hạn lưu trữ và phân quyền.

Warehouse sidebar giữ 4 tab gốc: Dispatch Board / Batches / Alerts / Settings. Dispatch Board dùng thẻ thao tác theo hàng chờ; Batches dùng bảng tra cứu riêng. QA upload qua Simulation; Warehouse dùng cùng nguồn khi đổi vai trò.

Bản 05/11/2026 đã gỡ khối chỉnh độ nhạy minh họa và các điểm chất lượng chưa được tính. Giao diện giữ Thermal Status, kết quả dự báo backend và FEFO có dữ liệu thực tế.
