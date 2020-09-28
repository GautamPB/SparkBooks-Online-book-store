from trading import db, mail
from flask import Blueprint, redirect, render_template, flash, url_for, request, abort
from trading.models import Book, Orders, User, Comments
from .forms import UploadBookForm, CheckoutForm, CommentForm
from flask_mail import Message
from flask_login import current_user, login_required
from trading.users.utils import save_picture

books = Blueprint('books', __name__)

@books.route('/upload_books', methods = ['GET', 'POST'])
@login_required
def upload():
	if current_user.username == 'GautamPB':
		form = UploadBookForm()
		if form.validate_on_submit():
			book = Book(name = form.title.data, author = form.author.data, price = form.price.data, cover = save_picture(form.cover.data))
			db.session.add(book)
			db.session.commit()
			return redirect(url_for('main.home'))
	else:
		abort(403)
	return render_template('upload_book.html', form = form, title = 'Upload Book')

@books.route('/books/<string:data>', methods = ['GET', 'POST'])
def display_books(data):
	page = request.args.get('page', 1, type = int)
	books = Book.query.filter_by(author = data).paginate(page = page, per_page = 5)
	return render_template('books.html', title = data, books = books, author = data)

@books.route('/single_book/<int:book_id>')
def display_single_book(book_id):
	book = Book.query.filter_by(id = book_id).first()
	comments = Comments.query.filter_by(book_id = book_id)
	return render_template('single_book.html', book = book, comments = comments)

@books.route('/add_comment/<int:book_id>', methods = ['GET', 'POST'])
@login_required
def write_comment(book_id):
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comments(book_id = book_id, username = current_user.username,
			title = form.title.data, content = form.content.data, pfp = current_user.image_file)
		db.session.add(comment)
		db.session.commit()
		return redirect(url_for('books.display_single_book', book_id = book_id))
	return render_template('write_comment.html', form = form, title = 'Comment')

@books.route("/book/<int:comment_id>/delete", methods = ['GET', 'POST'])
@login_required
def delete_comment(comment_id):
	comment = Comments.query.get_or_404(comment_id)
	if current_user.username == comment.username:
		db.session.delete(comment)
		db.session.commit()
		flash('Your comment has been deleted successfully!', 'success')
		return redirect(url_for('main.home'))
	else:
		abort(403)

def send_order_email(order, user_email):
	msg = Message('Order Confirmation', sender='sparkbooks735@gmail.com', recipients=[user_email])
	msg.body = f'''We thank you for order, details of which are given below:

{order.book_title} to {order.user_name} for the price of ₹{order.book_price + 45}
to be delivered to:

{order.address}

Your order will be delivered within 3 days.
We accept only cash-on-delivery.
We request your cooperation to tender exact change to our delivery boy.

Thank you for shopping with us.
'''
	mail.send(msg)

def validate_phone_number(phone):
	validated = False
	count = 0
	if len(phone) == 10 and phone.isnumeric():
		validated = True
	return validated

@books.route('/buy_book/<int:id>', methods = ['GET', 'POST'])
@login_required
def buy_book(id):
	form = CheckoutForm()
	book = Book.query.filter_by(id = id).first()
	if form.validate_on_submit():
		address = form.address.data
		phone = form.phone.data
		if validate_phone_number(phone):
			order = Orders(user_name = current_user.username, email = current_user.email, 
			book_title = book.name, address = address, phone = phone, book_price = book.price)
			db.session.add(order)
			db.session.commit()
			send_order_email(order, current_user.email)
			return render_template('purchased.html', address = address, phone = phone, book = book)
		else:
			flash('The phone number you entered was invalid! Please try again.', 'danger')
			return redirect(url_for('books.display_single_book', book_id = id))
	return render_template('checkout.html', form = form, book = book)

@books.route('/all_books')
def display_all_books():
	page = request.args.get('page', 1, type = int)
	books = Book.query.paginate(page = page, per_page = 10)
	return render_template('all_books.html', books = books, title = 'Books')

def send_delete_order_mail(order, user_email):
	msg = Message('Delete Order Confirmation Mail', sender = 'noreply@demo.com', recipients=[user_email])
	msg.body = f'''As per your request, we confirm having cancelled the following order:
{order.book_title}

Feel free to check out our other selections of books.
Thank you for shopping with us.'''
	mail.send(msg)


@books.route("/delete/<int:order_id>", methods = ['GET', 'POST'])
@login_required
def delete_order(order_id):
	order = Orders.query.get(order_id)
	if current_user.username != order.user_name:
		abort(403)
	db.session.delete(order)
	db.session.commit()
	send_delete_order_mail(order, current_user.email)
	flash("Your order has been deleted!", 'success')
	return redirect(url_for('main.home'))