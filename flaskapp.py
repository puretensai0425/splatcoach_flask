import json, time
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Solomon0425$'
app.config['MYSQL_DB'] = 'db_splatch'
mysql = MySQL(app)

@app.route("/")
def hello():
    return "Welcome to Flask Application!"

@app.route('/posts', methods=['GET'])
def get_posts():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * from tbl_posts''')
    result = cursor.fetchall()
    posts = []
    for row in result:
        post = { 'id': row[0], 'code': row[1], 'comment': row[2], 'userId': row[3] }
        posts.append(post)

    cursor.close()

    return jsonify(posts)

@app.route('/post', methods=["POST"])
def create_post():
    cursor = mysql.connection.cursor()
    try:
        code = request.json['code']
        comment = request.json['comment']
        userId = request.json['userId']

        cursor.execute('''insert into tbl_posts values (DEFAULT, %s, %s, %s)''', (code, comment, userId))
        mysql.connection.commit()

        id = cursor.lastrowid
        post = { 'id': id, 'code': code, 'comment': comment, 'userId': int(userId) }

        cursor.close()
    except:
        post = { 'id': -1, 'code': '', 'comment': '', 'userId': -1 }

    return jsonify(post)


@app.route('/post/<int:id>', methods=['GET'])
def get_post(id: int):
    cursor = mysql.connection.cursor()

    cursor.execute('''SELECT * from tbl_posts WHERE id=%s''', (id,))
    row = cursor.fetchone()
    post = { 'id': row[0], 'code': row[1], 'comment': row[2], 'userId': row[3] }

    userId = row[3]
    cursor.execute('''SELECT * from tbl_users WHERE id=%s''', (userId,))
    row = cursor.fetchone()
    user = { 'id': row[0], 'name': row[2], 'email': row[3], 'photoUrl': row[4], 'comment': row[5] }

    cursor.execute('''SELECT * from tbl_reviews WHERE post_id=%s''', (id,))
    result = cursor.fetchall()
    reviews = []
    for row in result:
        rowUserId = row[1]
        cursor.execute('''SELECT * from tbl_users WHERE id=%s''', (rowUserId,))
        rowUser = cursor.fetchone()
        userName = rowUser[2]

        review = {'id': row[0], 'userId': row[1], 'postId': row[2], 'point': row[3], 'comment': row[4], 'userName': userName, 'photoUrl': rowUser[4]}
        reviews.append(review)

    result = {
        'post': post,
        'user': user,
        'reviews': reviews,
    }
    cursor.close()

    return jsonify(result)

@app.route('/user/posts/<int:id>', methods=['GET'])
def get_user_posts(id: int):
    cursor = mysql.connection.cursor()

    cursor.execute('''SELECT * from tbl_posts WHERE user_id=%s''', (id,))
    result = cursor.fetchall()
    posts = []
    for row in result:
        post = { 'id': row[0], 'code': row[1], 'comment': row[2], 'userId': row[3] }
        posts.append(post)

    cursor.close()

    return jsonify(posts)

@app.route('/user/reviews/<int:id>', methods=['GET'])
def get_user_reviews(id: int):
    cursor = mysql.connection.cursor()

    cursor.execute('''SELECT r1.* from tbl_reviews r1 left join tbl_posts p1 ON r1.post_id=p1.id WHERE p1.user_id=%s''', (id,))
    result = cursor.fetchall()

    reviews = []
    for row in result:
        rowUserId = row[1]
        cursor.execute('''SELECT * from tbl_users WHERE id=%s''', (rowUserId,))
        rowUser = cursor.fetchone()
        userName = rowUser[2]

        review = {'id': row[0], 'userId': row[1], 'postId': row[2], 'point': row[3], 'comment': row[4], 'userName': userName}
        reviews.append(review)

    return jsonify(reviews)


@app.route('/review', methods=["POST"])
def create_review():
    cursor = mysql.connection.cursor()
    try:
        point = request.json['point']
        comment = request.json['comment']
        userId = request.json['userId']
        postId = request.json['postId']

        cursor.execute('''insert into tbl_reviews values (DEFAULT, %s, %s, %s, %s)''', (userId, postId, point, comment))
        mysql.connection.commit()

        id = cursor.lastrowid
        review = { 'id': id, 'point': int(point), 'comment': comment, 'userId': int(userId), 'postId': int(postId), 'userName': '', }

    except:
        review = { 'id': -1, 'point': -1, 'comment': '', 'userId': -1, postId: -1, 'userName': '', }       
    cursor.close()

    return jsonify(review)


@app.route('/follows/<int:id>/<int:loginId>', methods=['GET'])
def get_follows_by_user(id: int, loginId: int):
    cursor = mysql.connection.cursor()

    cursor.execute('''SELECT * from tbl_followers WHERE user_id=%s''', (id,))
    result = cursor.fetchall()
    followings = []
    for row in result:
        rowUserId = row[2]
        cursor.execute('''SELECT * from tbl_users WHERE id=%s''', (rowUserId,))
        rowUser = cursor.fetchone()

        cursor.execute('''SELECT * from tbl_followers WHERE user_id=%s AND follower_id=%s''', (loginId, rowUserId,))
        rowFollow = cursor.fetchone()

        if rowFollow is not None:
            following = rowFollow[3]
        else:
            following = 0

        if rowUser[5] == None:
            comment = ''
        else:
            comment = rowUser[5]

        following = {'id': rowUser[0], 'name': rowUser[2], 'photoUrl': rowUser[4], 'comment': comment, 'following': following}
        followings.append(following)


    cursor.execute('''SELECT * from tbl_followers WHERE follower_id=%s''', (id,))
    result = cursor.fetchall()
    followers = []
    for row in result:
        rowUserId = row[1]
        cursor.execute('''SELECT * from tbl_users WHERE id=%s''', (rowUserId,))
        rowUser = cursor.fetchone()

        cursor.execute('''SELECT * from tbl_followers WHERE user_id=%s AND follower_id=%s''', (loginId, rowUserId,))
        rowFollow = cursor.fetchone()

        if rowFollow is not None:
            following = rowFollow[3]
        else:
            following = 0

        if rowUser[5] == None:
            comment = ''
        else:
            comment = rowUser[5]

        follower = {'id': rowUser[0], 'name': rowUser[2], 'photoUrl': rowUser[4], 'comment': comment, 'following': following}
        followers.append(follower)
    
    result = {
        'followings': followings,
        'followers': followers,
    }

    return jsonify(result)


@app.route('/follow', methods=["POST"])
def create_follow():
    userId = request.json['userId']
    followerId = request.json['followerId']

    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * from tbl_followers WHERE user_id=%s AND follower_id=%s''', (userId, followerId,))
    follower = cursor.fetchone()

    if follower is not None:
        following = follower[3]
        ret_following = 1 - following
        cursor.execute('''update tbl_followers set following=%s WHERE user_id=%s AND follower_id=%s''', (ret_following, userId, followerId))
    else:
        ret_following = 1
        cursor.execute('''insert into tbl_followers values (DEFAULT, %s, %s, DEFAULT)''', (userId, followerId))

    mysql.connection.commit()

    result = {
        'userId': userId, 
        'followerId': followerId,
        'following': ret_following,
    }
    return jsonify(result)

