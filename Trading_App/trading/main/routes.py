from flask import Blueprint, redirect, render_template, request, url_for, abort
from .forms import SearchForm
from trading.models import Book, Orders
from flask_login import current_user, login_required
from trading.models import User

main = Blueprint('main', __name__)

@main.route('/', methods = ['GET', 'POST'])
def welcome():
	return render_template('welcome.html')
@main.route('/home', methods = ['GET', 'POST'])
def home():
	page = request.args.get('page', 1, type = int)
	books = Book.query.paginate(page = page, per_page = 5)
	return render_template('home.html', title = 'Home', books = books)

@main.route('/about')
def about():
	return render_template('about.html', title = 'About')

@main.route('/view_orders/ba6478ee23c7f173e94a25d92383d179')
@login_required
def view_orders():
	if current_user.username =='GautamPB':
		orders = Orders.query.all()
		return render_template('view_orders.html', orders = orders)
	else:
		abort(403)
	return redirect(url_for('main.home'))

@main.route('/view_users/bca7888fe00850a55774ad87be3902b8')
@login_required
def view_users():
	if current_user.username == 'GautamPB':
		users = User.query.all()
		return render_template('view_users.html', users = users)
	else:
		abort(403)
	return redirect(url_for('main.home'))