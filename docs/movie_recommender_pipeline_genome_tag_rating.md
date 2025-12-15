# 📌 Movie Recommender Pipeline (Genome Tag + Rating)

## 🎯 Mục tiêu
Xây dựng hệ thống gợi ý phim dựa trên **content-based filtering** bằng **genome tag**, phù hợp cho **bài lab / thực hành**, có khả năng:
- Gợi ý **phim tương tự một phim cho trước**
- Gợi ý **phim phù hợp cho người dùng** dựa trên lịch sử đánh giá

---

## 1️⃣ Chuẩn bị dữ liệu

### 📂 Các file sử dụng
- **`genome_tags.csv`**
  - `movieId`: ID phim (MovieLens)
  - `tag`: nhãn nội dung
  - `relevance`: mức độ liên quan của tag với phim

- **`movies.csv`**
  - `movieId`
  - `title`

- **`ratings.csv`** *(tuỳ chọn)*
  - `userId`
  - `movieId`
  - `rating`

---

## 2️⃣ Biểu diễn phim dưới dạng vector

### 🔹 Ý tưởng
Mỗi phim được biểu diễn bằng **vector genome tag có trọng số relevance**.

- Mỗi **tag** là một chiều của vector
- Giá trị tại mỗi chiều là **relevance** tương ứng
- Vector rất **thưa (sparse)**

### 🔹 Thực hiện
1. Lấy danh sách tag duy nhất → ánh xạ `tag → index`
2. Lấy danh sách movieId duy nhất → ánh xạ `movieId → index`
3. Với mỗi dòng `(movieId, tag, relevance)`:
   - Gán `X[movie_index, tag_index] = relevance`
4. Tạo **ma trận sparse (CSR)** `X`

📌 Kết quả:
```
X ∈ R^(num_movies × num_tags)
```

---

## 3️⃣ Tính độ tương đồng giữa các phim

### 🔹 Phương pháp
- **Cosine Similarity**

### 🔹 Lý do chọn cosine
- Vector nhiều chiều
- Dữ liệu thưa
- So sánh tốt về "hướng" nội dung

### 🔹 Kết quả
- Ma trận tương đồng:
```
sim[i][j] = độ tương đồng giữa phim i và phim j
```

---

## 4️⃣ Gợi ý phim tương tự một phim

### 🔹 Quy trình
1. Nhận `movieId` đầu vào
2. Chuyển `movieId → index`
3. Lấy vector similarity tương ứng
4. Sắp xếp giảm dần
5. Loại bỏ chính nó
6. Lấy **top-K phim giống nhất**

📌 Kết quả:
- Danh sách phim có nội dung tương tự

---

## 5️⃣ Xây dựng vector đại diện cho người dùng (User Profile)

### 🔹 Ý tưởng
Vector người dùng được xây dựng bằng cách **kết hợp các vector phim mà người dùng đã đánh giá**, có **trọng số theo rating**.

### 🔹 Công thức
\[
\vec{u} = \frac{\sum r_i \cdot \vec{v_i}}{\sum r_i}
\]

Trong đó:
- \( \vec{v_i} \): vector phim
- \( r_i \): điểm rating của người dùng

---

## 6️⃣ Gợi ý phim cho người dùng

### 🔹 Quy trình
1. Xây dựng `user_vector`
2. Tính cosine similarity giữa `user_vector` và toàn bộ phim
3. Loại bỏ các phim người dùng đã xem
4. Lấy **top-K phim phù hợp nhất**

📌 Kết quả:
- Danh sách phim được đề xuất cho người dùng

---

## 7️⃣ Hiển thị kết quả

- Kết hợp với `movies.csv`
- Map `movieId → title`
- In kết quả dễ đọc cho người dùng / báo cáo

---

## 8️⃣ Đánh giá phương pháp

### ✅ Ưu điểm
- Không cần huấn luyện mô hình phức tạp
- Không cần dữ liệu người dùng lớn
- Dễ cài đặt, dễ giải thích
- Kết quả gợi ý hợp lý cho bài lab

### ⚠️ Hạn chế
- Không học được xu hướng cộng đồng
- Phụ thuộc vào chất lượng genome tag

---

## 9️⃣ Kết luận

> Hệ thống gợi ý phim được xây dựng dựa trên genome tag với trọng số relevance, sử dụng cosine similarity để đo độ tương đồng. Phương pháp content-based filtering này phù hợp cho bài tập thực hành và cho kết quả gợi ý hợp lý với độ phức tạp thấp.

---