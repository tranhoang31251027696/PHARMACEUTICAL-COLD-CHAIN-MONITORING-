# Dữ liệu đã sử dụng

- **01_Paper** là bản sao từ `src/Q1/inputs`. Có 98 ca NPZ trong manifest, gồm 50 Retained, 17 synthetic, 1 WDBC pilot và 30 pipeline. Thư mục cũng giữ các đầu vào phụ, gồm lưới lịch sử và dữ liệu dùng để kiểm tra thư viện. N = 37.471, G = 87 và K = 6 là thông số của hàng benchmark Simulated Cold-Chain trong paper.
- **02_App_Samples** là bốn CSV từ `ColdChain UI/NETLIFY_DASHBOARD/samples`. Gồm cảm biến 1 lô (336 dòng), cảm biến 3 lô (888 dòng), tồn kho FEFO (50 dòng) và regression (3 dòng). Khi người dùng tải tệp riêng lên, app sử dụng tệp đó trong phiên.
- **03_FEFO_Raw** là ba CSV nguồn từ `PAPER_DATASETS/01_Model1_Synthetic_Raw`. Bộ mô phỏng có 1.500 lô và 416.688 bản ghi cảm biến. Kết quả xếp hạng và hồ sơ lần chạy được lưu cùng thư mục trong `fefo_ranking.csv` và `run_manifest.json`.

Các tệp dữ liệu được đối chiếu SHA-256 với nguồn sau khi sao chép.

