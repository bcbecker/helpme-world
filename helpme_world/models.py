from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from helpme_world import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    """
    User loader callback for session
    """
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    replies = db.relationship('Reply', backref='reply_author', lazy=True)

    def get_reset_token(self, expires_sec=600):
        """
        Serializes token, returns json
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """
        Confirms valid token for password reset
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    replies = db.relationship('Reply', backref='post_reply_to', lazy=True, cascade="all, delete")

    @staticmethod
    def get_top_posts():
        """
        Returns mapping of posts with most replies, in descending order
        """
        query = db.session.query(
            Post.id, Post.title, User.username, User.image_file,
            db.func.count(Reply.post_id).label("reply_count"))\
                .join(Reply, Reply.post_id == Post.id)\
                    .group_by(Post.id, User.username, User.image_file, Reply.post_id)\
                .join(User, User.id == Post.user_id)\
                    .order_by(db.func.count(Reply.post_id)\
                        .desc()).limit(3)
        return db.session.execute(query).mappings()

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Reply('{self.content}', '{self.date_posted}')"