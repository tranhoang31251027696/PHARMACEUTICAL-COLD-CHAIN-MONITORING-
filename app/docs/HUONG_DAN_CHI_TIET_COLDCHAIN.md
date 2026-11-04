# Hướng dẫn chi tiết ứng dụng ColdChain

Tài liệu giải thích mục đích ứng dụng, dữ liệu đầu vào, từng màn hình và thao tác, kết quả đầu ra và cách đọc các chỉ số. Nội dung đối chiếu với mã nguồn local ngày 31/10/2026, sau khi Warehouse được giữ đúng bốn tab. Tên nút giữ bằng tiếng Anh như trên app; phần giải thích dùng tiếng Việt.

ColdChain hỗ trợ xem dữ liệu nhiệt độ, nhận cảnh báo từ quan sát và model, tra cứu lô, xếp thứ tự FEFO và thực hành luồng QA duyệt lô rồi Warehouse chuẩn bị xuất. Simulation còn có công cụ nghiên cứu để so sánh quyết định giữa hai phiên bản model.

Kết luận cần nhớ: dữ liệu sensor và inventory được tính ngay sau upload. Dự báo cần backend model, lịch sử phù hợp và xác nhận đầy đủ. Quyết định QA và Warehouse được đồng bộ trong cùng phiên tab trình duyệt; chưa ghi thành giao dịch kho trên server.

## Cách đọc tài liệu

| Bạn muốn biết | Đọc phần |
|---|---|
| App giúp làm gì và ai dùng | 1 đến 3 |
| Dataset nào đưa vào được | 4 và 5 |
| Mỗi màn hình và nút làm gì | 6 đến 11 |
| Model và các chỉ số có nghĩa gì | 12 đến 14 |
| Dùng dữ liệu Nepal | 15 |
| Hiểu phép kiểm chứng regression | 16 và 17 |
| Thực hành và xử lý lỗi | 18 và 19 |
| Kiểm tra phạm vi và mã nguồn | 20 |

**Các khái niệm khác nhau:** nhiệt độ quan sát là dữ liệu đo; p_cal là kết quả model; Approved là quyết định workflow; EQUIVALENT là kết luận về hai selector trên dữ liệu cố định. Không dùng một loại kết quả để thay nghĩa cho loại còn lại.

<!-- PAGE -->
# 1 Ứng dụng giải quyết công việc gì

## Theo dõi dữ liệu và nhận diện vấn đề

Người dùng đưa chuỗi đo vào app để xem nhiệt độ theo thời gian, giá trị thấp nhất và cao nhất, các điểm ngoài vùng [2,8]°C và lần đo mới nhất. Việc này giúp phát hiện lô hoặc logger cần xem xét. Với lịch sử đủ điều kiện, app gọi backend để nhận dự báo cảnh báo sớm cho các cửa sổ 6, 12 và 24 giờ.

## Hỗ trợ quyết định và chuẩn bị xuất kho

QA Manager xem số liệu, cảnh báo và thông tin lô, sau đó ghi nhận Approve hoặc Reject trong workflow. Warehouse Staff thấy quyết định này, yêu cầu QA xem xét khi cần, đưa lô đã Approved vào hàng chờ rồi xác nhận Dispatched. FEFO được dùng để ưu tiên lô đã được phép xử lý có hạn dùng sớm hơn trong cùng sản phẩm.

## Kiểm tra thay đổi giữa hai phiên bản

Khi đã có nhãn đúng cùng scores cũ và mới, công cụ regression trả lời việc cập nhật có làm đổi tập đối tượng được chọn tại những mức yêu cầu precision nào. Công cụ này là chức năng nghiên cứu tùy chọn, không bắt buộc để xem nhiệt độ hoặc chạy một model.

| Công việc | Đầu vào | Đầu ra chính |
|---|---|---|
| Phân tích sensor | Thời gian, nhiệt độ, ID chuỗi hoặc lô | Biểu đồ, thống kê, cảnh báo quan sát |
| Dự báo | Lịch sử sensor theo giờ, đầy đủ theo model | p_cal, threshold, status, alert |
| FEFO | Sản phẩm, lô, hạn dùng | Dense rank riêng từng sản phẩm |
| Workflow | Thông tin lô và quyết định của vai trò | Trạng thái, ghi chú, audit JSON |
| Regression | ID, nhãn, scores hai phiên bản | Verdict, PSC, cells, witness, certificate |

**Phạm vi thực tế:** app chưa tự thu telemetry trực tiếp từ thiết bị, chưa huấn luyện lại model khi upload và chưa tự xác nhận chất lượng hàng. Dữ liệu lịch sử hoặc UI demo có thể được dùng khi chưa có upload; banner nguồn giúp phân biệt.

<!-- PAGE -->
# 2 Mở app và chọn vai trò

1. Mở thư mục ColdChain UI và chạy start_ui.bat. Launcher gọi start_ui.py để phục vụ giao diện, API kiểm chứng local và proxy đến backend model.
2. Mở địa chỉ launcher in ra, thường là http://127.0.0.1:8000. Nếu cổng bận, launcher thử cổng khác.
3. Chọn Enter system. Ở màn đăng nhập, chọn QA Manager hoặc Warehouse Staff, bấm Use demo user rồi Sign in.
4. Khi vừa cập nhật mã, khởi động lại launcher nếu cần và dùng Ctrl + F5 để tránh giao diện cũ từ cache.

| Thành phần đăng nhập | Làm gì | Kết quả |
|---|---|---|
| Role | Chọn góc nhìn QA hoặc Warehouse | Menu và thao tác theo vai trò |
| Use demo user | Điền thông tin demo cho vai trò | Có thể vào bản demo mà không cần tài khoản thật |
| Sign in | Mở workspace đã chọn | Hiển thị Dashboard hoặc Dispatch Board |
| Show password | Đổi cách hiển thị ô mật khẩu | Không đổi mật khẩu |
| Forgot password | Giải thích đây là demo | Không gửi email khôi phục |
| Log out | Trở lại màn chọn vai trò | Nguồn upload và workflow vẫn còn trong cùng phiên tab |

Không mở index.html trực tiếp để thay cho launcher. Web Worker, fetch file mẫu và API local cần được phục vụ qua HTTP. Static hosting cũng không tự chạy được checker Python.

## Đổi vai trò để kiểm tra đồng bộ

QA ghi quyết định rồi Log out, chọn Warehouse Staff và Sign in trong chính tab đó. Warehouse thấy cùng nguồn dữ liệu và trạng thái. Làm ngược lại để QA xem lô đã In queue hoặc Dispatched.

Đăng nhập hiện là demo phía giao diện. Các guard trong workflow kiểm tra thao tác đúng vai trò nhưng không thay thế xác thực, phân quyền và lưu trữ của một hệ thống server hoàn chỉnh. Không nhập mật khẩu thật vào bản demo.

