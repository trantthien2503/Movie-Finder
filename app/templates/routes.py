from app import app
from flask import Flask, render_template, request
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load dữ liệu từ file .dat
movies_df = pd.read_csv('C:\\Users\\THIETKE\\Desktop\\dev\\Movie-Finder\\app\\data\\movies.dat',
                        sep='::', engine='python', names=['MovieID', 'Title', 'Genres'], encoding='ISO-8859-1')
ratings_df = pd.read_csv('C:\\Users\\THIETKE\\Desktop\\dev\\Movie-Finder\\app\\data\\ratings.dat',
                         sep='::', engine='python', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], encoding='ISO-8859-1')

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


@app.route('/')
def index():
    return render_template('index.html')

# Route cho gợi ý phim


@app.route('/suggest', methods=['POST'])
def suggest():
    print("request.form['userId'] ", request.form['userId'])
    userId = int(request.form['userId'])
    suggestions = get_movie_suggestions(userId)
    if suggestions:
        # Xử lý khi danh sách phim gợi ý không rỗng
        return render_template('index.html', suggestions=suggestions)
    else:
        return render_template('index.html')


@app.route('/about')
def about():
    return "Giới thiệu"


@app.route('/search')
def search():
    return "Tìm kiếm"


@app.route('/html')
def html():
    return "HTML"
