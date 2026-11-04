# ColdChain IQ và kiểm thử hồi quy bộ chọn ngưỡng

Kho nộp đồ án gồm ứng dụng ColdChain IQ, dữ liệu dùng trong đồ án và mã tái lập bài nghiên cứu *Exact Policy-Aware Regression Diagnosis for Precision-Constrained Threshold Selectors*.

## Chạy ứng dụng ColdChain IQ

- Link demo Netlify: https://coldchain-monitoring.netlify.app

Dùng Python 3.13.18. Từ thư mục gốc của repository, chạy:

```powershell
python -m pip install -r app/requirements-ui.txt
python app/start_ui.py
```

Mở địa chỉ được in trên terminal (thường là http://127.0.0.1:8000). Chọn **Enter system → Use demo user → Sign in → Simulation**. Chọn một bộ dữ liệu mẫu hoặc tải lên tệp CSV/TSV theo [hướng dẫn sử dụng](app/HUONG_DAN_SU_DUNG.md).

Trình kiểm tra hồi quy chạy trên máy. Dự báo Model 1 và dữ liệu lịch sử của dashboard dùng backend từ cấu hình app, có thể đặt qua biến môi trường `COLDCHAIN_MODEL_API`. Các chức năng này cần kết nối mạng và backend hoạt động. Tắt **auto-inference** nếu muốn phân tích tệp tải lên trên máy mà không gửi lịch sử cảm biến sang backend.



## Dữ liệu

| Thư mục | Nội dung |
| --- | --- |
| [data/01_Paper](data/01_Paper) | 98 cặp đầu vào cố định của paper gồm 50 Retained, 17 ca tổng hợp, 1 WDBC pilot và 30 cặp pipeline. Có manifest và các đầu vào kiểm thử bổ sung. |
| [data/02_App_Samples](data/02_App_Samples) | Bốn CSV mẫu gồm cảm biến 1 lô (336 dòng), cảm biến 3 lô (888 dòng), tồn kho FEFO (50 dòng) và hồi quy (3 dòng). Bản phục vụ trực tiếp cho app nằm trong `app/NETLIFY_DASHBOARD/samples/`. |
| [data/03_FEFO_Raw](data/03_FEFO_Raw) | Dữ liệu chuỗi lạnh mô phỏng gồm `sensor.csv` (416.688 bản ghi), `batches.csv` (1.500 lô) và `products.csv`, kèm kết quả xếp hạng FEFO và hồ sơ lần chạy. |

Thông số **N = 37.471, G = 87, K = 6** thuộc hàng đo hiệu năng *Simulated Cold-Chain* trong paper. Xem [README dữ liệu](data/README.md) để tra nguồn và vai trò của từng bộ.

## Tái lập nghiên cứu

Từ thư mục gốc, trong môi trường Python 3.13.18 riêng, chạy:

```powershell
python -m pip install -r requirements.txt
python run_all.py
```

Lệnh chạy quy trình 33 bước với đầu vào tại `code/reproduction/inputs/` và ghi lại kết quả sinh ra trong `code/reproduction/results/`. Lần chạy ghi nhận mất khoảng 39 phút. Xem [hướng dẫn tái lập](code/reproduction/docs/REPRODUCIBILITY_V11.md) và [danh mục mã](code/README.md).

## Tài liệu nộp

- [Paper và Supplement](report/paper) có bản LaTeX, gói nguồn LaTeX và các bản Word. Hai PDF có hậu tố `_LaTeX` tương ứng bản LaTeX.
- [Artifact và Evidence V11](report/release) gồm bộ tái lập đóng băng và hồ sơ kiểm chứng.

