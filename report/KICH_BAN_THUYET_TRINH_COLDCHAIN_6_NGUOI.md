# Kịch bản thuyết trình và demo ColdChain cho 6 người

Bản cập nhật ngày 05/11/2026. Thời lượng khoảng 15–18 phút, gồm thời gian chờ kết quả. Lời thoại có thể đọc trực tiếp; phần Thao tác dành cho người điều khiển máy.

Luồng demo đã chốt: chọn sensor sample liên kết một lần → backend inference (tùy chọn) → dùng scores từ cùng sensor hoặc chạy hai XGBoost → kiểm chứng regression → FEFO cùng các lô → QA duyệt → kho xác nhận xuất. App không còn phần tính dynamic expiry từ sensor. FEFO dùng hạn có sẵn trong inventory.

## Chuẩn bị trước buổi trình bày

- Chạy ColdChain UI/start_ui.bat và dùng bản local. Đổi QA và Warehouse trong cùng một tab; không reload giữa phần duyệt và xuất.
- Vào QA Manager → Simulation, tắt Automatically run backend models trước khi chọn sensor sample để tránh tự chạy nhiều batch và nhiều horizon.
- Chạy thử một batch đủ lịch sử theo giờ. Ghi lại batch và Position dùng được cho backend; ưu tiên điểm gốc nằm trong [2,8]°C. Trả What-if adjustment về 0.
- Sensor sample đã kèm scores tính sẵn từ chính sensor để demo nhanh; vẫn phải chạy checker. Chạy thử hai XGBoost nếu muốn tính mới trước buổi trình bày. Chuẩn bị kết quả đã tải của lượt chạy thử để minh họa nếu máy hoặc backend phản hồi chậm; khi dùng phải nói rõ đó là kết quả chạy trước.
- Inventory khớp sensor sample được nạp tự động. Ghi nhớ một lô hạng 1 trong phần FEFO for current batches. Không đổi nguồn trong lúc QA và kho đang xử lý lô.
- Dùng scores đã lưu kèm Sensor sample nếu không chạy model tại chỗ. Đây là scores đã tính trước từ đúng file sensor, không giới thiệu là kết quả vừa chạy mới.

| Người | Nội dung | Thời lượng dự kiến |
|---|---|---|
| 1 | Bài toán và hai phạm vi app với paper | 2 phút |
| 2 | Sensor CSV và Arrhenius tại điểm đang xem | 2 phút |
| 3 | Backend inference rồi chạy hai XGBoost | 3 phút |
| 4 | Kiểm chứng regression theo paper | 3 phút |
| 5 | Inventory FEFO và workflow QA với kho | 4 phút |
| 6 | Kết luận và giới hạn | 2 phút |

## Người 1 giới thiệu bài toán và mục tiêu

**Thao tác:** Mở slide giới thiệu, sau đó Enter system → chọn QA Manager → Use demo user → Sign in.

“Em xin chào thầy cô và các bạn. Nhóm em trình bày ứng dụng ColdChain hỗ trợ giám sát chuỗi lạnh dược phẩm và nghiên cứu kiểm tra thay đổi quyết định khi cập nhật mô hình.

Trong vận chuyển và bảo quản, người phụ trách cần biết nhiệt độ của từng lô diễn biến thế nào, có điểm nào ngoài vùng quy định và có cảnh báo sớm hay không. Sau khi xem thông tin, QA quyết định duyệt hoặc từ chối lô. Nhân viên kho xử lý những lô đã được duyệt theo thứ tự hạn dùng.

Ứng dụng của nhóm kết nối các công việc này qua dữ liệu sensor, dự báo, bảng lô và workflow. Bản demo dùng CSV làm đầu vào. QA và Warehouse là hai vai trò thao tác chính.

Bên cạnh vận hành, nhóm đặt thêm một câu hỏi nghiên cứu: khi đổi model hoặc quy tắc chọn ngưỡng, danh sách đối tượng được cảnh báo có thay đổi không? Nếu hệ thống cho phép nhiều mức yêu cầu precision thì kiểm tra ở một mức có đủ không? Đây là trọng tâm của paper: so sánh tập ID được chọn trên toàn miền policy đã khai báo, xác định nơi khác biệt và tạo bằng chứng để kiểm tra lại.