<!-- PAGE -->
# 3 Hai vai trò và cấu trúc menu

## QA Manager

QA có Dashboard, Batches, Alerts, Reports, Simulation và Settings. Vai trò này phân tích dữ liệu, chạy model hoặc checker, xem cảnh báo và quyết định duyệt hoặc từ chối lô. QA không thực hiện bước Dispatched thay Warehouse trong workflow hiện tại.

## Warehouse Staff

Warehouse giữ đúng bốn tab: **Dispatch Board, Batches, Alerts, Settings**. Dispatch Board là nơi chuẩn bị hàng chờ và xác nhận xuất. Batches là nơi tra cứu toàn bộ lô. Warehouse không có thêm Reports hoặc Simulation trong sidebar; dataset được QA upload vẫn dùng chung khi đổi sang Warehouse.

| Công việc | QA Manager | Warehouse Staff |
|---|---|---|
| Xem cùng nguồn dữ liệu và trạng thái lô | Có | Có |
| Upload và chạy phân tích trong Simulation | Có | Không có tab này |
| Approve và Reject | Có | Không |
| Request QA review cho lô chờ duyệt | Xem yêu cầu | Ghi yêu cầu |
| Add to Queue và Confirm Dispatch | Không | Có khi đúng trạng thái và thứ tự FEFO |
| Acknowledge Alert | Có | Chỉ xem trạng thái QA |
| Xem chi tiết và lịch sử sensor có sẵn | Có | Có |
| Tải workflow audit trong Batches | Có | Có |

## Dispatch Board khác Batches ở đâu

Dispatch Board chia thẻ thành Dispatch queue, Ready to queue và Waiting for QA để tập trung vào việc cần làm tiếp. Completed and rejected batches nằm trong vùng thu gọn.

Batches dùng một bảng gồm toàn bộ inventory, có tìm kiếm và lọc. Hàng trong bảng không lặp lại các nút dispatch của board. View details vẫn mở được hồ sơ và các thao tác hợp lệ của vai trò.

Hai màn là hai cách nhìn trên cùng trạng thái; chuyển lô sang In queue ở board thì Batches cũng hiển thị In queue.

<!-- PAGE -->
# 4 App lấy dữ liệu từ đâu

| Nguồn | Cách nhận biết | Cách sử dụng |
|---|---|---|
| Historical dataset | Nhãn nguồn lịch sử ở thanh trên | Dữ liệu snapshot được lấy qua API; không phải tín hiệu trực tiếp |
| UI demo | API offline hoặc nhãn demo | Minh họa giao diện khi API không có dữ liệu |
| Uploaded dataset | Banner ghi tên file và số dòng | Nguồn sensor hoặc inventory người dùng đã tải |

Khi upload sensor hoặc inventory hợp lệ, app thay nguồn hoạt động cho các màn tương ứng. Polling lịch sử được tạm dừng để không ghi đè lên upload. Dashboard, Batches, Alerts, workflow và Reports của QA đều đọc nguồn chung này; Dispatch Board của Warehouse cũng vậy.

**Mỗi lần upload sensor hoặc inventory là thay nguồn trước, không nối thêm.** Upload inventory sau sensor không tự ghép hai bảng thành một cơ sở dữ liệu. Vì thế, nếu chỉ có inventory thì nhiệt độ và dự báo có thể không có; nếu chỉ có sensor thì sản phẩm, vị trí và hạn dùng có thể không có.

Regression CSV là ngoại lệ: nó chỉ cấp dữ liệu cho phần kiểm chứng, không thay inventory hoặc sensor đang hoạt động trên toàn app. Khi xem regression trong Simulation, banner vẫn có thể ghi tên dataset vận hành trước đó.

## Banner nguồn upload

- Uploaded dataset ghi tên file; rows và kind cho biết kích thước cùng loại dữ liệu đã nhận dạng.
- Progress thông báo đang chạy batch nào, số batch thành công hoặc lỗi, hay đang chờ xác nhận lịch sử đầy đủ.
- Run models for all batches chạy lại dự báo cho sensor. Cancel model run dừng việc áp dụng các kết quả tiếp theo; các kết quả đã hoàn thành có thể được giữ.
- Return to historical/demo data bỏ nguồn upload và trở về nguồn trước. Workflow của nguồn upload không được giữ để áp sang nguồn khác.

Upload và workflow nằm trong bộ nhớ của tab. Đổi vai trò không làm mất chúng; reload, đóng tab hoặc đổi dataset sẽ làm mất hoặc khởi tạo lại trạng thái tương ứng. Chưa có đồng bộ nhiều máy hoặc nhiều tab. Hãy tải JSON cần giữ trước khi kết thúc phiên.

<!-- PAGE -->
# 5 Ba loại dataset và các cột cần có

## Sensor CSV hoặc TSV

Mỗi dòng là một lần đo. Schema dễ dùng là Batch_ID, Timestamp, calibrated_temp, Humidity, Shipment_Mode. Cột nhiệt độ cũng nhận actual_temp, Temperature hoặc temp theo thứ tự ưu tiên của parser. Nếu có cả calibrated_temp và Temperature, cột calibrated_temp được ưu tiên.

```csv
Batch_ID,Timestamp,calibrated_temp,Humidity,Shipment_Mode
LOT-A,2026-01-01 00:00:00,5.0,60,Air
LOT-A,2026-01-01 01:00:00,5.2,62,Air
```

Thời gian được sắp theo từng Batch_ID. Timestamp trùng trong cùng lô bị từ chối. Nếu thiếu Batch_ID, app dùng UPLOADED-BATCH và cảnh báo. Humidity hoặc Shipment_Mode thiếu có thể dùng giá trị từ import form; đây là giá trị người dùng bổ sung, không tự thành quan sát thật.

## Inventory CSV

```csv
Product_ID,Product_Name,Batch_ID,Dynamic_Expiry_Date
P001,Product A,LOT-A,2027-01-01
P001,Product A,LOT-B,2027-01-02
```

Cần Product_ID, Batch_ID, Dynamic_Expiry_Date. Mỗi cặp sản phẩm và lô chỉ có một dòng. Product_Name là tùy chọn. App tính lại FEFO rank từ hạn dùng được cung cấp, không lấy một cột status từ file để coi là đã được QA duyệt.

## Regression CSV

```csv
id,y,old_score,new_score
obs-A,1,0.9,0.1
obs-B,0,0.5,0.5
```

ID phải duy nhất, y là 0 hoặc 1, scores hữu hạn. Đây là cùng các quan sát được chấm bởi hai phiên bản. Nếu có new_id thì phải khớp ID và thứ tự của id. Scores không bắt buộc là xác suất trong [0,1]; yêu cầu quan trọng là đúng thứ tự và ý nghĩa của score cho việc chọn ngưỡng.

