# Đưa đồ án lên GitHub

Tạo một repository trống trên GitHub và mở terminal tại thư mục chứa README này. Đưa toàn bộ nội dung của thư mục lên repository, gồm `app/`, `data/`, `code/`, `report/` và các tệp cấu hình ẩn.

```powershell
git init
git add .
git status --short
git commit -m "Add ColdChain IQ project, datasets and research artifact"
git branch -M main
git remote add origin URL_REPOSITORY_CUA_BAN
git push -u origin main
```

Thay `URL_REPOSITORY_CUA_BAN` bằng địa chỉ repo của bạn. Nếu thư mục đã có Git và remote `origin`, kiểm tra `git remote -v` rồi dùng remote hiện có nếu đúng repo đích. Sau khi push, mở GitHub để kiểm tra README, thư mục dữ liệu và tài liệu nộp.