Phần tiếp theo sẽ đi từ sensor đến dự báo và kiểm chứng, sau đó chuyển sang inventory để minh họa ưu tiên xuất kho.”

## Người 2 nạp sensor và giải thích Arrhenius

**Thao tác 1:** Vào Simulation, tắt Automatically run backend models rồi chọn Sensor sample hoặc upload sensor CSV. Chỉ tên nguồn, số dòng, Batch và Position.

“Mỗi dòng sensor là một lần đo, có mã lô, thời gian và nhiệt độ; dữ liệu có thể kèm độ ẩm và phương thức vận chuyển. Khi nhận file hợp lệ, app nhóm theo batch và sắp xếp theo thời gian. Trong phần này, chúng em chủ động tắt chạy model tự động để chỉ gửi yêu cầu khi bấm nút.

Em chọn batch để xem biểu đồ. Position xác định thời điểm đang xét. Khi chạy dự báo, app dùng lịch sử từ đầu chuỗi đến vị trí này. Min và max mô tả nhiệt độ trong chuỗi; số điểm ngoài [2,8] độ C là số lần đo ngoài vùng, cần kết hợp timestamp để diễn giải thời lượng.”

**Thao tác 2:** Chỉ Temperature at cursor và Arrhenius ratio. Nếu thử What-if, trả về 0 sau khi giải thích.

“Arrhenius ratio là tỷ số tốc độ suy giảm ước tính tại nhiệt độ đang xem so với mốc tham chiếu 5 độ C, theo tham số minh họa đang cấu hình. Nó cho thấy nhiệt độ tác động đến tốc độ theo mô hình như thế nào.

App hiện hiển thị tỷ số tại điểm đang xét. Phần tính cộng dồn để suy ra hạn dùng động từ sensor đã được gỡ khỏi luồng demo. Khi đến FEFO, chúng em dùng hạn đã được cung cấp trong inventory CSV.

Bây giờ em giữ nguyên sensor để bạn tiếp theo chạy dự báo backend.”

## Người 3 chạy backend và tạo cặp scores mới

**Thao tác 1:** Chọn batch và Position đã chạy thử, có nhiệt độ gốc trong vùng và lịch sử đầy đủ. Chọn Backend forecast horizon là 6 hours, What-if = 0. Xác nhận lịch sử đầy đủ rồi bấm Run backend inference. Đợi kết quả thực tế.

“Nút Run backend inference gửi lịch sử của batch đang chọn đến dịch vụ model. Với horizon sáu giờ, model ước tính khả năng khởi phát một đợt ngoài [2,8] độ C kéo dài ít nhất ba giờ trong cửa sổ tương lai đó. App còn cho chọn 12 hoặc 24 giờ.

Kết quả ghi tên model và phiên bản thực tế backend trả về. p_cal là điểm xác suất sau hiệu chỉnh; threshold là ngưỡng vận hành; status và alert cho biết trạng thái xử lý và quyết định cảnh báo. Precision50 là tên cấu hình vận hành, không phải cam kết precision 50 phần trăm trên mọi dữ liệu mới.

Lần chạy thủ công này hiển thị trong Simulation. Nếu thời điểm gốc đã ngoài vùng, cần đọc trạng thái trả về vì cảnh báo sớm có thể không áp dụng. Nếu backend lỗi, app báo lỗi và lần chạy đó chưa có kết quả dự báo.”

**Thao tác 2:** Tải inference JSON nếu cần. Đưa Position đến cuối chuỗi. Để demo nhanh, dùng cặp scores mẫu đã được tính trước từ chính sensor và nói rõ nguồn. Nếu cần chạy mới, giữ xác nhận lịch sử đầy đủ rồi bấm Run two XGBoost models locally; sensor và bảng FEFO vẫn hiển thị. Không bấm một sample khác.

“Nút thứ hai phục vụ nghiên cứu so sánh. App chạy hai XGBoost đã huấn luyện ngay trên máy local: thermal sáu giờ và thermal bổ sung đặc trưng Arrhenius sáu giờ. Đây là hai biến thể nghiên cứu riêng; không suy rằng chúng trùng weights với model backend vừa gọi.

