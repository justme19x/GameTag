from flask import Blueprint,render_template,flash
from flask_login import login_required,current_user
from models import Utilizator,Friendship
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from website_start import db
from models import get_user_id
from games import actualizare_jocuri
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime
from models import db, Postare, Comentariu, Utilizator

views=Blueprint('views',__name__)

class PostareForm(FlaskForm):
    text_postare = TextAreaField('How are you today...', validators=[DataRequired()])
    submit = SubmitField('Post')

class ComentariuForm(FlaskForm):
    text_comentariu = TextAreaField('Write a comment...', validators=[DataRequired()])
    submit = SubmitField('Comment')

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    
    form = PostareForm()
    if form.validate_on_submit():
        postare = Postare(
            text_postare=form.text_postare.data,
            tip_postare="TEXT",
            id_utilizator_postare=current_user.id_utilizator,
            data_postare=datetime.now()
        )
        db.session.add(postare)
        db.session.commit()
        flash('Postarea ta a fost creată!', 'success')
        return redirect(url_for('views.home'))
    
    postari = Postare.query.order_by(Postare.data_postare.desc()).all()
    comentariu_forms = {postare.id_postare: ComentariuForm() for postare in postari}
    return render_template('home.html', form=form, postari=postari, comentariu_forms=comentariu_forms,user=current_user)

@views.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    form = ComentariuForm()
    if form.validate_on_submit():
        comentariu = Comentariu(
            text_comentariu=form.text_comentariu.data,
            id_postare=post_id,
            id_utilizator=current_user.id_utilizator,
            data_comentariu=datetime.now()
        )
        db.session.add(comentariu)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    return redirect(url_for('views.home'))














#profile specifice utilizatori
@views.route('/profile/<int:id_utilizator>', methods=['GET','POST'])
@login_required
def profile(id_utilizator):
    current_user.jocuri=actualizare_jocuri(current_user)
    username_profile= Utilizator.query.get_or_404(id_utilizator)
    return render_template('profile.html',user=current_user)

##tine de base

#profile toti utilizatori
@views.route('/Discover')
@login_required
def list_profiles():
    users = Utilizator.query.all()  
    usernames = [user.username for user in users if user.id_utilizator != current_user.id_utilizator] # excludere current user
    return render_template('profiles.html', usernames=usernames, user=current_user, Utilizator=Utilizator)


# accesare profil
@views.route('/profile/<username>')
@login_required
def profiles(username):
    user = Utilizator.query.filter_by(username=username).first_or_404()
    user_id=get_user_id(username)
    friendship_exists = Friendship.query.filter(
        ((Friendship.id_utilizator_1 == current_user.id_utilizator) & (Friendship.id_utilizator_2 == user_id)) |
        ((Friendship.id_utilizator_1 == user_id) & (Friendship.id_utilizator_2 == current_user.id_utilizator))
    ).first()
    user.jocuri = actualizare_jocuri(user)
    return render_template('profile_interaction.html',  user=user,friendship_exists=friendship_exists)


