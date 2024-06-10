from flask import Blueprint,render_template,request,redirect,url_for,flash
from datetime import datetime
from models import *
from website_start import db
from flask_login import login_user, login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash 
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired,Email
from sqlalchemy import select


auth=Blueprint('auth',__name__)




@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_pass():
    form=ResetPasswordForm()
    if form.validate_on_submit():
        select_user=select(Utilizator).where(Utilizator.email==form.email.data)
        user = db.session.execute(select_user).fetchone()
        if user:
            flash('A message has been sent to the email address','success')
        else:
            flash('User with this email does not exist', 'error')
    return render_template('reset_password_logout.html',title="Reset Password",user=current_user,form=form)








class ResetPasswordForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired(),Email()])
    submit= SubmitField("Password reset submit")



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        parola=request.form.get('parola')

        user=Utilizator.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.parola, parola):
                flash("Login successfully!",category="success")
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.',category='error')
        else:
            flash('Email does not exist.',category='error')
    return render_template("login.html",user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign_up' ,methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST" :
        username = request.form["username"]
        email = request.form["email"]
        parola = request.form["parola"]
        confirm_password = request.form["confirm_password"]
        data_nasterii = request.form["data_nastere"]
        data_inregistrare = datetime.utcnow()
        locatie = request.form["locatie"]
        Pseudonim = request.form["Pseudonim"]  


        if Utilizator.check_email_exists(email):
            flash('A user with this email already exists!', 'error')
            return redirect(url_for('auth.sign_up'))
        

        #verificare spatii
        if ' ' in username or ' ' in parola:
            flash('Username and password cannot contain spaces. Please try again.', 'error')
            return redirect(url_for('auth.sign_up'))
        
        #verificare lungime
        if len(username) < 4 or len(username) > 20:
            flash('Username must be between 4 and 20 characters long.', 'error')
            return redirect(url_for('auth.sign_up'))
        
        if not username.isalnum() and '_' not in username and '.' not in username:
            flash('Username can only contain letters, numbers, underscore (_) and dot (.)', 'error')
            return redirect(url_for('auth.sign_up'))
        
        if any(pattern in username.lower() for pattern in ['admin', 'root', 'password']):
            flash('Username cannot contain forbidden patterns.', 'error')
            return redirect(url_for('auth.sign_up'))
        
        if len(parola) < 5 or len(parola) > 25:
            flash('Password must be between 5 and 25 characters long.', 'error')
            return redirect(url_for('auth.sign_up'))


        if parola != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('auth.sign_up'))
        
        if ' ' in locatie:
            flash('Country name cannot contain spaces. Please try again.', 'error')
            return redirect(url_for('auth.sign_up'))
        
        if len(locatie) > 25:
            flash('Country name cannot exceed 25 characters.', 'error')
            return redirect(url_for('auth.sign_up'))        




        if parola == confirm_password:

            # Creare obiect Utilizator și adăugare în baza de date
            Utilizator_nou = Utilizator(
            username=username,
            email=email,
            data_nasterii=data_nasterii,
            data_inregistrare=data_inregistrare,
            locatie=locatie,
            Pseudonim=Pseudonim,
            parola=generate_password_hash(parola, method='pbkdf2:sha256')
            )

            # Adăugare și commit pentru a salva noul utilizator în baza de date
            db.session.add(Utilizator_nou)
            db.session.commit()
            login_user(Utilizator_nou, remember=True)
            flash("Account created!",category="success")
            return redirect(url_for('views.home'))

        else:
            flash('Passwords do not match. Please try again.', 'error')


    return render_template("sign_up.html",user=current_user)

