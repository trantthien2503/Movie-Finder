from app import app
from flask import Flask, jsonify, request
import pandas as pd
import os
import json
from sklearn.metrics.pairwise import cosine_similarity
import random
import string
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

# Xây dựng đường dẫn tới file ratings.dat
user_file_path = os.path.join(current_dir, 'data', 'users.dat')

# Đọc file ratings.dat
users_df = pd.read_csv(user_file_path, sep='::', engine='python', names=['UserID','Gender','Age','Occupation','Zip-code'], encoding='ISO-8859-1')





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



def save_user_data_to_file(data):
    with open('users.dat', 'w') as file:
        json.dump(data, file)



def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def update_user_data_format():
    users = users_df.to_dict('records')
    updated_users = []

    for user in users:
        user_id = int(user['UserID'])
        gender = user['Gender']
        age = int(user['Age'])
        occupation = int(user['Occupation'])
        zip_code = user['Zip-code']
        username = generate_random_string(8)
        password = generate_random_string(10)
        updated_user = f"{user_id}::{gender}::{age}::{occupation}::{zip_code}::{username}::{password}\n"
        updated_users.append(updated_user)
        print("Đang chạy trong này")

    print("Danh sách cập nhật", updated_users)   
    save_user_data_to_file(updated_users)

# GET
# Hàm thực hiện lấy danh sách phim

@app.route('/', methods=['GET'])
def init():
    update_user_data_format()
    return jsonify({'message': 'Updating'})


@app.route('/api/get-moives', methods=['GET'])
def get_movies():
    # Chuyển đổi DataFrame thành định dạng JSON
    movies_json = movies_df.to_json(orient='records')
    response = jsonify(movies_json)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Hàm thực hiện trả về danh sách gợi ý theo UserID
@app.route('/api/suggest', methods=['GET'])
def suggest():
    response = jsonify(get_movie_suggestions(1))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 


# Hàm thực hiện lấy danh sách phim theo userId
@app.route('/api/get-movies-byuserid/<int:userId>', methods=['GET'])
def get_moives_byUserId(userId):
   # Lấy danh sách phim theo userId
    suggested_movies = get_movie_suggestions(userId)
    # Tạo response với dữ liệu JSON
    response = jsonify(suggested_movies)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Post
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Xử lý logic đăng nhập
    # ...

    response = jsonify({'message': 'Đăng nhập thành công'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Xử lý logic đăng ký
    save_user_data_to_file(data)

    response = jsonify({'message': 'Đăng ký thành công'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




# Put


# Delete
@app.route('/api/datadelete/<id>', methods=['DELETE'])
def delete_data(id):
    # Xóa tài nguyên có id tương ứng trong cơ sở dữ liệu hoặc xử lý theo nhu cầu
    # ...
    return jsonify({'message': 'DELETE request successful'})