File upload tối đa 75 MiB và 500.000 dòng. Regression giới hạn 2.000 quan sát. Parser hỗ trợ dấu phẩy, chấm phẩy, tab, BOM, ô trống và trường có dấu nháy; số bắt buộc bị thiếu sẽ báo lỗi thay vì biến thành 0.

<!-- PAGE -->
# 6 Dashboard của QA Manager

## Khi dùng dữ liệu lịch sử

Dashboard cung cấp tổng quan số lô, cảnh báo và tình trạng nhiệt. Review mở lô cần xem; View all batches chuyển sang bảng lô. Biểu đồ có dữ liệu thật khi sensor API trả được lịch sử; các hình minh họa của chế độ demo không nên được đọc như quan sát mới.

| Chỉ số | Cách hiểu theo mã hiện tại |
|---|---|
| Active Batches | Số lô không thuộc Dispatched hoặc Rejected theo trạng thái workflow |
| Current Excursions | Số lô active được phân loại High do nhiệt độ hoặc trạng thái excursion từ nguồn |
| Open Alerts | Số bản ghi cảnh báo chưa mang trạng thái Resolved; một lô có thể có nhiều bản ghi |
| Awaiting Approval | Số lô đang chờ QA duyệt |
| Thermal Status | Phân nhóm excursion, early warning, no early alert từ snapshot; không phải điểm chất lượng tổng hợp |
| Shelf life hoặc Remaining Days | Giá trị do nguồn lịch sử cung cấp; upload sensor không tự tính được giá trị tương đương |

## Khi dùng dataset upload

Dashboard chuyển sang Uploaded dataset overview. Phần QA batch decisions cho phép Review batch hoặc View details. Bên dưới là thống kê nguồn mới, bảng quan sát hoặc FEFO và Batch history and model results nếu có sensor.

| Chỉ số upload | Ý nghĩa |
|---|---|
| Batches / inventory rows | Số chuỗi sensor khác ID, hoặc số dòng inventory |
| Input rows | Số dòng dữ liệu sau chuẩn hóa; Nepal là số giờ sau tổng hợp |
| Latest reading excursions | Số chuỗi có lần đo cuối dưới 2°C hoặc trên 8°C |
| Active alerts | Tổng cảnh báo quan sát và cảnh báo các task model có alert bật |

Màu High của upload sensor phản ánh lần đo cuối ngoài vùng. Khi nhiệt độ trong vùng, phân loại nền có thể vẫn là Unknown; không tự đổi thành Low chỉ vì chưa có cảnh báo. Inventory không có sensor cũng dùng Unknown. Kết quả model được xem riêng trong bảng task và Alerts.

Không có model Quality Risk Score tổng hợp được tích hợp trong nhánh này. Dấu gạch ngang hoặc N/A ở risk score là thiếu chỉ số đó, không phải rủi ro bằng 0.

<!-- PAGE -->
# 7 Dispatch Board của Warehouse Staff

Mục đích của board là trả lời lô nào có thể chuẩn bị xuất và việc tiếp theo là gì. Board dùng thẻ để thao tác, khác bảng tra cứu Batches. Nguồn dữ liệu và quyết định QA giống nhau ở cả hai vai trò.

| Nhóm trên board | Lô nào xuất hiện | Việc có thể làm |
|---|---|---|
| Dispatch queue | In queue | Xem chi tiết, mở bước Confirm Dispatch |
| Ready to queue | Approved | Xem chi tiết, mở bước Add to Queue |
| Waiting for QA | Awaiting approval | Xem chi tiết, Request QA review |
| Completed and rejected batches | Dispatched hoặc Rejected | Mở vùng thu gọn để xem lại hồ sơ |

Các ô tổng Ready to queue, In queue và Dispatched là số lô đang ở mỗi trạng thái. Đây là số lượng workflow, không phải số model đã chạy hay số cảnh báo.

## Những nút quan trọng

**View details** mở hồ sơ đúng lô. **Request QA review** ghi một yêu cầu trong workflow để QA thấy ở dữ liệu chung; không gửi email hoặc tin nhắn ra ngoài. Sau khi ghi, nút chuyển thành QA review requested để tránh tạo yêu cầu lặp.

**Add to Queue** trước hết mở hồ sơ lô. Trong hồ sơ, chọn Add to Queue rồi Confirm action để đổi từ Approved sang In queue. **Confirm Dispatch** cũng mở hồ sơ; chọn hành động và Confirm action để ghi Dispatched. Nút trên thẻ không bỏ qua bước xác nhận.

**Cancel** đóng bước xác nhận mà không đổi trạng thái. Đóng hồ sơ cũng không tự thực hiện thao tác. Trước khi xác nhận, app kiểm tra lại vai trò, trạng thái hiện tại và FEFO; một cửa sổ mở từ trước không được dùng để bỏ qua quyết định QA mới.

Nếu lô có thứ hạng sau một lô Approved hoặc In queue sớm hơn cùng Product_ID, nút thao tác sẽ bị khóa và ghi FEFO process…first. Lô thiếu hạn dùng hoặc sản phẩm không được gán một rank giả. Warehouse không có quyền tự Approve lô đang chờ hoặc xuất lô Rejected.

<!-- PAGE -->
# 8 Batches và hồ sơ chi tiết lô

## Bảng tra cứu Batches

Batches phục vụ tìm lô theo ID hoặc sản phẩm, lọc Workflow status và xem toàn bộ inventory. Với Warehouse, màn này dùng bảng, không lặp board thẻ hay các nút dispatch theo từng hàng. Clear filters bỏ điều kiện tìm kiếm và lọc; Show 50 more tăng số hàng hiển thị.

| Cột | Giải thích |
|---|---|
| Batch | ID lô hoặc ID chuỗi logger được quy ước lúc import |
| Product | Tên hoặc mã sản phẩm nếu nguồn có cung cấp |
| FEFO rank | Hạng hạn dùng trong cùng sản phẩm; nhỏ hơn được ưu tiên |
| Current temperature | Lần đo mới nhất của chuỗi; inventory đơn thuần có thể N/A |
| Workflow status | Trạng thái QA và Warehouse dùng chung |
| Dynamic expiry | Hạn dùng đầu vào, chưa được tự suy từ nhiệt độ upload |
| Location | Vị trí nếu mô hình dữ liệu của nguồn đã cung cấp; có thể Not supplied |
| Action | View details; QA có thể thấy Review batch cho lô chờ |

## View details mở những gì

Hồ sơ hiển thị ID, sản phẩm, trạng thái, nhiệt độ, rank, hạn dùng, thời điểm đo, số lượng hoặc vị trí nếu có. Last decision nêu vai trò, thời điểm và ghi chú quyết định. Batch workflow audit cho xem các bước đã ghi cho lô đó.

