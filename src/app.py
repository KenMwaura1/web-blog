from flask import Flask, render_template, request, session, make_response, jsonify

from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post
from src.models.user import User

app = Flask(__name__)
app.secret_key = "zoo"


@app.route('/', methods=['GET', 'POST'])
def home_template():
    blogs = Database.find(collection='blogs', query=({}))
    if request.method == 'GET':
        return render_template("home.html", blogs=blogs)
    elif request.method == 'POST':
        if session['email'] is not None:
            return make_response(user_home(session['email']))


@app.route('/user/home', methods=['GET', 'POST'])
def user_home(user=None):
    if session['email'] is not None:
        blogs = Database.find(collection='blogs', query=({}))
        user = User.get_by_email(session['email'])
        user_blogs = user.get_blogs()
        return render_template('user_home.html', user=user, blogs=blogs, user_blogs=user_blogs)


@app.route('/home/posts/<string:blog_id>', methods=['GET'])
def home_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()
    return render_template('home_posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id)


@app.route('/home/author/<string:author_id>')
def home_author(author_id):
    blogs = Blog.find_by_author_id(author_id)
    author = [blog.author for blog in blogs]
    author = author[0]
    return render_template('author_blogs.html', blogs=blogs, author=author)


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.before_first_request
def database_initialize():
    Database.initialize()


@app.route('/auth/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if User.login_valid(email, password):
        User.login(email)
    else:
        session['email'] = None
    return render_template("profile.html", email=session['email'])


@app.route("/auth/register", methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']
    User.register(email, password)
    return render_template("profile.html", email=session['email'])


@app.route('/user/logout')
def user_logout(user=None):
    user = User.get_by_email(session['email'])
    user.logout()
    return make_response(home_template())


@app.route('/user/author/<string:author_id>', methods=['GET', 'POST'])
def author_blogs(author_id, ):
    user = User.get_by_id(author_id)
    user_email = User.get_by_email(session['email'])
    user_blogs = user_email.get_blogs()
    blogs = user.get_blogs()
    return render_template('user_author_blogs.html', blogs=blogs, user_blogs=user_blogs)


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])
    blogs = user.get_blogs()
    return render_template("user_blogs.html", blogs=blogs, email=user.email)


@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])
        new_blog = Blog(user.email, user._id, title, description)
        new_blog.save_to_mongo()
        return make_response(user_blogs(user._id))


@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()
    user_email = User.get_by_email(session['email'])
    user_blogs = user_email.get_blogs()
    user_posts = Post.from_blog(blog_id)
    if blog.author == session['email']:
        user_posts = blog.get_posts()
        return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id,
                               user_posts=user_posts, user_blogs=user_blogs)
    else:
        return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id)


@app.route('/blogs/update/<string:blog_id>', methods=['GET', 'POST'])
def update_blog(blog_id):
    if request.method == 'GET':
        return render_template('update_blog.html', blog_id=blog_id)
    else:
        title = request.form['title']
        description = request.form['description']
        existing_blog = Blog.from_mongo(blog_id)
        if str.strip(title) == "":
            title = existing_blog.title
        if str.strip(description) == "":
            description = existing_blog.description
        updated_blog = Blog(existing_blog.author, existing_blog.author_id,
                            title, description, existing_blog._id)
        updated_blog.update_blog(blog_id)
    return make_response(user_blogs())


@app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
def create_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])

        new_post = Post(blog_id, title, content, user.email)
        new_post.save_to_mongo()
        return make_response(blog_posts(blog_id))


@app.route('/posts/del/<string:post_id>', methods=['POST', 'GET'])
def delete_post(post_id):
    post = Post.del_post(post_id)
    return post


@app.route('/posts/update/<string:blog_id>/<string:post_id>', methods=['GET', 'POST'])
# @app.route('/posts/update/<string:post_id>',methods=['GET','POST'])
def update_post(post_id, blog_id):
    if request.method == 'GET':
        return render_template('update_post.html', blog_id=blog_id, post_id=post_id)
    else:
        title = request.form['title']
        content = request.form['content']
        # user = User.get_by_email(session['email'])
        existing_post = Post.from_mongo(post_id)
        if str.strip(title) == "":
            title = existing_post.title
        if str.strip(content) == "":
            content = existing_post.content
        updated_post = Post(existing_post.blog_id, title, content, existing_post.author,
                            existing_post.created_date, existing_post._id)
        updated_post.update_post(post_id)
    return make_response(blog_posts(blog_id))


@app.route('/blogs/del/<string:blog_id>', methods=['POST', 'GET'])
def delete_blog(blog_id):
    blog = Blog.del_blog(blog_id)
    return "Deleted " + blog + "blog"


# API test TODO 1: add authentication for API calls 2: Add POST methods to the api routes
@app.route('/api')
@app.route('/api/')
def api():
    return jsonify(
        status=True,
        message='Welcome to the Zoo blog api!!'
    )


@app.route('/api/blogs')
def blog_api():
    blogs = Database.find(collection='blogs', query=({}))
    item = {}
    data = []
    for blog in blogs:
        item = {
            'id': str(blog['_id']),
            'author': blog['author'],
            'title': blog['title'],
            'description': blog['description'],
        }
        data.append(item)
    return jsonify(
        status=True,
        data=data
    )


@app.route('/api/posts')
def post_api():
    posts = Database.find(collection='posts', query=({}))
    item = {}
    data = []
    for post in posts:
        item = {
            'id': str(post['_id']),
            'author': post['author'],
            'title': post['title'],
            'content': post['content'],
            'blog_id': post['blog_id'],
            'created_date': post['created_date']
        }
        data.append(item)
    return jsonify(
        status=True,
        data=data
    )


if __name__ == '__main__':
    app.run(debug=True)
