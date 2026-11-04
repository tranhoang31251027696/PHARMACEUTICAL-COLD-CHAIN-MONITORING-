# Mã nguồn và các script nghiên cứu

Các file Python lẻ đã được gom vào `reproduction/`. Đây là một bộ tái lập tự chứa: các script giữ tài nguyên `src/`, `inputs/`, `vendor/`, `results/`, `docs/`, `tests/`, `provenance/` và `evidence/` cạnh nhau vì dùng đường dẫn tương đối. Không có bản sao thừa của từng script ở ngoài.

```text
code/
├── README.md
└── reproduction/
    ├── run_all.py
    ├── build_manuscript.py
    ├── validate_all.py
    ├── các script thí nghiệm/CLI/công cụ bên dưới
    ├── src/          # thuật toán, oracle và checker cốt lõi
    ├── tests/        # bộ kiểm thử
    ├── inputs/       # frozen inputs và hash
    ├── vendor/       # dependency, nguồn upstream và giấy phép
    ├── results/      # kết quả tham chiếu và snapshot
    ├── docs/         # đặc tả, chứng minh, protocol, Markdown
    ├── provenance/   # hash nguồn và khai báo kế thừa
    └── evidence/     # metadata kiểm toán lịch sử
```

## Chạy gì?

Từ thư mục gốc repository, dùng Python 3.13.18, tạo/kích hoạt môi trường ảo rồi chạy:

```shell
python -m pip install -r requirements.txt
python run_all.py
```

Lệnh ở gốc chuyển đến `code/reproduction/run_all.py`. Không cần chạy lần lượt các bản dự án cũ. Để kiểm tra lại kết quả đã có hoặc dựng lại Markdown:

```shell
python code/reproduction/validate_all.py
python code/reproduction/build_manuscript.py
```

Không cần tự gọi từng script trong các bảng sau. Lệnh mặc định điều phối những bước cần thiết. Các công cụ tùy chọn không được đánh dấu là đã chạy chỉ vì chúng có trong repository.

## Lệnh chạy và kiểm chứng

| File | Nhiệm vụ | Cách dùng |
|---|---|---|
| [run_all.py](reproduction/run_all.py) | Điều phối 33 bước thí nghiệm/kiểm chứng theo đúng thứ tự. | Mặc định |
| [validate_all.py](reproduction/validate_all.py) | Kiểm tra kết quả đã có; gộp 10 nhóm kiểm chứng, chọn riêng bằng --section. | Mặc định |
| [verify_artifact.py](reproduction/verify_artifact.py) | Kiểm tra độc lập certificate, memberships, witness và các số lượng báo cáo. | Mặc định |
| [verify_release.py](reproduction/verify_release.py) | Giải nén ZIP đóng băng, kiểm tra manifest rồi chạy pipeline và tạo report tách rời. | Công cụ phát hành |

## Đặc tả và giao diện chương trình

| File | Nhiệm vụ | Cách dùng |
|---|---|---|
| [policy_cli.py](reproduction/policy_cli.py) | CLI đọc các mảng frozen input và tạo certificate cho so sánh policy. | Được kiểm tra trong pipeline |
| [program_gate.py](reproduction/program_gate.py) | CLI trả trạng thái conforming, failing hoặc unsupported cho selector thật. | Được kiểm tra trong pipeline |
| [check_cli_integration.py](reproduction/check_cli_integration.py) | Kiểm tra việc gọi CLI và mã thoát trên các trường hợp cần thiết. | Mặc định |
| [policy_domain_query.py](reproduction/policy_domain_query.py) | Truy vấn tập policy hữu hạn, lattice thập phân hoặc interval trên certificate đã kiểm tra. | Thư viện dùng bởi thí nghiệm |
| [verified_boolean_query.py](reproduction/verified_boolean_query.py) | Index trả Boolean và witness mà không tạo toàn bộ output giao cắt. | Thư viện dùng bởi thí nghiệm |

## Thí nghiệm cốt lõi và chi phí

| File | Nhiệm vụ | Cách dùng |
|---|---|---|
| [run_experiments.py](reproduction/run_experiments.py) | Chạy các input pairs, declared mutants/controls và benchmark tạo certificate. | Mặc định |
| [program_evaluation.py](reproduction/program_evaluation.py) | Chạy source mutants thật với reference specification không đổi. | Mặc định |
| [benchmark_test_methods.py](reproduction/benchmark_test_methods.py) | Đo các phương pháp trên cùng đầu vào, giữ đúng phạm vi từng phép kiểm tra. | Mặc định |
| [checker_cost_benchmark.py](reproduction/checker_cost_benchmark.py) | Benchmark riêng chi phí consumer/checker so với producer. | Công cụ bổ sung |
| [run_ablation.py](reproduction/run_ablation.py) | Đo chi phí từng pha bên trong một lần gọi thuật toán. | Mặc định |
| [streaming_checker_study.py](reproduction/streaming_checker_study.py) | So sánh consumer cũ/streaming và kiểm tra lại tập certificate. | Mặc định |
| [reuse_cost_study.py](reproduction/reuse_cost_study.py) | Đo chi phí tái sử dụng certificate theo batch, gồm setup. | Mặc định |
| [boolean_query_study.py](reproduction/boolean_query_study.py) | Đo riêng API Boolean và API đầy đủ với các nghĩa vụ evidence đã phân biệt. | Mặc định |