Với sensor upload, View uploaded sensor history mở lịch sử; preview JSON gồm 30 dòng cuối và Download full sensor history JSON lấy toàn bộ chuỗi. Với nguồn saved, app gọi sensor API và cho xem lịch sử trả về. API lỗi hoặc không có readings sẽ được báo, không dùng đường nhiệt độ mẫu thay thế.

Hồ sơ mở Approve/Reject cho QA theo trạng thái hợp lệ; Add to Queue/Confirm Dispatch cho Warehouse theo điều kiện hợp lệ. Close hoặc Escape đóng hồ sơ; khi đang ở bước xác nhận, Escape hủy bước xác nhận trước.

N/A và Not supplied nghĩa là chưa có dữ liệu dùng được. Chúng không có nghĩa là không có rủi ro, không có tồn kho hay không cần kiểm tra lô.

<!-- PAGE -->
# 9 Trạng thái và luồng duyệt xuất

Luồng thông thường là Awaiting approval → Approved → In queue → Dispatched. Reject là quyết định giữ lô không cho tiếp tục qua luồng xuất. Model không tự chuyển bất kỳ lô nào sang Approved.

| Trạng thái hiện tại | Vai trò | Hành động | Kết quả |
|---|---|---|---|
| Awaiting approval | QA | Approve rồi Confirm action | Approved |
| Awaiting approval | QA | Reject và nhập lý do | Rejected |
| Approved | Warehouse | Add to Queue và xác nhận | In queue |
| In queue | Warehouse | Confirm Dispatch và xác nhận | Dispatched |
| Approved hoặc In queue | QA | Reject và nhập lý do | Rejected |
| Awaiting approval | Warehouse | Request QA review | Giữ trạng thái, thêm yêu cầu review |

Reject bắt buộc có Decision note. Approve một lô được gắn risk High cũng cần ghi chú đánh giá. Đây là yêu cầu ghi nhận quyết định, không phải chứng minh lô đạt chất lượng chỉ nhờ có ghi chú.

Warehouse không thể chuyển Awaiting approval thẳng sang In queue. QA không thể thực hiện Dispatched. Lô đã Dispatched không có thao tác hoàn tác trong workflow hiện tại. Muốn thử lại từ đầu, dùng một nguồn thử nghiệm mới hoặc một phiên mới, thay vì coi app đã hỗ trợ nghiệp vụ hoàn hàng.

## Audit ghi những gì

Mỗi hành động ghi sequence, time, batch_id, batch_key, role, action, note, from và to. Thời gian ở audit là ISO theo UTC; nó khác thời gian sensor vốn có thể là giờ địa phương. Không so trực tiếp hai chuỗi giờ nếu chưa quy về cùng múi giờ.

Download workflow audit JSON xuất các lô, trạng thái và quyết định hiện tại cùng chuỗi hành động. Với inventory có Batch_ID trùng ở hai sản phẩm khác nhau, workflow dùng khóa ghép sản phẩm và lô để không gán nhầm quyết định.

Đổi vai trò và model refresh giữ quyết định của cùng nguồn. Đổi dataset reset workflow. Audit này là bản ghi trong bộ nhớ phiên, chưa có chữ ký số, cơ chế bất biến hay đồng bộ cơ sở dữ liệu kho.

<!-- PAGE -->
# 10 Alerts và cách xử lý cảnh báo

Alerts giúp xác định cần xem lô nào và vì sao. Với upload sensor, app tạo cảnh báo từ hai nguồn riêng. Không có sensor thì inventory đơn thuần không tạo cảnh báo nhiệt độ.

| Loại | Điều kiện tạo | Mức hiển thị |
|---|---|---|
| Observed excursion | Lần đo cuối của chuỗi nhỏ hơn 2°C hoặc lớn hơn 8°C | Critical |
| Model alert | Một task dự báo trả alert=true hoặc 1 | Warning |

Observed excursion là quan sát đã xảy ra ở điểm cuối. Model alert là kết quả cảnh báo cho cửa sổ tương lai. Một lô có thể có cảnh báo của nhiều task và đồng thời có cảnh báo quan sát; số alert vì vậy không bằng số lô.

## Cách sử dụng

1. Mở Alerts, chọn Alert severity để lọc All severities, Critical hoặc Warning.
2. Đọc Batch, Type, Severity, Observed at và Details. Với model, xem task, p_cal, threshold và status đi kèm.
3. Chọn View batch details để đối chiếu hồ sơ và sensor thực có.
4. QA có thể bấm Acknowledge Alert. Warehouse chỉ xem trạng thái xác nhận của QA và thông tin lô.

**Acknowledge** nghĩa là đã tiếp nhận/xem cảnh báo. Nó không tự làm nhiệt độ trở lại bình thường, không tự resolve alert, không duyệt lô và không xuất kho. Các số Active alerts hoặc Open Alerts vẫn có thể giữ nguyên sau acknowledgement vì bản ghi vẫn còn là cảnh báo.

Nếu cảnh báo mất sau khi thay dataset hoặc đầu vào, cần xem lại nguồn và thời điểm đo. Danh sách upload hiện tập trung vào điểm cuối mỗi chuỗi và kết quả model đang lưu, không phải cơ sở dữ liệu đầy đủ mọi episode trong quá khứ.

No active alerts không chứng minh model đã chạy thành công. Có thể chỉ có inventory, chưa xác nhận lịch sử, model lỗi hoặc không task nào trả alert. Kiểm tra progress và lỗi từng batch trước khi kết luận.

<!-- PAGE -->
# 11 Simulation và các nút nhập dữ liệu

Simulation của QA mở Dataset & Research Workbench. Đây là điểm nhập dữ liệu ngoài, chạy thử dự báo một lô hoặc nhiều lô, và thực hiện kiểm chứng tùy chọn. Warehouse không có tab này trong menu bốn tab.

## Mục 1 Upload your dataset

Select a CSV/TSV file hoặc kéo thả một file. Sensor sample, FEFO sample và Regression sample là nút dùng thử, không giới hạn việc chọn dataset riêng. File hợp lệ được phân loại sensor, inventory hoặc regression và hiển thị tên, số dòng, cảnh báo.

Automatically run backend models… mặc định bật. Muốn tự chạy sau upload sensor, bạn còn phải xác nhận trước upload rằng tất cả chuỗi chứa lịch sử đầy đủ. Nếu chưa xác nhận, app tính thống kê local và cập nhật toàn app nhưng chờ chạy model. Bạn cũng có thể xác nhận trong banner rồi Run models for all batches.

| Import option | Tác dụng |
|---|---|
| Shipment_Mode default if missing | Điền giá trị thiếu từ form, mặc định Air, kèm cảnh báo |
| Humidity default if missing | Điền giá trị thiếu, mặc định 60%, kèm cảnh báo |
| Apply Temperature offset | Chỉ với cột Temperature và offset có trong CSV, áp dụng hiệu chỉnh được chọn |
| Reload file with current options | Đọc lại chính file bằng cấu hình form mới |