Sensor sample đã kèm kết quả tính trước từ đúng file để giảm thời gian chờ; khi em bấm chạy lại thì model thực thi mới. Nút này tạo scores cho nhiều thời điểm đủ điều kiện trong lịch sử, tối đa hai nghìn quan sát. Nó cố định horizon sáu giờ và không áp dụng ô What-if. App suy ra nhãn từ diễn biến nhiệt độ phía sau trong file, nên cần thời gian theo dõi tương lai và loại phần cuối theo điều kiện tạo nhãn. Nhãn này được tạo theo quy tắc, chưa phải ground truth được đánh giá độc lập.

Khi chạy thành công, app đưa ID, nhãn và hai cột scores sang mục 3. Chúng em không cần chọn Regression CSV nữa. Chạy hai model mới hoàn thành bước tạo dữ liệu; bước kiểm chứng sẽ do bạn tiếp theo thực hiện.”

## Người 4 kiểm chứng quyết định theo paper

**Thao tác:** Giữ dataset do hai model vừa tạo. Không bấm scores mẫu liên kết. Trong mục 3, chỉ tên hai model và bảng scores. Chọn lo = 0.30, hi = 0.90, cả hai contract inclusive ≥. Bấm Compare and verify independently.

“Bảng này chứa cùng các quan sát được chấm bởi hai model. ID dùng để đối chiếu cùng quan sát; y là nhãn; old_score và new_score là điểm của hai bên.

Paper không chỉ so xem scores tăng hay giảm. Nó kiểm tra hai selector có chọn đúng cùng tập ID trên miền yêu cầu precision từ 0,30 đến 0,90 hay không. Alpha là yêu cầu precision của tập được chọn, khác với ngưỡng score. Với contract inclusive, ứng viên có precision đúng bằng alpha vẫn được chấp nhận.

Phương pháp tìm các điểm có thể làm quyết định thay đổi, chia miền thành các khoảng và các điểm biên rồi so membership. Cách kiểm tra đầy đủ này dựa trên contract hữu hạn đã khai báo. Producer tạo certificate; checker riêng dựng lại membership từ đầu vào để kiểm tra trước khi trả kết luận.”

**Thao tác:** Đọc verdict thực tế; chỉ PSC, các cells và witness nếu có. Tải certificate JSON.

“Nếu kết quả là EQUIVALENT, hai phiên bản chọn cùng ID trên toàn miền đã kiểm tra theo contract. Nếu là DIVERGENT, có ít nhất một alpha làm tập ID khác nhau. Witness chỉ ra trường hợp cụ thể để kiểm tra lại.

PSC là tỷ lệ độ dài miền alpha có phân kỳ. Nó không phải tỷ lệ dữ liệu dự đoán sai. Nếu hai bên chỉ khác tại một điểm riêng lẻ, PSC có thể bằng không mà verdict vẫn là DIVERGENT. Đây là lý do paper giữ thông tin điểm biên thay vì chỉ thử vài mức alpha.

DIVERGENT cũng chưa kết luận model mới kém hơn; nó cho biết quyết định đã đổi ở đâu. Certificate có thể tải về để kiểm tra lại với đầu vào. Kết luận giới hạn trên dataset, miền policy và contract hiện tại, không chứng nhận toàn bộ ứng dụng hoặc chất lượng hàng.

Sau phần nghiên cứu này, nhóm giữ nguyên nguồn và mở FEFO của chính các lô đó để minh họa workflow.”

## Người 5 chạy FEFO và workflow QA với kho

**Thao tác 1:** Giữ nguyên nguồn sensor. Bấm FEFO for current batches hoặc cuộn tới bảng FEFO đã nạp cùng sample. Chỉ Product_ID, Batch_ID, Dynamic_Expiry_Date và FEFO rank. Đối chiếu mã lô với batch ở phần sensor/regression. Không upload file khác; ghi nhớ lô hạng 1.

“Inventory được gắn với sensor theo cùng Batch_ID và được giữ khi kiểm chứng regression. Mỗi dòng ghi một lô của một sản phẩm, kèm ngày hết hạn được cung cấp trong Dynamic_Expiry_Date. App dùng ngày này để xếp FEFO trong từng sản phẩm: hạn sớm hơn được ưu tiên trước. Những lô có cùng hạn được cùng hạng.

