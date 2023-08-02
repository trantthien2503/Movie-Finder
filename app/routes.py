from app import app

@app.route('/')
def index():
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