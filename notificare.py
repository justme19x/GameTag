from flask import Blueprint,render_template,request,redirect,url_for,flash
from datetime import datetime
from models import Utilizator,Notification,Friendship,Eveniment,Participare_eveniment
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


notificare=Blueprint('notificare',__name__)



#cereri pe care tu le-ai trimis sau le-ai trimis / current user// ut1
@notificare.route('/notifications')
@login_required
def afisare_notificare_friendship():
    cereri_trimise = Friendship.query.filter_by(id_utilizator_1=current_user.id_utilizator).all()
    cereri_primite = Friendship.query.filter_by(id_utilizator_2=current_user.id_utilizator).all()
    evenimente_trimise = db.session.query(Notification).join(Eveniment, Notification.id_eveniment == Eveniment.id_Eveniment).filter(Eveniment.created_by == current_user.id_utilizator, Notification.info == 'Event').all()
    return render_template('notificari.html',evenimente_trimise=evenimente_trimise ,cereri_trimise=cereri_trimise, cereri_primite=cereri_primite,user=current_user,get_username=get_username)



@notificare.route('/notifications/accept/<username>',methods=['POST'])
@login_required
def accept(username):
    """
    
    """
    user_id_to_add=get_user_id(username)
    if user_id_to_add: 
        friendship_exist = Friendship.query.filter_by(id_utilizator_2=current_user.id_utilizator, id_utilizator_1=user_id_to_add).first()
        if friendship_exist:
            friendship_exist.data_acceptare = datetime.now()
            db.session.commit()
            notification_exist = Notification.query.filter_by(id_Friendship=friendship_exist.id_Friendship).first()
            if notification_exist:
                db.session.delete(notification_exist)
                db.session.commit()

            flash('The request was accepted!', 'success')
            return redirect(url_for('notificare.afisare_notificare_friendship')) 
        else:
            flash('error','error')
            return redirect(url_for('notificare.afisare_notificare_friendship')) 



@notificare.route('/notifications/refuse/<username>',methods=['POST'])
@login_required
def refuse(username):
    user_id_to_refused=get_user_id(username)
    if user_id_to_refused:    
        friendship_exist = Friendship.query.filter_by(id_utilizator_2=current_user.id_utilizator, id_utilizator_1=user_id_to_refused).first()
        if friendship_exist:
            notification_exist = Notification.query.filter_by(id_Friendship=friendship_exist.id_Friendship).first()
            if notification_exist:
                db.session.delete(notification_exist)
                db.session.commit()
            db.session.delete(friendship_exist)
            db.session.commit()
            flash('The request was rejected!', 'success')
            return redirect(url_for('notificare.afisare_notificare_friendship')) 
        else:
            flash('Error!', 'error')
            return redirect(url_for('notificare.afisare_notificare_friendship')) 


@notificare.route('/notifications/delete/<username>',methods=['POST'])
@login_required
def deleted(username):
    user_id_to_delete=get_user_id(username)
    if user_id_to_delete:
    #verificam daca exista cerea de prietenie de la bun inceput intre cei doi
        friendship_exist = Friendship.query.filter_by(id_utilizator_1=current_user.id_utilizator, id_utilizator_2=user_id_to_delete).first()
        if friendship_exist:
            notification_exist = Notification.query.filter_by(id_Friendship=friendship_exist.id_Friendship).first()
            if notification_exist:
                db.session.delete(notification_exist)
                db.session.commit()
            db.session.delete(friendship_exist)
            db.session.commit()

            flash('Deleted!', 'success')
            return redirect(url_for('notificare.afisare_notificare_friendship')) 
        else:
            # Dacă nu există cerere de prietenie
            flash('Error!', 'error')
            return redirect(url_for('notificare.afisare_notificare_friendship')) 
        











#PARTEA DE ACCEPT EVENT/DECLINE EVENT


@notificare.route('/notifications/refuse_user/<username>/<int:event_id>',methods=['POST'])
@login_required
def decline_request(username,event_id):
    user_id_to_decline=get_user_id(username)
    if user_id_to_decline:
        Notification.query.filter_by(id_utilizator=user_id_to_decline, id_eveniment=event_id).delete()
        db.session.commit()
        flash('Request declined successfully.', 'success')
    else:
        flash('User not found.', 'error')
    
    return redirect(request.referrer)

    

@notificare.route('/notifications/accept_user/<username>/<int:event_id>',methods=['POST'])
@login_required
def accept_request(username,event_id):
    user_id_to_accept=get_user_id(username)
    if user_id_to_accept:
        participare_eveniment = Participare_eveniment(
            utilizator_id=user_id_to_accept,
            eveniment_id=event_id,
            data_inscriere=datetime.now() 
        )
        db.session.add(participare_eveniment)
        db.session.commit()


        Notification.query.filter_by(id_utilizator=user_id_to_accept).delete()
        db.session.commit()
        flash('Request accepted successfully.', 'success')
    else:
        flash('User not found.', 'error')
    
    return redirect(request.referrer)