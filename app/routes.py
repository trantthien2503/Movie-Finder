from app import app
from flask import Flask, jsonify
import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity
# Lấy đường dẫn tới thư mục chứa file hiện tại

current_dir = os.path.dirname(os.path.abspath(__file__))

# Xây dựng đường dẫn tới file movies.dat
movies_file_path = os.path.join(current_dir, 'data', 'movies.dat')

# Đọc file movies.dat
movies_df = pd.read_csv(movies_file_path, sep='::', engine='python', names=['MovieID', 'Title', 'Genres'], encoding='ISO-8859-1')

# Xây dựng đường dẫn tới file ratings.dat
ratings_file_path = os.path.join(current_dir, 'data', 'ratings.dat')

# Đọc file ratings.dat
ratings_df = pd.read_csv(ratings_file_path, sep='::', engine='python', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], encoding='ISO-8859-1')

# Tạo pivot table từ ratings_df
pivot_table = ratings_df.pivot(
    index='UserID', columns='MovieID', values='Rating').fillna(0)

# Tính ma trận độ tương đồng cosine
similarity_matrix = cosine_similarity(pivot_table)

# Hàm gợi ý phim dựa trên userId


def get_movie_suggestions(userId, num_suggestions=10):
    user_index = pivot_table.index.get_loc(userId)

    # Tính toán độ tương đồng cosine giữa user hiện tại và tất cả các user khác
    user_similarity_scores = similarity_matrix[user_index]

    # Lấy danh sách các user có độ tương đồng cao nhất
    similar_users_indices = user_similarity_scores.argsort()[::-1][1:]

    # Tạo danh sách các phim được gợi ý
    suggested_movies = []
    for i in similar_users_indices:
        movies_not_watched = pivot_table.iloc[i][pivot_table.iloc[user_index] == 0]
        if not movies_not_watched.empty:
            suggested_movies.extend(movies_not_watched.sort_values(
                ascending=False).index[:num_suggestions])
            if len(suggested_movies) >= num_suggestions:
                break

    return movies_df[movies_df['MovieID'].isin(suggested_movies)].to_dict('records')


# GET
@app.route('/api/dataget', methods=['GET'])
def get_data():
    data = {'message': 'Hello, World!'}
    return jsonify(data)

@app.route('/api/suggest', methods=['GET'])
def suggest():
    return jsonify(get_movie_suggestions(1))    

# Post
@app.route('/api/datapost', methods=['POST'])
def create_data():
    # Lấy dữ liệu từ yêu cầu và tạo một tài nguyên mới
    data = request.get_json()
    # Lưu dữ liệu vào cơ sở dữ liệu hoặc xử lý theo nhu cầu
    # ...
    return jsonify({'message': 'POST request successful'})

# Put
@app.route('/api/dataput/<id>', methods=['PUT'])
def update_data(id):
    # Lấy dữ liệu từ yêu cầu và cập nhật tài nguyên có id tương ứng
    data = request.get_json()
    # Tìm và cập nhật tài nguyên có id trong cơ sở dữ liệu hoặc xử lý theo nhu cầu
    # ...
    return jsonify({'message': 'PUT request successful'})

# Delete
@app.route('/api/datadelete/<id>', methods=['DELETE'])
def delete_data(id):
    # Xóa tài nguyên có id tương ứng trong cơ sở dữ liệu hoặc xử lý theo nhu cầu
    # ...
    return jsonify({'message': 'DELETE request successful'})