EQUATION: Temperature_adjusted = Temperature × (1 − Calibration_Offset_Pct / 100)

Hiệu chỉnh không tự áp cho calibrated_temp hoặc actual_temp. Đổi tên cột thành calibrated_temp không tạo bằng chứng rằng thiết bị đã được hiệu chuẩn theo model.

## Mục 2 Process your dataset

Khi chưa có dữ liệu, mục này hiện hướng dẫn. Với sensor, nó trở thành vùng chọn batch, cursor, biểu đồ và inference. Với inventory, nó là bảng FEFO. Với regression, nó hướng dẫn tiếp tục xuống mục 3; vì thế thứ tự 1, 2, 3 vẫn được giữ.

## Mục 3 Exact Policy Regression Diagnosis

Đây là nhánh riêng cần labels và cặp scores. Sensor CSV chỉ có nhiệt độ không đủ để chạy nhánh này. Không cần dùng nó cho một lượt dự báo thông thường.

<!-- PAGE -->
# 12 Chạy sensor và đọc kết quả model

## Chạy toàn bộ batch và chạy thử một batch

Run models for all batches gửi lần lượt lịch sử từng batch, chạy đủ w1_6, w1_12 và w1_24, lưu kết quả vào nguồn chung cho Dashboard và Alerts. Lịch sử phải theo giờ liên tục, không vượt 100.000 readings mỗi batch, thời gian phù hợp API và có xác nhận đầy đủ. Giới hạn JSON của proxy local là 20 MiB nên một request cũng có thể chạm giới hạn dung lượng trước giới hạn dòng.

Trong Simulation, Batch chọn một lô; Position chọn thời điểm đang xét. Backend forecast horizon chọn 6, 12 hoặc 24 giờ. Run backend inference chỉ gửi lịch sử từ đầu chuỗi đến cursor của lô đó. Kết quả của lần chạy thủ công hiển thị tại Simulation, không tự ghi đè tập kết quả chạy toàn bộ trên Dashboard.

What if adjustment thay đổi nhiệt độ ở điểm cuối cho lần thử thủ công, trong khoảng −30 đến 30°C. File nguồn không đổi. Các thống kê min/max và số điểm ngoài vùng của CSV vẫn tính từ chuỗi nguồn, còn nhiệt độ tại cursor và Arrhenius dùng nhiệt độ đang thử. JSON request ghi mức điều chỉnh để tránh nhầm với dữ liệu quan sát.

## Mô hình đang dự báo điều gì

Theo model card kế thừa, tác vụ là dự báo một đợt ngoài vùng nhiệt liên tiếp ít nhất 3 giờ bắt đầu trong t+1 đến t+W khi thời điểm gốc đang normal. Spike 1–2 giờ không phải cùng biến đích. Đó không phải dự báo chính xác nhiệt độ ở t+W.

Cửa sổ 24 giờ nghĩa là xét sự kiện bắt đầu ở bất kỳ thời điểm nào trong khoảng tương lai đó, không có nghĩa mọi sự kiện đều được báo trước đủ 24 giờ. Cửa sổ dự báo và số giờ báo sớm thực tế là hai đại lượng khác nhau.

Backend đã kiểm tra trả model t_only, version FINAL-1.0 và các cửa sổ 6/12/24 giờ. Model card cũ còn mô tả biến thể thermal; không suy rằng nhãn model cũ và backend đang deploy có cùng weights. Tên thật của lần chạy nằm trong response.

Backend dùng các đặc trưng tích lũy và từ chối lịch sử được khai báo không đầy đủ. Đừng bật xác nhận chỉ để vượt lỗi nếu dữ liệu thực tế là một đoạn cắt. Có thể tiếp tục xem thống kê mà chưa chạy model.

Lỗi từng batch được lưu riêng. Batch lỗi không được tạo p_cal thay thế hoặc coi là an toàn. Cancel không thể thu hồi dữ liệu của request đã gửi đến backend; nó ngăn app tiếp tục áp dụng kết quả của lượt chạy đã hủy.

<!-- PAGE -->
# 13 Ý nghĩa các chỉ số nhiệt độ và dự báo

| Chỉ số hoặc trường | Cách đọc | Điều không thể suy ra |
|---|---|---|
| Temperature at cursor | Nhiệt độ ở vị trí chọn, có thể gồm điều chỉnh thử | Không phải nhiệt độ được dự báo |
| Latest temperature | Điểm cuối của chuỗi đang dùng | Không mô tả mọi thời điểm trong lô |
| Min và Max | Cực trị trên chuỗi lô sau chuẩn hóa | Không tự là thời lượng vượt ngưỡng |
| Readings outside [2,8]°C | Đếm điểm có nhiệt độ dưới 2 hoặc trên 8 | Không tự bằng số giờ hay số episode |
| p_raw | Điểm trước hiệu chỉnh do API trả, nếu có trong JSON | Không đồng nhất với p_cal |
| p_cal | Điểm xác suất sau hiệu chỉnh do backend trả cho task | Không là phần trăm hàng đã hỏng |
| Threshold | Ngưỡng của task và operating point | Không phải ngưỡng nhiệt độ 2/8°C |
| alert | Quyết định cảnh báo do backend trả | false không bảo đảm không có sự cố |
| Model và version | Định danh backend tự báo trong response | Không thay cho việc đối chiếu hash weights |

Ví dụ minh họa: p_cal=0,12 và threshold=0,08 cho thấy điểm cao hơn ngưỡng cấu hình. Khi đọc quyết định cuối cùng hãy xem trường alert mà API trả, vì backend còn xử lý trạng thái tại thời điểm gốc.

p_cal=0,12 có thể đọc là mức xác suất ước lượng 12% cho biến cố mục tiêu của task theo model, chưa phải tần suất đã xác nhận trên dataset mới. Calibration ở đây là hiệu chỉnh thang xác suất, khác việc hiệu chỉnh nhiệt độ sensor hoặc áp dụng Calibration_Offset_Pct.

**NORMAL_ORIGIN** nghĩa là điểm gốc thuộc điều kiện normal của model. **ALREADY_EXCURSION** nghĩa là đã ở ngoài vùng tại điểm gốc; early warning có thể không áp dụng nên p_cal hoặc threshold có thể null. Null không được đổi thành xác suất 0. Các trạng thái khác nếu API trả cần đọc cùng detail, không tự ép thành normal.

**precision50** là operating point của model. Nó không phải p_cal=0,5, không buộc threshold luôn bằng 0,5 và không bảo đảm precision đạt 50% trên dataset mới. Các task có thể có ngưỡng khác nhau.

