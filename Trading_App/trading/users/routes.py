import os, secrets
from PIL import Image
from trading import bcrypt, db, mail
from flask import redirect, render_template, request, url_for, flash, Blueprint, abort
from flask_login import login_required, login_user, logout_user, current_user
from .forms import (LoginForm, RegisterForm, UpdateAccountForm, ChangePasswordForm,
			RequestResetForm, ResetPasswordForm)
from trading.models import User, Orders
from flask_mail import Message
from .utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route('/login', methods = ['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			flash(f'Successfully logged in as {user.username}!', 'success')
			next_page = request.args.get('next') #get returns none if next doesn't exist
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Please check username and password and try again', 'danger')
	return render_template('login.html', title = 'User Login', form = form)

@users.route('/register', methods = ['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegisterForm()
	if form.validate_on_submit():
		hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username = form.username.data, email = form.email.data, password = hashed_pw)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created for {form.username.data}. You can now login', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title = 'Register', form = form)

@users.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out', 'success')
	return redirect(url_for('main.home'))

@users.route('/profile/<string:user>')
@login_required
def profile(user):
	image_file = url_for('static', filename = 'pictures/' + current_user.image_file)
	return render_template('profile.html', title = 'User Profile', image_file = image_file)

@users.route('/update/<string:user>', methods = ['GET', 'POST'])
@login_required
def update_account(user):
	if current_user.username == user:
		form = UpdateAccountForm()
		if form.validate_on_submit():
			if form.picture.data:
				picture_file = save_picture(form.picture.data)
				current_user.image_file = picture_file

			current_user.username = form.username.data
			current_user.email = form.email.data
			db.session.commit()
			return redirect(url_for('users.profile', user = current_user.username))

		elif request.method == 'GET':
			form.username.data = current_user.username
			form.email.data = current_user.email
	else:
		abort(403)
	return render_template('update_account.html', title = 'Update', form = form)

@users.route('/change_password/<string:user>', methods = ['GET', 'POST'])
@login_required
def change_password(user):
	if current_user.username == user:
		form = ChangePasswordForm()
		if form.validate_on_submit():
			if bcrypt.check_password_hash(current_user.password, form.old_password.data):
				hashed_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
				current_user.password = hashed_pw
				db.session.commit()
				flash('Your password was changed successfully!', 'success')
				return redirect(url_for('main.home'))
			else:
				flash('Check old password and try again', 'danger')
	else:
		abort(403)
	return render_template('change_password.html', form = form)

@users.route('/my_orders/<string:user>')
@login_required
def my_orders(user):
	orders = Orders.query.filter_by(user_name = user)
	return render_template('my_orders.html', orders = orders, n = Orders.query.count())

@users.route('/reset_password', methods = ['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', form = form, title = 'Reset Password')

@users.route('/reset_password/<string:token>', methods = ['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token! Please try again.', 'warning')
		return redirect(url_for('users.reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Your password was changed successfully! You can now login', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_password.html', title = 'Reset Password', form = form)