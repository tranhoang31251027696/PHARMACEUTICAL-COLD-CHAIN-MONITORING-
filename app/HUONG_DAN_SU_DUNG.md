# Hướng dẫn sử dụng ColdChain

Cập nhật ngày 05/11/2026. Bản demo: https://coldchain-monitoring.netlify.app. Hướng dẫn đầy đủ theo từng màn hình: [Markdown](docs/HUONG_DAN_CHI_TIET_COLDCHAIN.md) hoặc [Word](docs/HUONG_DAN_CHI_TIET_COLDCHAIN.docx).

## Đọc giao diện phiên bản hiện tại

- **Settings của QA:** hồ sơ, ngôn ngữ, thông báo và giới hạn nhiệt độ 2–8°C. Phần chỉnh độ nhạy minh họa đã được gỡ.
- **Thermal Status / Thermal status:** trạng thái nhiệt của lô. High yêu cầu xem xét dữ liệu nhiệt; không phải điểm chất lượng tổng hợp. Trạng thái Unknown thể hiện chưa có phân loại, không đồng nghĩa an toàn.
- Bảng, thẻ và chi tiết lô không còn cột Risk score hoặc điểm rỗng. Xem nhiệt độ quan sát, cảnh báo, kết quả model và FEFO ở đúng phần tương ứng.
- **p_cal / threshold** trong kết quả dự báo và **old_score / new_score** trong regression vẫn là dữ liệu của các chức năng đang hoạt động.
- Bản demo online phục vụ giao diện và các kết nối backend đã cấu hình. Công cụ kiểm chứng hồi quy Python cần chạy bản local như bên dưới.

## Mở hệ thống

Đóng cửa sổ server cũ nếu đang chạy, rồi nhấp đúp `start_ui.bat` trong thư mục này. Hoặc:

```powershell
python start_ui.py
```