Precision là số cảnh báo đúng chia số cảnh báo đã phát; recall là số sự kiện dương được phát hiện chia tổng sự kiện dương theo định nghĩa đánh giá. Muốn tính thực tế trên Nepal cần nhãn đúng và quy trình đánh giá riêng. App hiện không tự tính accuracy, precision, recall hay ROC AUC từ việc upload sensor.

Hai điểm 2°C và 8°C thuộc vùng normal trong logic hiện tại; chỉ nhỏ hơn 2 hoặc lớn hơn 8 mới ngoài vùng. Chu kỳ đo không đều làm việc đổi số điểm sang thời lượng trở nên không hợp lệ.

<!-- PAGE -->
# 14 Arrhenius và FEFO dùng để làm gì

## Arrhenius ratio

Arrhenius ratio là phép tính mô tả tốc độ theo nhiệt độ tại cursor, lấy 5°C làm tham chiếu. App dùng Ea=51.044,8 J/mol và R≈8,31446 J mỗi mol mỗi Kelvin; nhiệt độ phải đổi sang Kelvin.

EQUATION: r(T) = exp[(Ea / R) × (1 / Tref − 1 / T)]

Trong đó Tref=278,15 K và T=Temperature°C+273,15. Ở 5°C, ratio bằng 1×; cao hơn 1× nghĩa là tốc độ theo công thức cao hơn tham chiếu. Ratio 2× không có nghĩa đã mất 50% chất lượng, cũng không có nghĩa còn đúng một nửa hạn dùng.

Đây là bộ tham số mô tả cố định, chưa phải mô hình động học đã xác thực riêng cho từng sản phẩm. Nhánh upload không tự tích phân ratio để suy hạn dùng mới. Runtime chặn số mũ ở biên ±50 để tránh giá trị tính toán quá lớn; không diễn giải vùng cực đoan này như hiệu lực vật lý được chứng minh.

## FEFO rank

FEFO là First Expired First Out. App nhóm theo Product_ID và sắp Dynamic_Expiry_Date tăng dần. Nó dùng dense rank: cùng hạn dùng thì cùng rank, hạng sau tăng một đơn vị, không nhảy số do hòa hạng.

| Sản phẩm | Lô | Dynamic expiry | Rank |
|---|---|---|---|
| P001 | A | 01/01/2027 | 1 |
| P001 | B | 01/01/2027 | 1 |
| P001 | C | 05/01/2027 | 2 |
| P002 | D | 10/01/2027 | 1 |

Rank 1 của P001 không được so trực tiếp với rank 1 của P002 để kết luận lô nào xuất trước toàn kho. Guard workflow chỉ chặn bởi lô cùng sản phẩm, rank nhỏ hơn và đang Approved hoặc In queue; lô rank bằng nhau không chặn nhau. Lô chờ QA không được tự duyệt chỉ để giữ một thứ tự FEFO.

Dynamic expiry là hạn dùng đầu vào. Model alert không tự thay nó, và FEFO không tự tạo quyết định Approved. Với sensor đơn thuần, rank và hạn dùng có thể Unavailable.

<!-- PAGE -->
# 15 Dùng dữ liệu Nepal trên app

App nhận dạng trực tiếp một định dạng logger Nepal đã được kiểm tra: dòng ghi chú All Date Time values are in UTC +05:45, sau đó mỗi dòng có số thứ tự, ngày YYYY-MM-DD, giờ HH:mm:ss, nhiệt độ và ô trống cuối. Đây không phải bộ nhập chung cho mọi định dạng trong archive.

## Quy trình chuyển đổi đang có

1. Giải nén dataset và chọn một CSV logger. App hiện không nhận ZIP hoặc XLSX trực tiếp.
2. Ghép ngày và giờ, kiểm tra ngày, số nhiệt độ và timestamp trùng. Tạo ID chuỗi từ tên file; ID này chưa xác minh là một batch hàng thật.
3. Giữ đồng hồ địa phương Nepal UTC+05:45. Không tự đổi giờ địa phương thành UTC khi chưa có quy tắc tương thích model.
4. Mỗi giờ chỉ giữ khi có đủ sáu mẫu cách nhau 10 phút; tính nhiệt độ trung bình giờ. Giờ thiếu hoặc không đều bị loại, có số điểm loại trong cảnh báo. Không nội suy giờ thiếu.
5. Tính thống kê trên chuỗi sau tổng hợp; model chỉ chạy khi lịch sử phù hợp và được người dùng xác nhận đầy đủ.

Một file thật đã kiểm tra có 2.882 điểm, tạo 479 giờ đầy đủ, loại 8 điểm trong các bin không đủ điều kiện. Đây là số liệu của file kiểm tra đó, không phải kích thước toàn bộ dataset Nepal.

## Những điều cần đọc trong cảnh báo import

Hourly mean có thể che spike ngắn và làm min/max khác dữ liệu 10 phút gốc. Input rows, số readings ngoài vùng và các giá trị trên app sau import Nepal phản ánh dữ liệu đã tổng hợp. File gốc không bị sửa.

Humidity và Shipment_Mode thiếu có thể dùng mặc định 60/Air từ form. Đây là giả định, không phải số đo hoặc loại vận chuyển đã xác minh của Nepal. Cũng phải chọn đúng logger phản ánh vùng cần phân tích; một logger môi trường không tự trở thành nhiệt độ vaccine.

Backend trả được score không chứng minh model đã được đánh giá tốt trên Nepal. App vẫn dùng model hiện có, không tự huấn luyện lại. Nepal sensor chưa đủ để tạo FEFO nếu thiếu sản phẩm và hạn dùng, và chưa đủ cho regression nếu thiếu nhãn cùng cặp scores cũ/mới.

<!-- PAGE -->
# 16 Phép kiểm chứng regression là gì

Regression ở đây là thay đổi hành vi quyết định sau khi cập nhật phần mềm hoặc model; không phải thuật toán hồi quy tuyến tính. Câu hỏi là với cùng các quan sát và cùng nhãn, phiên bản cũ và mới có chọn đúng cùng các ID ở mọi policy đang xét hay không.

Ví dụ một phiên bản chọn A và B, phiên bản khác chọn A và C. Dù đều chọn hai đối tượng, tập ID đã đổi. Ngược lại, scores có thể thay đổi nhẹ mà tập được chọn ở mọi policy vẫn giữ nguyên.

## Các khái niệm đầu vào

**y** là nhãn đúng 0/1 của mỗi quan sát. Nhãn 1 là lớp mục tiêu cần phát hiện/chọn theo bài toán; app không tự biết đó là loại bệnh, sự cố hay lô hàng nếu người dùng chưa định nghĩa.

**old_score và new_score** là điểm hai phiên bản tạo cho cùng quan sát. Chúng được cấp từ bên ngoài; công cụ không tự tạo một model cũ để đối chứng với model đang chạy.

