from flask import Blueprint,render_template,flash,request,redirect,url_for
from flask_login import login_required,current_user
from models import Utilizator,Friendship,Notification
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from website_start import db
from sqlalchemy import and_,or_
from models import get_username,get_user_id
friends=Blueprint('friends',__name__)

#afisare prietenii
@friends.route('/friends')
@login_required
def friends_list():
    friends = Friendship.query.filter(or_(
        and_(
            Friendship.id_utilizator_1 == current_user.id_utilizator,
            Friendship.data_acceptare != None
        ),
        and_(
            Friendship.id_utilizator_2 == current_user.id_utilizator,
            Friendship.data_acceptare != None
        )
    )).all()



    return render_template('friends_profile.html',user=current_user,friends=friends,get_username=get_username)


# ruta for friends req
@friends.route('/add_friend/<username>',methods=['POST'])
@login_required
def add_friend(username):
    
    utilizator_curent = current_user 
    utilizator_destinatar = Utilizator.query.filter_by(username=username).first()


    # verificare existenta 
    existing_request = Friendship.query.filter(
        (Friendship.id_utilizator_1 == utilizator_curent.id_utilizator) &
        (Friendship.id_utilizator_2 == utilizator_destinatar.id_utilizator)
    ).first()



    if Friendship.id_utilizator_1 != Friendship.id_utilizator_2:
        if not existing_request:
            new_friendship = Friendship(
                id_utilizator_1=utilizator_curent.id_utilizator,
                id_utilizator_2=utilizator_destinatar.id_utilizator,
                data_cerere=datetime.utcnow()  # Data cererii este momentul curent
            )

            db.session.add(new_friendship)
            db.session.commit()

            new_notification = Notification(
            id_utilizator=utilizator_destinatar.id_utilizator,  
            info="Friends",
            created_at=datetime.utcnow(),
            friendship=new_friendship
            )
            db.session.add(new_notification)
            db.session.commit()



            return redirect(request.referrer)
        else:
            return render_template('profile.html', user=current_user) #ce returneaza daca sunt prietenii
    else:
        print("Error: The user cannot be friends with himself.")





# ruta for delete friend
@friends.route('/friends/delete/<username>',methods=['POST'])
@login_required
def delete_friend(username):
    friend_id=get_user_id(username)
    friendship = Friendship.query.filter(
        (Friendship.id_utilizator_1 == current_user.id_utilizator) &
        (Friendship.id_utilizator_2 == friend_id) |
        (Friendship.id_utilizator_1 == friend_id) &
        (Friendship.id_utilizator_2 == current_user.id_utilizator)
    ).first()

    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash('Friend successfully deleted', 'success')
    else:
        flash('Friendship not found', 'error')

    return redirect(url_for('friends.friends_list'))