Trình duyệt mở địa chỉ local được in ra (mặc định http://127.0.0.1:8000, tự đổi port nếu bận). Chọn **Enter system → Use demo user → Sign in → Simulation** để mở Dataset & Research Workbench.

Chạy bằng `start_ui.py`, không mở HTML trực tiếp hay dùng server static cũ: server mới cung cấp API kiểm chứng Python và proxy model/data cùng origin.

Bản tại workspace hiện tại tự dùng môi trường Python nghiên cứu đã có nếu Python mặc định thiếu NumPy. Khi chuyển thư mục này sang máy khác, dùng Python 3.10+ (ưu tiên 3.13), tạo/kích hoạt môi trường ảo và cài:

```powershell
python -m pip install -r requirements-ui.txt
python start_ui.py
```

NumPy chỉ dùng cho exact checker local. XGBoost đang chạy trên model backend đã cấu hình; không cần nạp pickle hay cài XGBoost vào trình duyệt.

## Upload dataset ngoài

Trong Workbench, bấm **Choose File** hoặc kéo/thả CSV/TSV. Không bị giới hạn ở các nút mẫu. Các nút Mẫu sensor / FEFO / regression chỉ là tùy chọn thử nhanh.

Giới hạn đọc: 75 MiB và 500.000 dòng/file. Parser chạy trong Web Worker để không khóa giao diện; hỗ trợ comma, semicolon, tab, BOM, CRLF/LF, quoted comma, quoted newline và ô trống. Dữ liệu sai schema được báo lỗi, không tự biến ô số trống thành 0.

Dữ liệu upload chỉ tồn tại trong phiên trình duyệt. Sensor/inventory upload tự trở thành nguồn dữ liệu của Dashboard, Batches, Alerts và Reports; polling lịch sử bị tạm dừng để không ghi đè. Nó không tự ghi kho hoặc lưu dataset lên backend. Workbench hiển thị rõ tên file và loại dataset. Reload trang thì cần chọn lại file.

### 1. Sensor CSV — inference

Ví dụ:

```csv
Batch_ID,Timestamp,calibrated_temp,Humidity,Shipment_Mode
MY-BATCH-1,2026-01-01 00:00:00,5.0,60,Air
MY-BATCH-1,2026-01-01 01:00:00,5.2,62,Air
```

- Timestamp có thể dùng tên `Timestamp`, `time`, `datetime`, `date`, `Reading_Time`; dùng định dạng ISO hoặc YYYY-MM-DD HH:mm:ss. Ngày/giờ không hợp lệ và timestamp trùng trong một lô bị từ chối.
- Nhiệt độ ưu tiên `calibrated_temp`, sau đó `actual_temp`, `Temperature`, `temp`. Không tự chứng nhận chất lượng calibration từ tên cột.
- Nếu CSV thiếu Batch_ID, dùng một ID UPLOADED-BATCH và hiện thông báo. Nếu thiếu Humidity/Shipment_Mode, giá trị bổ sung phải lấy từ form hiển thị, có cảnh báo trong kết quả đọc file.
- Tùy chọn hiệu chỉnh `Temperature × (1 − Calibration_Offset_Pct/100)` chỉ áp dụng khi người dùng chọn; không tự sửa calibrated_temp/actual_temp. Chọn đúng profile dữ liệu của model, không suy đoán profile từ việc upload thành công.
- Có nhiều batch thì chọn lô trong dropdown. Các dòng được sắp theo thời gian; không trộn lịch sử của các lô khi gửi inference.
- Chọn cursor để gửi lịch sử đến thời điểm đó. Có thể điều chỉnh giả lập nhiệt độ ở điểm cuối; dữ liệu CSV nguồn không bị thay đổi.
- Model API giới hạn 100.000 readings/request. Workbench sẽ báo lỗi thay vì âm thầm cắt dữ liệu vượt giới hạn.
- Backend hiện nhận timestamp source-local **không timezone**. Với ISO có Z/offset, người dùng phải chọn chuyển sang UTC-naive hoặc chuẩn hóa dữ liệu theo timezone model. Không tự bỏ timezone âm thầm; chuyển đổi được ghi trong JSON inference.
- Checkbox “lịch sử đầy đủ” là xác nhận của người dùng, mặc định tắt; không tự giả định file upload là toàn bộ lịch sử của lô.

Bấm **Chạy inference backend**. Chỉ lúc này các readings của lô đến cursor được gửi tới model backend. UI hiển thị đúng model name, model_version, p_cal, threshold, status và JSON response; không thay bằng công thức local hoặc giá trị mặc định khi API lỗi.

Hiện API hỗ trợ operating_point=precision50 và các task w1_6/w1_12/w1_24. Nó đang trả model `t_only`; UI không tự gọi đó là thermal+Arrhenius. Precision50 là operating point đã cấu hình của model, không phải bảo đảm precision trên dataset mới. Vì API chưa hỗ trợ selectedModel/alpha tùy ý nên không hiển thị các lựa chọn giả.

Arrhenius ratio trên giao diện là phép tính mô tả Ea=51.044,8 J/mol, Tref=5°C. Không diễn giải thành xác nhận chất lượng vaccine, tuổi thọ lô hay khuyến nghị xuất kho.

### 2. Inventory CSV — FEFO

```csv
Product_ID,Product_Name,Batch_ID,Dynamic_Expiry_Date
P001,Product A,LOT-A,2027-01-01
P001,Product A,LOT-B,2027-01-02
```

Workbench tự nhận dạng inventory khi có Product_ID, Batch_ID, Dynamic_Expiry_Date. Tính lại dense rank trong từng Product_ID theo Dynamic_Expiry_Date tăng dần, xử lý cả timestamp tới nanosecond. Ngày bằng nhau có cùng rank; tên sản phẩm có dấu phẩy quoted được giữ nguyên. Mỗi product/batch cần một dòng inventory; không dùng sensor stream nhiều thời điểm làm inventory.

FEFO sử dụng hạn dùng do CSV cung cấp, không tự suy ra hạn dùng mới từ model early-warning hay tự approve/dispatch. Bảng có phân trang 50 dòng.

### 3. Regression CSV — phương pháp paper

```csv
id,y,old_score,new_score
obs-A,1,0.9,0.1
obs-B,0,0.5,0.5
obs-C,1,0.2,0.9
```

- IDs phải duy nhất; labels là 0/1; scores là số hữu hạn. Nếu có cột new_id, phải cùng ID và cùng thứ tự với id.
- Giới hạn UI/API kiểm chứng: 2.000 quan sát/lần để chặn công việc checker quá lớn trên máy local.
- Nhập domain lo/hi và query bằng **chuỗi rational**, ví dụ 0.30, 0.90, 1/2. Không dùng giá trị JSON float để tự coi là rational contract.
- Chọn precision inclusive hoặc strict cho reference/actual. Đây là so sánh dữ liệu và selector semantics khai báo, không tự xác minh source code chương trình bất kỳ.
- Bấm **So sánh và kiểm chứng độc lập**. Local API gọi producer `policy_exact`, sau đó consumer `streaming_checker` dựng lại membership và kiểm tra certificate. Chỉ sau khi consumer chấp nhận mới trả EQUIVALENT hoặc DIVERGENT.
- Hiển thị cells, ownership endpoints, PSC exact, witness IDs và input digest. PSC=0 không tự động đồng nghĩa tương đương; các điểm phân kỳ vẫn được báo.
- Query hỗ trợ finite set, interval và decimal lattice, đối chiếu cả full answer và Boolean index. Query ngoài domain bị từ chối.
- Có thể tải certificate kèm input thành JSON rồi dùng ô **kiểm tra lại certificate JSON**. Đường này chỉ gọi consumer, không tạo lại certificate bằng producer. Certificate bị sửa, input bị đổi hoặc schema sai sẽ bị từ chối.

Không thể tạo certificate cho một sensor CSV chỉ có nhiệt độ mà thiếu labels và cặp scores cũ/mới. UI không còn hiển thị G=162, max tie=14.192 hay PASS/chứng minh tương đương cố định cho upload mới.

## Cấu hình và dữ liệu lịch sử

`NETLIFY_DASHBOARD/api-config.js` là cấu hình công khai. Local mode dùng proxy same-origin của `start_ui.py`; proxy model/data mặc định trỏ backend Render hiện có. Có thể đổi model backend cho server bằng biến môi trường `COLDCHAIN_MODEL_API` do người vận hành cấu hình.

Khi chưa có upload hoặc sau khi bấm Return to historical/demo data, các màn Dashboard/Batches/Alerts đọc snapshot lịch sử qua API, có nhãn Historical hoặc UI demo khi API không trả dữ liệu. Khi có upload, các màn này và Reports dùng nguồn upload chung, không trộn với lịch sử/demo. Chúng không phải telemetry trực tiếp. Role/login/approval trong shell cũ vẫn là preview phía UI, không phải xác thực/phê duyệt bền vững phía server. Không nhập mật khẩu thật vào demo.

## Static Netlify và local research API

`NETLIFY_DASHBOARD/` chứa frontend đã build và các file Workbench đọc được. Có thể deploy toàn bộ thư mục này để cập nhật upload/parser và inference frontend; việc chuẩn bị local không tự deploy lên Netlify.

Static hosting không chạy Python. Exact regression cần server `start_ui.py` ở cùng origin, hoặc API nghiên cứu đã được triển khai riêng và cấu hình CORS/HTTPS phù hợp. Bản này đã kiểm thử đầy đủ theo đường local; không tuyên bố đã deploy research API mới lên Render/Netlify. Không gán URL backend hiện tại thành research API khi endpoint đó chưa tồn tại.

Model weights của server remote không được sao sang UI. Chưa có kiểm tra hash/weights deploy so với artifact training hoặc nghiên cứu người dùng độc lập/production; bản sửa là tích hợp chức năng nghiên cứu, không phải chứng nhận vận hành y tế.

## Mã và kiểm thử

- `NETLIFY_DASHBOARD/coldchain-runtime.js`: CSV/validation/timezone/FEFO/HTTP utilities.
- `NETLIFY_DASHBOARD/coldchain-workbench.js`: component Workbench đọc được, được bridge vào tab Simulation.
- `NETLIFY_DASHBOARD/csv-worker.js`: đọc CSV ngoài main thread.
- `backend/regression_service.py`: adapter HTTP cho research contract.
- `backend/engine/`: 4 module nghiên cứu sao nguyên bytes cùng giấy phép và SOURCE_MANIFEST.
- `start_ui.py`: phục vụ static, API research local và proxy inference/data; mặc định chỉ bind loopback.
- `SOURCE_PATCH/workbench/`: bản sao source frontend để tham khảo; các file đang chạy là trong NETLIFY_DASHBOARD.

Từ thư mục ColdChain UI, dùng Node.js nếu muốn chạy kiểm thử parser; unittest Python kiểm tra API loopback mà không gọi backend model remote:

```powershell
node tests/test_runtime.cjs
node tests/test_dataset.cjs
node tests/test_workflow.cjs
python -m unittest discover -s tests -p "test_*.py" -v
```

Bằng chứng kiểm thử trình duyệt headless, file upload tổng hợp nằm ngoài thư mục sample, inference backend thật, từ chối certificate giả và lỗi API nằm ở `PROJECT/outputs/COLDCHAIN_SYSTEM_FIX/`. Bản cũ trước sửa đã lưu tại `PROJECT/BACKUP/ColdChain_UI_BEFORE_FIX_20261031/`.

## Dataset upload cho toàn app (31/10/2026)

- Vào Simulation để upload sensor/inventory CSV. Dữ liệu hợp lệ tự thay nguồn cho toàn app; banner luôn ghi tên file. Sensor tự tính min/max, số readings, số điểm ngoài [2,8]°C và cảnh báo tại lần đo cuối. Inventory tính dense FEFO theo sản phẩm/hạn dùng đã cung cấp.
- Checkbox “Automatically run backend models…” mặc định bật: sau upload sensor, app gửi lần lượt lịch sử từng batch tới backend, chạy cả 6/12/24 giờ với precision50, history_complete=true chỉ sau khi bạn xác nhận lịch sử đầy đủ. Nếu chưa xác nhận, app chỉ tính local và chờ xác nhận ở banner; backend hiện từ chối lịch sử không đầy đủ vì dùng cumulative features. Không tự xác nhận thay người dùng. Tắt auto-inference trước upload nếu chỉ muốn tính local. Có Cancel và Run models for all batches. Chuỗi model phải theo giờ liên tục và timestamp không timezone; lỗi được ghi riêng từng batch, không coi là an toàn.
- Dashboard/Batches/Alerts/Reports trong chế độ upload hiển thị dữ liệu tính thật; model alert dựa trên trường alert của API, khác cảnh báo nhiệt độ đo được. Reports xuất JSON kết quả thật thay cho report demo. Số điểm vượt ngưỡng không phải số giờ vượt ngưỡng. Chưa lưu lâu dài sau reload; workflow QA/Warehouse trong phiên được mô tả ở phần bên dưới.
- Regression CSV chỉ phục vụ kiểm chứng cặp scores cũ/mới ở section 3; không thay inventory/sensor đang hoạt động. Không bắt buộc chạy regression để phân tích dataset đơn.
- Bấm Return to historical/demo data để hủy các request model đang chờ áp dụng, bỏ nguồn upload và quay lại nguồn ban đầu. Request cũ hoàn thành sau khi đổi file không được gắn vào file mới.

### CSV logger Nepal

Hỗ trợ trực tiếp định dạng đã kiểm tra: dòng ghi chú “All Date-Time values are in: UTC +05:45”, sau đó index, YYYY-MM-DD, HH:mm:ss, temperature, ô trống cuối. Upload từng CSV đã giải nén, không upload ZIP/XLSX. Các định dạng logger khác chưa được tự đoán.

Mỗi logger thành một series ID, chưa xác minh là batch hàng. Giữ đồng hồ Nepal UTC+05:45 theo giờ địa phương, không tự coi đó là UTC. Chỉ lấy giờ có đủ 6 mẫu cách nhau 10 phút, tính trung bình giờ; loại giờ thiếu/không đều và báo số điểm loại. Không nội suy khoảng thiếu; model có thể từ chối chuỗi có khoảng trống. Trung bình giờ có thể che spike ngắn; số liệu trên app là số liệu sau tổng hợp. Raw CSV không bị sửa.

Humidity/Shipment_Mode thiếu dùng giá trị trên import form và có cảnh báo (mặc định 60/Air, là giả định). Khả năng backend trả kết quả không xác nhận chất lượng dự báo trên Nepal. File sensor không đủ thông tin tự tính FEFO hoặc hạn dùng; cần inventory riêng. Bản hiện tại mỗi lần upload thay nguồn trước, chưa merge sensor và inventory từ nhiều file.

Mã quản lý nguồn chung: NETLIFY_DASHBOARD/coldchain-dataset.js. Kiểm thử state/Nepal: tests/test_dataset.cjs. Bằng chứng browser global_upload_checks.json phân biệt backend giả lập có kiểm soát với request backend thật trong global_upload_live_backend.json.

## QA Manager và Warehouse Staff — workflow đồng bộ (31/10/2026)

Hai vai trò dùng chung nguồn dữ liệu, trạng thái lô, yêu cầu QA review, xác nhận cảnh báo và audit trong **cùng phiên tab trình duyệt**. Log out rồi chọn vai trò khác không xóa quyết định. Model cập nhật và polling cùng nguồn không xóa quyết định. Đổi dataset hoặc reload sẽ bắt đầu workflow mới; chưa có cơ sở dữ liệu workflow hoặc đồng bộ nhiều thiết bị/tab.

- QA Manager: View details/Review batch → Approve hoặc Reject → Confirm action. Reject bắt buộc lý do. Approve lô có trạng thái nhiệt High cần ghi chú đánh giá. Có thể Reject lô Approved/In queue để giữ lại trước khi dispatch; không sửa lô đã Dispatched.
- Warehouse Staff: Dispatch Board/Batches → Request QA review cho lô chờ duyệt; có ghi nhận trong bảng/audit của QA. Không có quyền Approve/Reject. Với Approved, chọn Add to Queue → Confirm action; với In queue, chọn Confirm Dispatch → Confirm action. Cancel không đổi trạng thái. Lô Rejected mở được lý do QA nhưng không queue/dispatch.
- Khi có FEFO rank và Product_ID, chỉ xử lý trước các lô đã Approved/In queue có hạn dùng sớm hơn cùng sản phẩm. Các lô rank bằng nhau không chặn nhau. Lô thiếu dữ liệu FEFO không được gán một thứ hạng giả.
- Mỗi xác nhận kiểm tra lại vai trò, trạng thái hiện tại và FEFO để từ chối thao tác từ màn hình đã cũ. Đây là guard trong app demo, không thay cho phân quyền server.
- Alerts: QA Acknowledge Alert, Warehouse xem trạng thái QA và mở View batch details. Acknowledge không tự resolve cảnh báo hoặc approve lô. Không tạo trip/driver telemetry giả; lịch sử upload lấy từ file, lịch sử nguồn saved được gọi qua API sensor và báo lỗi rõ nếu thiếu.
- Warehouse giữ đúng 4 tab: Dispatch Board, Batches, Alerts, Settings. QA vẫn có Reports và Simulation. Dataset do QA upload được dùng chung khi đổi sang Warehouse. Warehouse có Download workflow audit JSON trong Batches; không thêm tab Reports/Simulation.
- Nút Forgot password? giải thích đây là demo và hướng dẫn Use demo user, không giả lập một email khôi phục đã gửi.

Mã nguồn đọc được: NETLIFY_DASHBOARD/coldchain-workflow.js; bản sao SOURCE_PATCH/workbench/coldchain-workflow.js. Kiểm thử: node tests/test_workflow.cjs. Browser evidence: outputs/COLDCHAIN_SYSTEM_FIX/warehouse_checks.json. Các thao tác workflow không ghi giao dịch xuất kho thật.

### Phân biệt Dispatch Board và Batches

- Dispatch Board của Warehouse là bảng thao tác dạng thẻ theo 3 nhóm: Dispatch queue (In queue), Ready to queue (Approved), Waiting for QA (Awaiting approval). Các lô Dispatched/Rejected nằm trong mục thu gọn. Tại đây thực hiện Request QA review, Add to Queue và Confirm Dispatch, có kiểm tra FEFO.
- Batches là bảng tra cứu toàn bộ inventory, có tìm kiếm/lọc trạng thái, nhiệt độ, FEFO rank, dynamic expiry, location và View details; không lặp lại board thẻ hoặc các nút dispatch trên từng hàng. Cùng một thay đổi trạng thái xuất hiện ở cả hai tab.
- Warehouse không có thêm Reports hay Simulation trong sidebar. Menu vẫn là Dispatch Board / Batches / Alerts / Settings, ở cả nguồn lịch sử và nguồn upload. Việc upload thực hiện ở Simulation của QA; đổi vai trò vẫn giữ nguồn dữ liệu trong cùng phiên.
