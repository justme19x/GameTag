from flask import Blueprint,render_template,request,redirect,url_for,flash
from datetime import datetime
from models import Utilizator,Joc,Biblioteca_joc,Eveniment,Participare_eveniment,Notification
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
from flask_cors import cross_origin
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from flask import abort
from operator import attrgetter

events=Blueprint('events',__name__)

class EventForm(FlaskForm):
    name_event = StringField('Name for event',validators=[DataRequired()])
    descriere_event = TextAreaField('Description')
    data_inceput_ev = DateField('Event start date',validators=[DataRequired()])
    data_final_ev = DateField('Event end date',validators=[DataRequired()])
    #tags = StringField('Tags')
    #tags2 = SelectField('tags2', choices=[('game1', 'Game1'), ('game2', 'Game2'), ('game3', 'Sports')])
    submit = SubmitField('Submit')

class EventeditForm(FlaskForm):
    descriere_event = TextAreaField('Description')
    data_inceput_ev = DateField('Event start date',validators=[DataRequired()])
    data_final_ev = DateField('Event end date',validators=[DataRequired()])
    submit = SubmitField('Submit')

#definim your events
@events.route('/events/<id_utilizator>')
@login_required
def home_events(id_utilizator):


    joined_query = db.session.query(Participare_eveniment).join(
        Eveniment, Participare_eveniment.eveniment_id == Eveniment.id_Eveniment)

#filtram doar pentru evenimentele unde id_utilizator participa sau evenimentul e creat de el
    user_events_query = joined_query.filter(Participare_eveniment.utilizator_id == id_utilizator)

    user_events = user_events_query.all()

    evenimente_info = []

    for participation in user_events:
        eveniment_id = participation.eveniment_id
        eveniment_info = Eveniment.query.filter_by(id_Eveniment=eveniment_id).first()
        evenimente_info.append(eveniment_info)

    return render_template('events_home.html', evenimente_info=evenimente_info, user=current_user,Utilizator=Utilizator)