@app.route('/user/<int:id>/<int:loginId>', methods=['GET'])
def get_user(id: int, loginId: int):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * from tbl_users WHERE id=%s''', (id,))
    user = cursor.fetchone()

    cursor.execute('''SELECT * from tbl_followers WHERE user_id=%s AND follower_id=%s''', (loginId, id,))
    rowFollow = cursor.fetchone()
    if rowFollow is not None:
        following = rowFollow[3]
    else:
        following = 0
    
    cursor.execute('''SELECT COUNT(*) from tbl_followers WHERE user_id=%s AND following=1''', (id,))
    followingCnt = cursor.fetchone()[0]

    cursor.execute('''SELECT COUNT(*) from tbl_followers WHERE follower_id=%s AND following=1''', (id,))
    followerCnt = cursor.fetchone()[0]
    
    if user[5] == None:
        comment = ''
    else:
        comment = user[5]

    result = {
        'id': user[0], 'name': user[2], 'photoUrl': user[4], 'comment': comment, 'following': following, 'followingCnt': followingCnt, 'followerCnt': followerCnt
    }

    return jsonify(result)
    
@app.route('/profile', methods=["POST"])
def update_profile():
    cursor = mysql.connection.cursor()
    try:
        userId = request.json['userId']
        name = request.json['name']

        cursor.execute('''update tbl_users set name=%s WHERE id=%s''', (name, userId))
        mysql.connection.commit()

        cursor.execute('''SELECT * from tbl_users WHERE id=%s''', (userId,))
        user = cursor.fetchone()

        result = { 'id': user[0], 'name': user[2], 'photoUrl': user[4], 'comment': user[5] }
    except:
        result = { 'id': -1, 'name': '', 'comment': '' }

    cursor.close()
    return jsonify(result)

@app.route('/register', methods=["POST"])
def register():
    cursor = mysql.connection.cursor()
    try:
        email = request.json['email']
        displayName = request.json['displayName']
        photoUrl = request.json['photoUrl']
        g_id = request.json['id']

        cursor.execute('''SELECT * from tbl_users WHERE email LIKE %s''', (email,))
        user = cursor.fetchone()

        if user is not None:
            id = user[0]
            # cursor.execute('''update tbl_users set name=%s, photo_url=%s WHERE id=%s''', (displayName, photoUrl, id))
            cursor.execute('''update tbl_users set photo_url=%s WHERE id=%s''', (photoUrl, id))
            mysql.connection.commit()

            result = { 'id': id, 'name': displayName, 'photoUrl': photoUrl, 'comment': user[5] }
        else:
            cursor.execute('''insert into tbl_users values (DEFAULT, %s, %s, %s, %s, DEFAULT)''', (g_id, displayName, email, photoUrl))
            mysql.connection.commit()

            id = cursor.lastrowid
            result = { 'id': id, 'name': displayName, 'photoUrl': photoUrl, 'comment': '' }

    except:
        result = { 'id': -1, 'name': '', 'photoUrl': '', 'comment': '' }

    cursor.close()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
