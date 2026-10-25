# Business Data Assistant (BDA)

Ứng dụng phân tích dữ liệu bằng tiếng Việt, thiết kế theo hướng dễ dùng, có thể mở rộng cho đồ án sinh viên.

## Tính năng hiện có

- Tải CSV, XLSX, XLS; xem trước dữ liệu.
- Báo cáo nhanh: số dòng/cột, ô trống, dòng trùng, kiểu dữ liệu.
- Làm sạch: bỏ dòng trùng, xóa khoảng trắng, chuẩn hóa tên cột, xử lý ô trống.
- Lọc theo điều kiện, sắp xếp nhiều cột.
- Nhóm và tổng hợp; tạo cột bằng phép nhân; biểu đồ cột.
- Xuất CSV/Excel.
- Tích hợp AI API tùy chọn, chỉ gửi metadata và tối đa 3 dòng mẫu trong bản khởi đầu.
- Kết nối PostgreSQL tùy chọn và khởi tạo bảng metadata.
- Giới hạn upload Streamlit được cấu hình 1 GB; giới hạn thực tế phụ thuộc RAM, dung lượng tạm và hosting.

## Yêu cầu

Python 3.11 hoặc 3.12 được khuyến nghị để có hệ sinh thái thư viện ổn định. Có thể dùng Python mới hơn nếu các gói hỗ trợ tương thích.

## Chạy trên Windows bằng VS Code

1. Giải nén thư mục dự án.
2. Mở thư mục `BusinessDataAssistant` trong VS Code.
3. Mở Terminal tại thư mục đó.
4. Tạo môi trường ảo:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Khởi chạy ứng dụng:

   ```powershell
   streamlit run app.py
   ```

6. Trình duyệt sẽ mở giao diện. Nếu lệnh `py -3.12` không hoạt động, hãy cài Python 3.12 hoặc dùng phiên bản Python tương thích đã có trên máy.

## Bật AI (tùy chọn)

1. Sao chép `.env.example` thành `.env`.
2. Điền `OPENAI_API_KEY` và model được tài khoản API của bạn hỗ trợ.
3. Khởi động lại Streamlit.

API có thể phát sinh chi phí. Không commit `.env` lên GitHub. AI trong bản đầu chỉ tư vấn; chưa tự chạy thao tác trên dữ liệu.

## Bật PostgreSQL (tùy chọn)

1. Tạo database PostgreSQL local hoặc cloud (ví dụ Supabase).
2. Thêm `DATABASE_URL` vào `.env`, dùng định dạng `postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME`.
3. Trong ứng dụng, mở tab **Database** và chọn **Kiểm tra kết nối và tạo bảng BDA**.

Không đưa mật khẩu database lên GitHub. Cấu hình mạng, TLS, firewall và quyền database cần được thiết lập đúng trước khi triển khai công khai.

## Kiểm thử

```powershell
python -m pytest -v
```

## Cấu hình upload

`.streamlit/config.toml` đặt `maxUploadSize = 1024` (MB). Đây chỉ là giới hạn upload ở tầng Streamlit, không bảo đảm file 1 GB sẽ xử lý được trong RAM. Với file lớn cần thử tải trên máy/hosting mục tiêu, giới hạn dung lượng tạm và tránh tạo nhiều bản sao DataFrame.

## Lưu ý bảo mật và giới hạn bản đầu

- Đây là MVP học tập, chưa phải hệ thống doanh nghiệp đã kiểm toán bảo mật.
- Không dùng dữ liệu cá nhân/nhạy cảm thật khi chưa thiết lập quyền truy cập, mã hóa, chính sách lưu trữ và xóa dữ liệu.
- Tab Database chỉ khởi tạo bảng metadata; chưa có đăng nhập, phân quyền nhiều người dùng, upload file bền vững hoặc lưu toàn bộ lịch sử trong database.
- Bản đầu chưa có đăng nhập, hàng đợi tác vụ nền, resumable upload, kiểm soát quota người dùng hay triển khai production hoàn chỉnh.
- Kiểm tra mọi thao tác trên bản sao trước khi áp dụng. Kết quả thống kê cần được đối chiếu với ý nghĩa nghiệp vụ của dữ liệu.

## Cấu trúc

```text
BusinessDataAssistant/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/config.toml
├── data/sample/sales_demo.csv
├── src/
│   ├── ai_assistant.py
│   ├── data_analyzer.py
│   ├── data_cleaner.py
│   ├── data_loader.py
│   ├── data_quality.py
│   ├── db.py
│   └── exporter.py
└── tests/test_analyzer.py
```