#create_event
@events.route('/events/create_event/', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    user_event_count = Eveniment.query.filter_by(created_by=current_user.id_utilizator).count()
    if user_event_count >= 3:
        flash('You have already created 3 events(max 3). Delete an event, then create another one.', 'error')
        return redirect(url_for('events.home_events',id_utilizator=current_user.id_utilizator))  

    if form.validate_on_submit():
        existing_event = Eveniment.query.filter(func.lower(Eveniment.nume_eveniment) == func.lower(form.name_event.data)).first()
        if existing_event:
            flash('An event with this name already exists. Please choose a different name.', 'error')
            return redirect(url_for('events.create_event',id_utilizator=current_user.id_utilizator))



    if form.validate_on_submit():
        event = Eveniment(
                      created_by=current_user.id_utilizator,
                      nume_eveniment=form.name_event.data,
                      descriere=form.descriere_event.data,
                      data_postare=datetime.utcnow(),
                      data_inceput_ev=form.data_inceput_ev.data,
                      data_final_ev=form.data_final_ev.data)
        db.session.add(event)
        db.session.commit()

        # adaugam participarea la eveniment daca utilizatorul a creat evenimentul
        participare = Participare_eveniment(
            utilizator_id=current_user.id_utilizator,
            eveniment_id=event.id_Eveniment,
            data_inscriere=datetime.utcnow()
        )
        db.session.add(participare)
        db.session.commit()


        return redirect(url_for('events.home_events',user=current_user,id_utilizator=current_user.id_utilizator))
    return render_template('event_create.html', form=form,user=current_user)



# functie pentru trimiterea de not
def send_notification(user_id,id_eveniment, info, details=None):
    notification = Notification(
        id_utilizator=user_id,
        info=info,
        details=details,
        id_eveniment=id_eveniment
    )
    db.session.add(notification)
    db.session.commit()


@events.route('/events/event_participate/', methods=['POST'])
@login_required
def event_participate():
    if request.method == 'POST':
        id_eveniment = request.form.get('id_eveniment')
        event=Eveniment.query.get(id_eveniment)
        if event:
            creator = Utilizator.query.get(event.created_by)
            existing_notification = Notification.query.filter_by(id_eveniment=id_eveniment, id_utilizator=current_user.id_utilizator).first()
            if not existing_notification:
                flash('Your request to join the event has been sent.', 'success')
                send_notification(current_user.id_utilizator,id_eveniment, 'Event', f' has requested to join your event "{event.nume_eveniment}".')
            else:
                flash("A notification has already been sent for.")
        return redirect(url_for('events.home_events', id_utilizator=current_user.id_utilizator))


def check_participation(event_id):
    participare_existenta = Participare_eveniment.query.filter_by(
        eveniment_id=event_id,
        utilizator_id=current_user.id_utilizator
    ).first()
    return participare_existenta is not None

@events.route('/events/search_for_event/', methods=['GET', 'POST'])
@login_required
def search_for_event():
    eventss = Eveniment.query.all()  
    return render_template('event_find.html', events=eventss,check_participation=check_participation,user=current_user,Utilizator=Utilizator)


@events.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    # daca utilizatorul a creat evenimentul - stergem evenimentul si participarea din event.
    event = Eveniment.query.filter_by(id_Eveniment=event_id, created_by=current_user.id_utilizator).first()
    if event:
        participari_eveniment = Participare_eveniment.query.filter_by(eveniment_id=event_id).all()
        for participare in participari_eveniment:
            db.session.delete(participare)

        db.session.delete(event)
        db.session.commit()

        flash('Event deleted successfully', 'success')
    else:
        #daca nu a fost creat de el stergem doar participarea
        event_to_delete = Participare_eveniment.query.filter_by(utilizator_id=current_user.id_utilizator, eveniment_id=event_id).first()
        if event_to_delete:
            db.session.delete(event_to_delete)
            db.session.commit()
            flash('Your participation in the event has been deleted', 'success')
        else:
            abort(404)

    return redirect(url_for('events.home_events', id_utilizator=current_user.id_utilizator))


@events.route('/events/edit/<int:event_id>/', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Eveniment.query.get_or_404(event_id)

    if event.created_by != current_user.id_utilizator:
        abort(403) 

    form = EventeditForm()
    
    if form.validate_on_submit():
        event.descriere = form.descriere_event.data
        event.data_inceput_ev = form.data_inceput_ev.data
        event.data_final_ev = form.data_final_ev.data
        db.session.commit()

        flash('Event updated successfully', 'success')
        return redirect(url_for('events.home_events', event_id=event_id,id_utilizator=current_user.id_utilizator))
    
    form.descriere_event.data = event.descriere
    form.data_inceput_ev.data = event.data_inceput_ev
    form.data_final_ev.data = event.data_final_ev

                
    return render_template('event_edit.html', form=form, event=event, user=current_user)


#if ur a creator
@events.route('/events/<int:event_id>/edit_participants', methods=['GET', 'POST'])
def edit_participants(event_id):
    event = Eveniment.query.get_or_404(event_id)

    if event.created_by != current_user.id_utilizator:
        abort(403)

    participants = Participare_eveniment.query.filter_by(eveniment_id=event_id).all()
    event_participants_sorted = sorted(participants, key=attrgetter('utilizator.username'))
    return render_template('event_participants.html', event=event, participants=event_participants_sorted,user=current_user)


#else
@events.route('/events/<int:event_id>/view_participants/')
@login_required
def view_event_participants(event_id):
    event = Eveniment.query.get_or_404(event_id)
    creator = Utilizator.query.get(event.created_by)
    event_participants = Participare_eveniment.query.filter_by(eveniment_id=event_id).all()
    event_participants_sorted = sorted(event_participants, key=attrgetter('utilizator.username'))
    return render_template('event_view_participants.html',event=event,creator=creator, participants=event_participants_sorted,user=current_user)

#functionalitate butoane de delete participant
@events.route('/delete_participant', methods=['POST'])
def delete_participant():
    event_id = request.form['event_id'] 
    event = Eveniment.query.get_or_404(event_id)
    participant_id = request.form['participant_id']  
    if current_user.id_utilizator != event.created_by:
        abort(403)
    participant_event = Participare_eveniment.query.filter_by(utilizator_id=participant_id, eveniment_id=event_id).first()
    if participant_event:
        db.session.delete(participant_event)
        db.session.commit()
        message = ("The participant has been successfully deleted from the event.")
    participants = Participare_eveniment.query.filter_by(eveniment_id=event_id).all()
    event_participants_sorted = sorted(participants, key=attrgetter('utilizator.username'))
    return render_template('event_participants.html',event=event,participants=event_participants_sorted,message=message,user=current_user)