## SMT, vùng phân kỳ và domain

| File | Nhiệm vụ | Cách dùng |
|---|---|---|
| [smt_baseline.py](reproduction/smt_baseline.py) | Đối chứng Z3 cho câu hỏi có policy gây sai khác hay không. | Mặc định |
| [complete_region_comparison.py](reproduction/complete_region_comparison.py) | So sánh toàn bộ vùng phân kỳ, endpoints, PSC và witness giữa partition và SMT. | Mặc định |
| [expanded_region_benchmark.py](reproduction/expanded_region_benchmark.py) | Benchmark theo kích thước N, số candidate và kiểu candidate omission. | Mặc định |
| [large_g_region_benchmark.py](reproduction/large_g_region_benchmark.py) | Mở rộng phép so sánh sang số candidate lớn G=250/500. | Mặc định |
| [policy_significance.py](reproduction/policy_significance.py) | Tính PSC và ảnh hưởng trên các độ phân giải policy được khai báo. | Mặc định |
| [domain_query_study.py](reproduction/domain_query_study.py) | Đối chiếu truy vấn allowed-policy domains trên cohort SciPy hiện có. | Mặc định |

## Ca thực tế và giới hạn tích hợp

| File | Nhiệm vụ | Cách dùng |
|---|---|---|
| [external_sut_evaluation.py](reproduction/external_sut_evaluation.py) | Tái hiện lỗi scikit-learn #23213 từ các hàm upstream được ghim nguồn. | Mặc định |
| [external_selector_integration.py](reproduction/external_selector_integration.py) | Gọi threshold optimizer qua public API của scikit-learn đang cài. | Mặc định |
| [scipy_documented_defect.py](reproduction/scipy_documented_defect.py) | Tái hiện lỗi SciPy #6318/#6351 về integer-axis overflow của nearest interpolation. | Mặc định |
| [second_project_evaluation.py](reproduction/second_project_evaluation.py) | Chạy selector eval-toolkit và đối chiếu semantics binary64/rational. | Mặc định |
| [failure_and_ci_evaluation.py](reproduction/failure_and_ci_evaluation.py) | Sinh fixture không được hỗ trợ và kiểm tra local subprocess/CI gate. | Mặc định |
| [version_evaluation.py](reproduction/version_evaluation.py) | Kiểm tra lại các output phiên bản đã đóng kèm; sai khác không tự động là bug. | Mặc định |

## Chuẩn bị dữ liệu và chạy dependency riêng

| File | Nhiệm vụ | Cách dùng |
|---|---|---|
| [prepare_inputs.py](reproduction/prepare_inputs.py) | Tạo lại frozen inputs và huấn luyện pipeline; cần tài nguyên huấn luyện gốc. | Tùy chọn --retrain; không cần cho mặc định |
| [version_worker.py](reproduction/version_worker.py) | Thực thi interpolation trong một môi trường SciPy cụ thể do người dùng cung cấp. | Tùy chọn; không cần cho mặc định |
| [run_version_pair.py](reproduction/run_version_pair.py) | Điều phối hai môi trường SciPy riêng để chạy lại binary-version comparison. | Tùy chọn; không cần cho mặc định |

## Bài báo và đóng gói

| File | Nhiệm vụ | Cách dùng |
|---|---|---|
| [build_manuscript.py](reproduction/build_manuscript.py) | Dựng bản Markdown cuối từ kết quả; toàn bộ helper build đã gộp trong file này. | Bước cuối pipeline |
| [render_manuscript.py](reproduction/render_manuscript.py) | Xuất Word với bảng, hình và phương trình từ Markdown; khác bước tính toán. | Authoring riêng |
| [package_artifact.py](reproduction/package_artifact.py) | Đóng băng ZIP tái lập, tạo manifest và loại response/tệp nội bộ khỏi gói. | Công cụ phát hành |

## Có xóa các file nhỏ được không?

Không nên xóa theo kích thước hoặc theo tên. Nhiều file nhỏ là module được import, CLI được subprocess gọi hoặc một bước benchmark riêng. `build_manuscript.py` và `validate_all.py` đã gộp các file revision; những script còn lại có vai trò khác nhau. README này chỉ rõ đâu là bước mặc định và đâu là công cụ tùy chọn.

ZIP V11 đã chạy 33 bước và bằng chứng gốc vẫn nằm dưới `report/` của repository. Bản mã sau consolidation/grouping có kiểm tra riêng; không gán báo cáo 33 bước cũ cho một source tree đã thay đổi cấu trúc. Xem `report/consolidation_checks/` và `report/grouping_checks/`.
