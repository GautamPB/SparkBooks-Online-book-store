from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField

class UploadBookForm(FlaskForm):
	title = StringField('Title')
	author = StringField('Author')
	cover = FileField('Book Cover', validators=[FileAllowed(['jpg', 'png'])])
	price = IntegerField('Price')
	submit = SubmitField('Upload')

class CheckoutForm(FlaskForm):
	address = TextAreaField('Address', validators=[DataRequired()])
	phone = StringField('Phone', validators=[DataRequired()])
	submit = SubmitField('Order')

class CommentForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Post')