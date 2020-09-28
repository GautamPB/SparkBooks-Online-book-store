import os, secrets
from PIL import Image
from trading import mail, app
from trading.models import User
from flask_mail import Message

def save_picture(form_picture):
	randome_hex = secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = randome_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/pictures', picture_fn) #app.root_path determines the directory of the current running application(run.py)

	output_size = (180, 180)
	i = Image.open(form_picture)
	i.thumbnail = (output_size)

	i.save(picture_path)
	return picture_fn

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender = 'noreply@demo.com',
		recipients = [user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token = token, _external = True)}
If you did not make this request, simply ignore this email
'''
	mail.send(msg)