Ở luồng hiện tại, app không tính lại hạn dùng từ sensor hoặc từ scores XGBoost. Tên cột Dynamic_Expiry_Date mô tả giá trị đầu vào; người cung cấp dữ liệu chịu trách nhiệm về nguồn và cách xác định ngày đó. Inventory này đã được gắn cùng sensor. Kiểm chứng vừa rồi giữ nguyên nguồn, nên Dashboard và workflow vẫn có cùng lịch sử nhiệt và thông tin lô.”

**Thao tác 2:** QA → Batches → View details đúng lô hạng 1 → Approve → Confirm action. Log out và đăng nhập Warehouse Staff trong cùng tab.

“FEFO cho biết thứ tự ưu tiên. QA vẫn cần xem hồ sơ và quyết định duyệt. Em mở đúng lô hạng một, ghi nhận Approve rồi xác nhận. Nếu chọn Reject, cần ghi lý do theo yêu cầu của app. Sau đó em đổi vai trò trong cùng tab để kho tiếp tục trên trạng thái vừa ghi.”

**Thao tác 3:** Warehouse → Dispatch Board → tìm lô Ready to queue → Add to Queue → Confirm action → Confirm Dispatch → Confirm action. Mở Batches đối chiếu Dispatched, tải workflow audit JSON.

“Kho thấy lô đã được duyệt trong Ready to queue. Add to Queue đưa lô vào hàng đợi; Confirm Dispatch ghi nhận bước xác nhận xuất trong demo. App kiểm tra trạng thái, vai trò và thứ tự FEFO trước khi chấp nhận thao tác. Lô đang chờ QA có thể được gửi yêu cầu xem xét.

Dispatch Board tập trung vào các việc cần làm, còn Batches dùng tra cứu. Audit JSON ghi lại lịch sử thao tác trong phiên. Đây là workflow mô phỏng trong cùng tab, chưa phải giao dịch xuất kho được lưu vào cơ sở dữ liệu server.”

## Người 6 kết luận và giới hạn

**Thao tác:** Về slide kết luận. Chỉ inference JSON, certificate và workflow audit nếu cần; phân biệt mục đích từng file.

“Nhóm vừa trình bày ba luồng dùng dữ liệu. Sensor phục vụ xem nhiệt độ và gọi backend dự báo. Cặp scores từ hai XGBoost phục vụ kiểm chứng thay đổi quyết định theo paper. Inventory có hạn dùng sẵn phục vụ FEFO và phối hợp giữa QA với kho.

Đóng góp nghiên cứu tập trung vào xác định chính xác sự khác biệt của tập ID được chọn trên miền precision, giữ cả những khác biệt tại điểm biên và cung cấp bằng chứng để kiểm tra độc lập. App đưa phương pháp vào một màn thao tác cùng bối cảnh ColdChain.

Bản hiện tại chạy dự báo bằng model đã huấn luyện; upload không huấn luyện lại model. Workflow và upload được giữ trong phiên tab, chưa có lưu trữ giao dịch và đồng bộ nhiều người dùng trên server. Việc triển khai tiếp cần bổ sung lưu trữ, xác thực và đánh giá trên dữ liệu thực tế phù hợp.

Kết quả dự báo, kết luận tương đương selector và quyết định duyệt lô có ý nghĩa riêng. QA vẫn chịu trách nhiệm đánh giá và phê duyệt theo quy trình. Nhóm em xin cảm ơn thầy cô và các bạn.”

## Xử lý khi demo chậm hoặc lỗi

- Backend chậm: nói “Yêu cầu đang chờ backend trả về”; dùng kết quả chạy thử đã lưu và ghi rõ nguồn. Không giới thiệu kết quả cũ là response của lần bấm hiện tại.
- Hai XGBoost không chạy được: chuyển scores mẫu liên kết và nói “Đây là cặp scores đã lưu từ hai model nghiên cứu, được dùng để minh họa bước kiểm chứng”. Sau đó chạy mục 3; không cần chạy backend để dùng regression CSV.
- Checker chậm: dùng certificate đã chuẩn bị để giải thích kết quả và phạm vi. Không kết luận PASS cho lượt đang chờ.
- Nếu rút ngắn buổi demo: bỏ What-if, chỉ chạy backend horizon 6 giờ, chỉ demo một lô FEFO và một nhánh Approve → Queue → Dispatch.
- Không nhập sẵn lời khẳng định sample chắc chắn DIVERGENT hoặc chắc chắn có cảnh báo. Luôn đọc đúng kết quả đang hiển thị.
