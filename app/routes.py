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
movies_df = pd.read_csv(movies_file_path, sep='::', engine='python', names=[
                        'MovieID', 'Title', 'Genres'], encoding='ISO-8859-1')

# Xây dựng đường dẫn tới file ratings.dat
ratings_file_path = os.path.join(current_dir, 'data', 'ratings.dat')

# Đọc file ratings.dat
ratings_df = pd.read_csv(ratings_file_path, sep='::', engine='python', names=[
                         'UserID', 'MovieID', 'Rating', 'Timestamp'], encoding='ISO-8859-1')

# Xây dựng đường dẫn tới file ratings.dat
user_file_path = os.path.join(current_dir, 'data', 'users.dat')

# Đọc file users.dat
users_df = pd.read_csv(user_file_path, sep='::', engine='python', names=[
                       'UserID', 'Gender', 'Age', 'Occupation', 'Zip-code', 'Username', 'Password'], encoding='ISO-8859-1')


# Tạo pivot table từ users
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


# Hàm thực hiện kiểm tra đăng nhập
def check_login(username, password):
    users_df = pd.read_csv(user_file_path, sep='::', engine='python', names=[
        'UserID', 'Gender', 'Age', 'Occupation', 'Zip-code', 'Username', 'Password'], encoding='ISO-8859-1')
    # Kiểm tra xem username và password có tồn tại trong DataFrame users_df hay không
    login_user = users_df[(users_df['Username'] == username)
                          & (users_df['Password'] == password)]
    if not login_user.empty:
        return True  # Đăng nhập thành công
    return False  # Đăng nhập không thành công

# Hàm thực hiện kiểm tra đăng kí


def check_register(Username, Age):
    users_df = pd.read_csv(user_file_path, sep='::', engine='python', names=[
        'UserID', 'Gender', 'Age', 'Occupation', 'Zip-code', 'Username', 'Password'], encoding='ISO-8859-1')
    if users_df['Username'].isin([Username]).any():
        return False  # Tên người dùng đã tồn tại
    # Thực hiện kiểm tra và điều kiện khác tùy thuộc vào yêu cầu của bạn
    if not validate_age(Age):
        return False  # Tuổi không hợp lệ
    return True  # Điều kiện đăng ký đúng

# Kiểm tra tuổi hợp lí


def validate_age(age):
    try:
        age = int(age)
        if age < 0 or age > 150:
            return False  # Tuổi không hợp lệ
    except ValueError:
        return False  # Tuổi không phải là một số nguyên

    return True  # Tuổi hợp lệ

# GET
# Hàm thực hiện lấy danh sách phim


@app.route('/', methods=['GET'])
def init():
    return jsonify({'message': 'Welcome to my prooject'})


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


# Hàm thực hiện nhận request và thực hiện đăng nhập
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if check_login(username, password):
        response = jsonify({'message': 'Đăng nhập thành công !'})
    else:
        response = jsonify({'message': 'Đăng nhập không thành công !'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Hàm thực hiện nhận request và thực hiện đăng kí
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    gender = data.get('gender')
    age = data.get('age')
    occupation = data.get('occupation')
    zip_code = data.get('zip_code')
    users_count = len(users_df)

    # Xử lý logic đăng ký
    if check_register(username, age):
        add_user = f"{users_count + 1}::{gender}::{age}::{occupation}::{zip_code}::{username}::{password}"
        with open(user_file_path, 'a') as file:
            file.write(add_user + '\n')
        response = jsonify({'message': 'Đăng ký thành công'})
    else:
        response = jsonify({'message': 'Đăng ký không thành công!'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Put


# Delete
@app.route('/api/datadelete/<id>', methods=['DELETE'])
def delete_data(id):
    # Xóa tài nguyên có id tương ứng trong cơ sở dữ liệu hoặc xử lý theo nhu cầu
    # ...
    return jsonify({'message': 'DELETE request successful'})
