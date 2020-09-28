from trading import db, login_manager, app
from flask_login import UserMixin #for functions like current_user, user_anonymous etc
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader #to load the user with the ID
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer(), primary_key = True)
	username = db.Column(db.String(20), unique = True, nullable = False)
	email = db.Column(db.String(120), unique = True, nullable = False)
	image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
	password = db.Column(db.String(20), nullable = False)

	def get_reset_token(self, expires_sec = 1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8') #creates a token associated with the user who requested

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.id}', '{self.username}', '{self.image_file}')"

class Book(db.Model):
	id = db.Column(db.Integer(), primary_key = True)
	name = db.Column(db.String(100), nullable = False)
	author = db.Column(db.String(50), nullable = False)
	cover = db.Column(db.String(20), nullable = False, default = 'default.png')
	price = db.Column(db.Integer(), nullable = False)

	def __repr__(self):
		return f"Book('{self.id}', '{self.name}', '{self.cover}')\n"

class Orders(db.Model):
	id = db.Column(db.Integer(), primary_key = True)
	user_name = db.Column(db.String(100), nullable = False)
	email = db.Column(db.String(120), nullable = False)
	book_title = db.Column(db.String(120), nullable = False)
	address = db.Column(db.String(200), nullable = False)
	phone = db.Column(db.Float(), nullable = False)
	book_price = db.Column(db.Integer(), nullable = False)

	def __repr__(self):
		return f"Order('{self.id}', '{self.user_name}', '{self.book_title}', '{self.book_price}')"

class Comments(db.Model):
	id = db.Column(db.Integer(), primary_key = True)
	book_id = db.Column(db.Integer())
	username = db.Column(db.String(120), nullable = False)
	pfp = db.Column(db.String(120), nullable = False)
	title = db.Column(db.String(100), nullable = False)
	content = db.Column(db.String(500), nullable = False)

	def __repr__(self):
		return f"Comment '{self.title}', '{self.book_id}'"