**Alpha** là yêu cầu precision của tập được chọn. Alpha khác threshold score. Khi alpha đổi, selector có thể chọn một ngưỡng score khác để đạt yêu cầu.

## Selector hoạt động thế nào

1. Sắp score giảm dần và giữ các điểm bằng nhau thành cùng nhóm ứng viên trong contract mặc định.
2. Với từng tập ứng viên, tính precision bằng TP chia N: TP là số nhãn 1 được chọn, N là số quan sát được chọn.
3. Giữ ứng viên thỏa precision ≥ alpha hoặc > alpha tùy contract.
4. Chọn ứng viên có TP lớn nhất; nếu hòa TP thì chọn N lớn nhất. Khi không có ứng viên hợp lệ, hoặc dữ liệu không có nhãn dương theo mã hiện tại, chọn tập rỗng.

Producer chia miền policy thành các vùng/điểm có trạng thái quyết định ổn định và tạo certificate. Independent checker dựng lại membership từ input để kiểm tra. Chỉ sau khi checker chấp nhận mới có EQUIVALENT hoặc DIVERGENT. Kết luận có điều kiện trên input và contract, không phải chứng minh mọi mã nguồn của một chương trình bất kỳ.

<!-- PAGE -->
# 17 Nhập policy và đọc kết quả kiểm chứng

Policy domain lo/hi xác định miền alpha, ví dụ [0,30; 0,90]. Nhập dạng chuỗi 0.30, 0.90 hoặc phân số 1/2; app dùng số hữu tỷ cho policy. Reference precision và Actual precision chọn inclusive ≥ hoặc strict >. Nếu precision đúng 0,8, ứng viên hợp lệ với ≥0,8 nhưng không hợp lệ với >0,8.

Compare and verify independently gọi producer rồi checker local. Recheck a downloaded certificate JSON chỉ chạy checker với input và certificate đã tải, không tạo lại certificate để thay thế bản đang kiểm tra.

| Kết quả hoặc chỉ số | Ý nghĩa |
|---|---|
| EQUIVALENT | Cùng tập ID tại mọi policy trong miền đã kiểm chứng |
| DIVERGENT | Có ít nhất một policy mà tập ID khác nhau |
| PSC exact | Tỷ lệ độ dài vùng phân kỳ trên độ dài toàn miền |
| Verified probes | Số điểm policy checker kiểm tra theo cấu trúc phân hoạch; không phải số quan sát |
| Candidate counts old/new | Số tập ứng viên của hai selector |
| Input SHA 256 | Dấu vân tay input; giúp phát hiện thay đổi, không chứng minh nguồn dữ liệu đúng |
| Cells | Các khoảng hoặc điểm với trạng thái old/new, equal và witness |
| Witness ID | Một quan sát có membership khác giữa hai phiên bản |

EQUATION: PSC = L_diff / (hi − lo)

Ví dụ minh họa: miền dài 0,60, vùng phân kỳ dài 0,12 thì PSC=0,20. Đó là 20% độ dài miền policy, không phải 20% dữ liệu dự đoán sai. Nếu chỉ phân kỳ tại một điểm đơn lẻ, độ dài bằng 0 nên PSC có thể bằng 0 mà vẫn DIVERGENT.

Trong cells, Lo/Hi là hai đầu; Left closed/Right closed cho biết có bao gồm đầu mút; Equal so sánh tập ID. Một điểm đơn có thể Lo=Hi và hai đầu đóng. Giao diện hiện 100 cells đầu, JSON chứa đầy đủ.

Allowed policy query có Finite set để hỏi vài alpha, Interval để hỏi mọi alpha trong một khoảng, Decimal lattice để hỏi lưới rời rạc theo số chữ số thập phân, hoặc No query. affected=true nghĩa phạm vi hỏi chứa policy phân kỳ. allowed_count và affected_count, nếu có, đếm policy trên tập/lưới được hỏi. full_query trả chi tiết; boolean_query trả tồn tại và witness. Không cộng các số này vào số lô hay số lỗi thực tế.

<!-- PAGE -->
# 18 Reports Settings và các file đầu ra

## Reports của QA

JSON là tệp văn bản có cấu trúc gồm tên trường và giá trị, phù hợp để kiểm tra chi tiết hoặc xử lý bằng mã. Nó không tự là một báo cáo PDF trình bày sẵn. Bạn có thể mở bằng trình soạn thảo văn bản; không cần chạy model lại chỉ để đọc tệp.

Với upload, Download dataset results JSON xuất tên nguồn, loại dữ liệu, số dòng, tóm tắt batch, alerts, phản hồi model, lỗi, import warnings và workflow decisions/audit. Khi cần trạng thái workflow mới nhất, đọc workflow.decisions; trường tóm tắt batch nền có thể vẫn ghi trạng thái khởi tạo.

Với nguồn lịch sử, màn report hiện dùng xuất session workflow audit, không tạo chứng chỉ tuân thủ hoặc một PDF chất lượng được xác thực. Warehouse không có Reports tab; Download workflow audit JSON nằm trong Batches.

| File tải xuống | Dùng để làm gì |
|---|---|
| uploaded dataset results JSON | Giữ kết quả phân tích, dự báo, lỗi và workflow của nguồn upload |
| warehouse workflow audit JSON | Theo dõi quyết định và thứ tự thao tác trong phiên |
| sensor history JSON | Lưu chuỗi đo đầy đủ của lô được xem |
| inference result JSON | Giữ phản hồi và request của lần inference thủ công |
| verified policy certificate JSON | Mang input và certificate đi kiểm tra lại |

## Settings của hai vai trò

Account Profile hiển thị hồ sơ demo. Display Language hiện là English để thống nhất giao diện. Notifications gồm New excursion alerts; Warehouse còn có Batch approved for dispatch, QA có Batches awaiting quality approval. Đây là điều khiển giao diện cục bộ; chưa thiết lập email/push thật hoặc thay backend cảnh báo.

Save changes trong Warehouse chỉ khả dụng khi có thay đổi và hết trạng thái Saving. Giá trị được ghi nhận trong component của màn, chưa lưu lâu dài lên server; rời màn hoặc reload có thể mất. Nút bị mờ khi không có thay đổi không phải một lỗi xử lý.

QA có Regulatory Temperature Limits hiển thị 2,0°C và 8,0°C cố định theo model dự án. Tên này không có nghĩa mọi loại hàng đều dùng chung ngưỡng phù hợp. Quality Risk Scoring Sensitivity với Decay rate, Anomaly, Excursion risk và Humidity variation là prototype. Low/Medium/High ở đây chưa đổi threshold model, rank FEFO hoặc tạo Quality Risk Score thật. Save/Reset của khối này chỉ tác động state demo của màn.

Không dùng thông báo Settings saved để suy rằng model đã được retrain, cấu hình server đã đổi hoặc cảnh báo cũ đã được resolve.

