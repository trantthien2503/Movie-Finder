from app import app
from flask import Flask, jsonify, request
import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
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

# Danh sách lịch sử tìm kiếm
historySearch_file_path = os.path.join(
    current_dir, 'data', 'historySearch.dat')

historys_df = pd.read_csv(historySearch_file_path, sep='::', engine='python', names=[
    'UserID', 'keyWord'], encoding='ISO-8859-1')
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


# Hàm thực hiện tìm kiếm phim theo đánh giá
def get_movie_suggestions_by_rate(userId, rate, limit):
    # Lọc các xếp hạng theo UserID và xếp hạng đạt ngưỡng rate
    user_ratings = ratings_df[(ratings_df['UserID'] == userId) & (
        ratings_df['Rating'] >= rate)]

    # Liệt kê các ID phim đã được xếp hạng bởi UserID
    movie_ids = user_ratings['MovieID'].unique()

    # Lấy thông tin phim dựa trên ID phim
    movies_by_rate = movies_df[movies_df['MovieID'].isin(movie_ids)]

    # Trích xuất thông tin cần thiết (ID phim, tiêu đề và thể loại)
    movie_list = movies_by_rate[['MovieID', 'Title', 'Genres']].to_dict(
        orient='records')

    # Giới hạn số lượng phim
    limited_movie_list = movie_list[:limit]

    return limited_movie_list


# Hàm thực hiển tìm kiếm phim theo chuổi
def search_movies_by_keyword(keyword):
    # Tìm kiếm phim theo chuỗi trong tiêu đề và thể loại
    matched_movies = movies_df[movies_df['Title'].str.contains(
        keyword, case=False) | movies_df['Genres'].str.contains(keyword, case=False)]
    # Trả về danh sách phim kết quả
    return matched_movies[['MovieID', 'Title', 'Genres']].to_dict(orient='records')


# Hàm thực hiện tìm kiếm phim theo danh chuỗi đa tìm kiếm
def search_movies_by_keywords(keywords):
    # Tìm kiếm phim dựa trên mảng các chuỗi tìm kiếm trong tiêu đề và thể loại
    matched_movies = movies_df[movies_df.apply(lambda row: any(
        keyword in row['Title'] or keyword in row['Genres'] for keyword in keywords), axis=1)]

    # Trả về danh sách phim kết quả
    return matched_movies[['MovieID', 'Title', 'Genres']].to_dict(orient='records')


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

# Hàm thực hiện lấy danh sách user


def getUsers(limit):
    return users_df.head(limit).to_dict(orient='records')


def getUserById(user_id):
    user = users_df[users_df['UserID'] == user_id].to_dict(orient='records')
    if len(user) > 0:
        return user[0]
    else:
        return {"message": "User not found"}


# GET
@ app.route('/', methods=['GET'])
def init():
    return jsonify({'message': 'Welcome to my prooject'})

# Hàm thực hiện lấy danh sách phim


@ app.route('/api/get-moives', methods=['GET'])
def get_movies():
    # Chuyển đổi DataFrame thành định dạng JSON
    movies_json = movies_df.to_json(orient='records')
    response = jsonify(movies_json)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Hàm thực hiện lấy danh sách phim theo userId
@ app.route('/api/get-movies-byuserid/<int:userId>', methods=['GET'])
def get_moives_byUserId(userId):
   # Lấy danh sách phim theo userId
    suggested_movies = get_movie_suggestions(userId)
    # Tạo response với dữ liệu JSON
    response = jsonify(suggested_movies)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# POST
# Hàm thực hiện nhận request và thực hiện đăng nhập


@ app.route('/api/login', methods=['POST'])
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
@ app.route('/api/register', methods=['POST'])
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


# Hàm thực hiện trả về danh sách gợi ý theo Đánh giá UserID và Rating
@ app.route('/api/suggest-rate', methods=['POST'])
def suggestRate():
    data = request.get_json()
    userId = data.get('userId')
    rate = data.get('rate')  # rate đánh giá 1-5
    limit = int(data.get('limit'))  # limit giới hạn danh sách phim
    response = jsonify(get_movie_suggestions_by_rate(userId, rate, limit))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Hàm thực hiện trả về danh sách phim theo chuỗi tìm kiếm
@ app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    userId = data.get('userId')
    keyWord = data.get('keyWord')  # keyWord: chuỗi tìm kiếm
    history_search = f"{userId}::{keyWord}"  # Ghi vào file lịch sử tìm kiếm
    with open(historySearch_file_path, 'a') as file:
        file.write(history_search + '\n')
    response = jsonify(search_movies_by_keyword(keyWord))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Hàm thực hiện lấy danh sách phim dựa trên kết quả đã tìm kiếm


@ app.route('/api/search-history-keywords', methods=['POST'])
def get_search_history_keywords():
    data = request.get_json()
    userId = data.get('userId')
    filtered_keywords = historys_df[historys_df['UserID']
                                    == userId]['keyWord'].tolist()
    response = jsonify(search_movies_by_keywords(filtered_keywords))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Hàm thực hiện lấy danh sách users
@ app.route('/api/users', methods=['POST'])
def get_users():
    data = request.get_json()
    limit = data.get('limit')
    # Tạo response với dữ liệu JSON
    response = jsonify(getUsers(limit))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Hàm thực hiện lấy user theo id
@ app.route('/api/user', methods=['POST'])
def get_user():
    data = request.get_json()
    userId = data.get('userId')
    # Tạo response với dữ liệu JSON
    response = jsonify(getUserById(userId))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Put


# Delete
@ app.route('/api/datadelete/<id>', methods=['DELETE'])
def delete_data(id):
    # Xóa tài nguyên có id tương ứng trong cơ sở dữ liệu hoặc xử lý theo nhu cầu
    # ...
    return jsonify({'message': 'DELETE request successful'})
