from flask import Blueprint,render_template,request,redirect,url_for,flash
from datetime import datetime
from models import Utilizator,Joc,Biblioteca_joc,Friendship,Recenzie
from website_start import db
from flask_login import login_user, login_required,logout_user,current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField,FileField,PasswordField, DateField,TextAreaField,SelectField
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
games=Blueprint('games',__name__)

from recenzie import calculate_reviews,recenzi_cu_text

#afisare games
@games.route('/profile/games')
@login_required
def game_page():
    all_games = Joc.query.all()

    def joc_in_biblioteca(id_Joc):
        """
        def o functie care cauta daca exista jocul in biblioteca_joc pentru current user
        """
        return Biblioteca_joc.query.filter_by(id_joc=id_Joc, id_utilizator=current_user.id_utilizator).first() is not None

    return render_template('games.html', jocuri=all_games, user=current_user, joc_in_biblioteca=joc_in_biblioteca)






#adauga joc in db
@games.route('/add_game_to_library/<int:id_joc>', methods=['POST'])
@login_required
def add_game_to_library(id_joc):
    try:
        joc=Joc.query.get(id_joc)
      

        #dupa ce verifica jocul il adauga in biblioteca
        biblioteca_joc = Biblioteca_joc(
            id_utilizator=current_user.id_utilizator,
            id_joc=id_joc,
            last_played=datetime.now(),
            data_adaugare=datetime.now(),
            play=True
        )
        db.session.add(biblioteca_joc)
        db.session.commit()
        flash("The game has been successfully added to the library!","success")
 
        return redirect(request.referrer)
    except Exception as e:
        flash('Error: ' + str(e), 'error')
        return redirect(request.referrer)




@games.route('/profile/games/delete/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Biblioteca_joc.query.filter_by(id_joc=game_id, id_utilizator=current_user.id_utilizator).first()
    if game:
        db.session.delete(game)
        db.session.commit()
        flash("Game deleted successfully.", 'success')
    else:
        flash("Game not found.", 'error')
    return render_template("games.html",user=current_user,id=game_id)




@games.route('/profile/yourgames')
@login_required
def your_game():
    utilizator_curent = current_user
    """
    afisare your games, cu cautare in biblioteca_joc =>  cauta PLAY == 1 -in partea de front avem nev de el sa afisam caseta
    
    """
    

    # Join Biblioteca_joc si Joc pe id_joc
    your_gamess = Biblioteca_joc.query.join(Joc, Biblioteca_joc.id_joc == Joc.id_Joc).filter(Biblioteca_joc.id_utilizator == utilizator_curent.id_utilizator)

    return render_template("your_game.html",games=your_gamess,user=current_user)



#update status for play - checkbox
@games.route('/update_game_play_status/<int:game_id>', methods=['POST'])
@login_required
def update_game_play_status(game_id):
    game = Biblioteca_joc.query.filter_by(id_joc=game_id, id_utilizator=current_user.id_utilizator).first()
    if game:
        data = request.get_json()
        new_play_status = data.get('play')
        
        # extragem datele din cererea http(cele sub forma JSON)
        if new_play_status == 1:
            game.play = new_play_status
            game.last_played=datetime.now()
            db.session.commit()
            return jsonify({'message': 'Game play status updated successfully'}), 200
        elif new_play_status == 0:
            game.play=new_play_status
            game.last_played=datetime.now()
            db.session.commit()

            
            return jsonify({'message': 'Game play status updated successfully'}), 200
        else:
            flash("Status errorr",'error')
    else:
        return jsonify({'error': 'Game not found'}), 404



def actualizare_jocuri(user):
    jocuri_utilizator = (db.session.query(Joc.nume_joc)
                     .select_from(Biblioteca_joc)
                     .join(Joc, Biblioteca_joc.id_joc == Joc.id_Joc)
                     .filter(Biblioteca_joc.id_utilizator == user.id_utilizator)
                     .filter(Biblioteca_joc.play == True)
                     .all())
    
    #returneaza tupluri doar cu numele jocului
    
    #for el in lista de tupluri ia primul element =joc[0]
    nume_jocuri = [joc[0] for joc in jocuri_utilizator]
    nume_jocuri=', '.join(nume_jocuri)
    return nume_jocuri



@games.route('/info_games/<int:id_joc>', methods=['POST', 'GET'])
@login_required
def view_joc_content(id_joc):
    joc = Joc.query.filter_by(id_Joc=id_joc).first()

    total_reviews, total_likes, total_dislikes, like_percentage, dislike_percentage = calculate_reviews(id_joc)
    
    recenzi_cu_text_var = recenzi_cu_text(id_joc)
    recenzi_pozitive = [(recenzie, get_username(recenzie.id_utilizator)) for recenzie in recenzi_cu_text_var if int(recenzie.Nota) == 1]
    recenzi_negative = [(recenzie, get_username(recenzie.id_utilizator)) for recenzie in recenzi_cu_text_var if int(recenzie.Nota) == 0]

    # Paginare
    page = request.args.get('page', 1, type=int)
    per_page = 5  
    total_pozitive = len(recenzi_pozitive)
    total_negative = len(recenzi_negative)

    
    total_pages_pozitive = (total_pozitive + per_page - 1) // per_page
    total_pages_negative = (total_negative + per_page - 1) // per_page
    total_pages = max(total_pages_pozitive, total_pages_negative)

    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    recenzi_pozitive_paginate = recenzi_pozitive[start_index:end_index]
    recenzi_negative_paginate = recenzi_negative[start_index:end_index]

    if joc:
        content = joc.content
        
        # Lista de utilizatori care au jocul activ
        utilizatori_cu_joc = Utilizator.query.join(Biblioteca_joc).filter(
            Biblioteca_joc.id_joc == id_joc,
            Biblioteca_joc.play == 1
        ).all()
        
        # Lista de prieteni a utilizatorului curent
        prieteni = Friendship.query.filter(((Friendship.id_utilizator_1 == current_user.id_utilizator) |
                                            (Friendship.id_utilizator_2 == current_user.id_utilizator)) &
                                           (Friendship.data_acceptare != None)).all()
        
        # Căutăm prietenii care au jocul activ
        prieteni_cu_joc = []

        for prietenie in prieteni:
            for utilizator in utilizatori_cu_joc:
                if prietenie.id_utilizator_1 == utilizator.id_utilizator or prietenie.id_utilizator_2 == utilizator.id_utilizator:
                    prieteni_cu_joc.append(utilizator)

        # Facem o listă pentru afișare
        rezultat = []

        for utilizator in prieteni_cu_joc:
            rezultat.append({
                "username": utilizator.username,
                #"id_utilizator": utilizator.id_utilizator  -- poate dacă vreau să folosesc mai departe
            })

        return render_template(
            'game_info.html',
            content=content,
            rezultat=rezultat,
            user=current_user,
            joc=joc,
            total_reviews=total_reviews,
            total_likes=total_likes,
            total_dislikes=total_dislikes,
            like_percentage=like_percentage,
            dislike_percentage=dislike_percentage,
            recenzi_pozitive_paginate=recenzi_pozitive_paginate,
            recenzi_negative_paginate=recenzi_negative_paginate,
            page=page,
            total_pages=total_pages
        )  
    else:
        return "The game was not found."