<!-- PAGE -->
# 19 Thực hành trọn luồng và xử lý lỗi

## Thử phân tích sensor và dự báo

QA mở Simulation, chọn Sensor sample hoặc file riêng. Nếu chỉ cần thống kê, tắt auto inference hoặc chưa xác nhận lịch sử. Kiểm tra tên nguồn, batch, min/max, số điểm ngoài vùng và biểu đồ. Nếu lịch sử thực sự đầy đủ, xác nhận rồi chạy model; xem progress và kết quả từng task trên Dashboard. Không lấy một request lỗi làm kết quả âm tính.

## Thử duyệt lô và xuất kho

QA upload inventory có sản phẩm/hạn dùng. Vào Dashboard hoặc Batches, mở View details, chọn Approve và Confirm action. Log out rồi đăng nhập Warehouse trong cùng tab. Dispatch Board hiện lô trong Ready to queue. Mở Add to Queue, xác nhận, sau đó Confirm Dispatch và xác nhận. Chuyển lại QA để xem Dispatched trong Batches. Tải audit trước khi reload.

| Dấu hiệu | Nguyên nhân cần kiểm tra | Việc nên làm |
|---|---|---|
| Run models bị mờ | Chưa xác nhận lịch sử hoặc lượt chạy còn bận | Đọc progress; chỉ xác nhận khi đúng dữ liệu |
| Partial tail hoặc complete history | Model cần đặc trưng tích lũy từ lịch sử đầy đủ | Cấp lịch sử đúng; không chỉ bật cờ để vượt lỗi |
| Consecutive hourly readings | Thiếu giờ hoặc chu kỳ đo không phù hợp | Chuẩn hóa có quy tắc; app không tự nội suy |
| Timestamp timezone | API yêu cầu source local không timezone | Chọn chuyển UTC cho lượt thủ công hoặc chuẩn hóa đúng timezone model |
| CSV header hoặc missing column | File chưa đúng schema | Kiểm tra mục 5; Nepal chỉ hỗ trợ định dạng đã mô tả |
| FEFO process another batch first | Có lô hợp lệ sớm hạn hơn cùng sản phẩm | Xử lý lô được chỉ ra trước |
| Không có Add to Queue | Chưa Approved, bị Rejected hoặc đã Dispatched | Xem workflow status và quyết định QA |
| Không có p_cal | Chưa chạy, API lỗi hoặc task không áp dụng | Xem status và errors, không thay bằng 0 |
| Regression button bị mờ | Sai loại file, API local chưa có hoặc đang bận | Dùng regression CSV và launcher có NumPy |

Nếu giao diện vẫn cũ, Ctrl + F5 và kiểm tra đúng địa chỉ launcher. Nếu mất dữ liệu sau reload, đó là giới hạn lưu trong phiên hiện tại; chỉ các file JSON bạn đã tải mới được giữ riêng.

<!-- PAGE -->
# 20 Phạm vi hiện tại và nguồn đối chiếu

## Chức năng đang có

App có parser CSV/TSV chạy trong worker, phân tích sensor, FEFO từ inventory, nhập một định dạng Nepal, gọi inference backend, nguồn upload dùng chung, workflow QA/Warehouse có guard, alert acknowledgement, xuất JSON và kiểm chứng policy bằng producer/checker độc lập.

Website online chưa tự cập nhật theo mọi thay đổi local. Tài liệu này mô tả bản mã trong ColdChain UI. Muốn online có checker cần triển khai API Python riêng phù hợp; static Netlify không tự chạy Python.

## Những việc chưa nên coi là đã có

Chưa có xác thực/phân quyền server hoàn chỉnh, cơ sở dữ liệu workflow, đồng bộ nhiều tab/máy, xuất kho thật, lưu upload sau reload, ghép nhiều file sensor và inventory, huấn luyện lại khi upload, đánh giá tự động chất lượng model trên Nepal, hoặc chứng nhận chất lượng hàng dựa vào p_cal/Arrhenius. Các cấu hình sensitivity còn là UI prototype.

## Tệp mã được dùng để đối chiếu

| Tệp trong ColdChain UI | Nội dung xác nhận |
|---|---|
| NETLIFY_DASHBOARD/coldchain-runtime.js | Parser, validation, Nepal, Arrhenius, timezone, FEFO |
| NETLIFY_DASHBOARD/coldchain-dataset.js | Nguồn upload, dự báo nhiều batch, metrics và report |
| NETLIFY_DASHBOARD/coldchain-workflow.js | Quyền thao tác, trạng thái, FEFO guards, board, hồ sơ và audit |
| NETLIFY_DASHBOARD/coldchain-workbench.js | Upload, inference thủ công và giao diện regression |
| NETLIFY_DASHBOARD/assets/index-BcV1nH7n.js | App shell, menu, đăng nhập, dashboard lịch sử, Settings |
| start_ui.py và backend/regression_service.py | Proxy model, API local và adapter checker |
| backend/engine/src/policy_exact.py | Selector contract, cells và PSC |
| backend/engine/policy_domain_query.py | Query hữu tỷ và đếm policy trong tập/lưới |

Định nghĩa biến đích dự báo tham chiếu model card kế thừa MODEL_CARD_source.md; tên model đang trả về cần đọc response của lần chạy cụ thể.

Bằng chứng local nằm tại outputs/COLDCHAIN_SYSTEM_FIX: four_tabs_checks.json kiểm tra menu và bố cục; warehouse_checks.json kiểm tra luồng hai vai trò; global_upload_checks.json kiểm tra nguồn upload; global_upload_live_backend.json ghi phản hồi model thật. Các kiểm thử browser có backend giả lập có kiểm soát được phân biệt với request backend thật, không phải dữ liệu hiệu năng triển khai.

<!-- PAGE -->
# Phụ lục giao diện Dispatch Board

Ảnh kiểm thử local dùng inventory minh họa, không phải dữ liệu sản xuất. Menu Warehouse chỉ có Dispatch Board, Batches, Alerts và Settings. Những thẻ ở Dispatch queue và Waiting for QA chỉ ra việc có thể làm tiếp; lô đã xuất hoặc bị từ chối nằm trong mục thu gọn phía dưới.

![Dispatch Board dạng thẻ](../../outputs/COLDCHAIN_SYSTEM_FIX/four_tabs_dispatch.png)

<!-- PAGE -->
# Phụ lục giao diện Batches

Ảnh kiểm thử dùng cùng nguồn inventory và trạng thái với ảnh Dispatch Board. Batches là bảng tra cứu, có tìm kiếm, lọc, hạn dùng, vị trí và View details. Trạng thái In queue giống nhau giữa hai màn nhưng cách trình bày và mục đích sử dụng khác nhau.

![Batches dạng bảng](../../outputs/COLDCHAIN_SYSTEM_FIX/four_tabs_batches.png)
