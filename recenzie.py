from flask import Blueprint,render_template,request,redirect,url_for,flash
from datetime import datetime
from models import Utilizator,Joc,Biblioteca_joc,Friendship,Recenzie
from website_start import db
from flask_login import login_user, login_required,logout_user,current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField,FileField,PasswordField, DateField,TextAreaField,SelectField,RadioField, BooleanField
from wtforms.validators import DataRequired
from wtforms.validators import (DataRequired,EqualTo,Length)
from flask_wtf.recaptcha import RecaptchaField
from werkzeug.security import check_password_hash, generate_password_hash
from models import get_username  
from models import get_user_id 
from sqlalchemy import and_
from sqlalchemy import exists
from flask import jsonify
from sqlalchemy import or_
from wtforms import IntegerField
from wtforms.validators import NumberRange
recenzie=Blueprint('recenzie',__name__)


def calculate_reviews(game_id):
    total_reviews = Recenzie.query.filter_by(id_joc=game_id).count()
    total_likes = Recenzie.query.filter_by(id_joc=game_id, Nota=1).count()
    total_dislikes = Recenzie.query.filter_by(id_joc=game_id, Nota=0).count()

    if total_reviews != 0:
        like_percentage = round((total_likes / total_reviews) * 100)
        dislike_percentage = 100 - like_percentage
    else:
        like_percentage = 0
        dislike_percentage = 0

    return total_reviews, total_likes, total_dislikes, like_percentage, dislike_percentage

def recenzi_cu_text(game_id):
    recenzi = Recenzie.query.filter(Recenzie.id_joc == game_id, Recenzie.text_recenzie != '').all()
    return recenzi

class GameReviewForm(FlaskForm):
    text_recenzie = TextAreaField('Review text(optional): ')
    
@recenzie.route('/profile/games/review/<int:game_id>', methods=['GET','POST'])
@login_required
def join_game(game_id):
    game=Joc.query.filter_by(id_Joc=game_id).first()
    form = GameReviewForm()
    existing_review = Recenzie.query.filter_by(id_utilizator=current_user.id_utilizator, id_joc=game_id).first()
    total_reviews, total_likes, total_dislikes, like_percentage, dislike_percentage = calculate_reviews(game_id)
        
    # Adăugăm paginarea
    page = request.args.get('page', 1, type=int)
    per_page = 5
    recenzi_cu_text_var = recenzi_cu_text(game_id)
    recenzi_pozitive = [(recenzie, get_username(recenzie.id_utilizator)) for recenzie in recenzi_cu_text_var if int(recenzie.Nota) == 1]
    recenzi_negative = [(recenzie, get_username(recenzie.id_utilizator)) for recenzie in recenzi_cu_text_var if int(recenzie.Nota) == 0]
    
    total_combinate = len(recenzi_pozitive) + len(recenzi_negative)
    total_pages = (total_combinate + per_page - 1) // per_page
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    recenzi_paginate = recenzi_pozitive[start_index:end_index] + recenzi_negative[start_index:end_index]
    recenzi_pozitive_paginate = [r for r in recenzi_paginate if r in recenzi_pozitive]
    recenzi_negative_paginate = [r for r in recenzi_paginate if r in recenzi_negative]

    if existing_review:
        flash('You have already submitted a review for this game.', 'warning')
        return render_template('gamesjoinn.html', game_id=game_id, user=current_user, game=game,
                               total_reviews=total_reviews, total_likes=total_likes, total_dislikes=total_dislikes,
                               like_percentage=like_percentage, dislike_percentage=dislike_percentage,
                               recenzi_pozitive_paginate=recenzi_pozitive_paginate, recenzi_negative_paginate=recenzi_negative_paginate,
                               page=page, total_pages=total_pages)



    if form.validate_on_submit():
        like_dislike = request.form.get('like_dislike')
        if like_dislike is None:
            flash('Please select either like or dislike.', 'warning')
            return render_template('gamesrecenzie.html', user=current_user, game_id=game_id, form=form)
        else:
            like_dislike = request.form.get('like_dislike')
            text_recenzie = form.text_recenzie.data
            data_recenzie = datetime.now()
            Recenzie_noua = Recenzie(id_utilizator=current_user.id_utilizator, id_joc=game_id, text_recenzie=text_recenzie, Nota=like_dislike, data_recenzie=data_recenzie)
            db.session.add(Recenzie_noua)
            db.session.commit()
            flash("The review was done successfully")
            return redirect(url_for('recenzie.game', game_id=game_id,user=current_user))  
        
        
    return render_template("gamesrecenzie.html", user=current_user, game_id=game_id, form=form,game=game)


@recenzie.route('/profile/games/join/<int:game_id>', methods=['GET', 'POST'])
@login_required
def game(game_id):
    total_reviews, total_likes, total_dislikes, like_percentage, dislike_percentage = calculate_reviews(game_id)
    page = request.args.get('page', 1, type=int)
    per_page = 5

    
    recenzi_cu_text_var = recenzi_cu_text(game_id)
    recenzi_pozitive = [(recenzie, get_username(recenzie.id_utilizator)) for recenzie in recenzi_cu_text_var if int(recenzie.Nota) == 1]
    recenzi_negative = [(recenzie, get_username(recenzie.id_utilizator)) for recenzie in recenzi_cu_text_var if int(recenzie.Nota) == 0]

    
    total_combinate = len(recenzi_pozitive) + len(recenzi_negative)
    total_pages = (total_combinate + per_page - 1) // per_page

    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    recenzi_paginate = recenzi_pozitive[start_index:end_index] + recenzi_negative[start_index:end_index]

    
    recenzi_pozitive_paginate = [r for r in recenzi_paginate if r in recenzi_pozitive]
    recenzi_negative_paginate = [r for r in recenzi_paginate if r in recenzi_negative]

    game = Joc.query.filter_by(id_Joc=game_id).first()
    chat = game.chat if game.chat else None

    return render_template(
        "gamesjoinn.html",
        user=current_user,
        game_id=game_id,
        game=game,
        total_reviews=total_reviews,
        total_likes=total_likes,
        total_dislikes=total_dislikes,
        like_percentage=like_percentage,
        dislike_percentage=dislike_percentage,
        recenzi_pozitive_paginate=recenzi_pozitive_paginate,
        recenzi_negative_paginate=recenzi_negative_paginate,
        page=page,
        total_pages=total_pages,
        chat=chat
    )



@recenzie.route('/profile/games/review_edit/<int:game_id>', methods=['GET', 'POST'])
@login_required
def recenzie_edit(game_id):

    game=Joc.query.filter_by(id_Joc=game_id).first()
    review = Recenzie.query.filter_by(id_joc=game_id, id_utilizator=current_user.id_utilizator).first_or_404()
    if request.method == 'POST':
        text_recenzie = request.form['text_recenzie']
        like_dislike = int(request.form['like_dislike'])

        review.text_recenzie = text_recenzie
        review.Nota = like_dislike
        db.session.commit()
        return redirect(url_for('recenzie.game', game_id=review.id_joc,user=current_user,game=game)) 

    form = GameReviewForm(obj=review)
    form.text_recenzie.data = review.text_recenzie
    return render_template("recenzie_edit.html", user=current_user, review=review, form=form,game=game)






