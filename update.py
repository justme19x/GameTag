from flask import Blueprint,render_template,request,redirect,url_for,flash
from datetime import datetime
from models import Utilizator
from website_start import db
from flask_login import login_user, login_required,logout_user,current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField,FileField,PasswordField, DateField,TextAreaField,SelectField
from wtforms.validators import DataRequired,Length
from wtforms.validators import (DataRequired,EqualTo,Length)
from flask_wtf.recaptcha import RecaptchaField
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from flask import current_app
from games import actualizare_jocuri

updatedd=Blueprint('updatedd',__name__)

#update information about profile
@updatedd.route('/update/<int:id_utilizator>', methods=['GET', 'POST'])
@login_required
def update(id_utilizator):
    if current_user.id_utilizator != id_utilizator:
        abort(403)
    # Obține utilizatorul pe care vrei să-l actualizezi din baza de date
    username_updated = Utilizator.query.get_or_404(id_utilizator)
    
    #odata gasit initializateaza cu datele utilizatorului
    form = ChestionarForm(obj=username_updated)

    if form.validate_on_submit():
        # Citirea datelor din formular
        username_updated.data_nasterii = request.form["data_nasterii"]
        username_updated.locatie = request.form["locatie"]
        username_updated.Pseudonim = request.form["Pseudonim"]  
        username_updated.descriere = request.form["descriere"]
        username_updated.sex=request.form["sex"]

        #check for file
        if request.files["fotografie"]:
            username_updated.fotografie = request.files["fotografie"]
            # grab image name
            pic_file=secure_filename(username_updated.fotografie.filename)
            #set uuid in caz ca avem acelasi nume pt poza de sus
            pic_name=str(uuid.uuid1()) + "_" + pic_file
            #save image
            saver = request.files["fotografie"]
            
            #salvam poza apoi schimbam numele
            username_updated.fotografie=pic_name

            try:
                db.session.commit()
                saver.save(os.path.join(current_app.config['UPLOAD_FOLDER'],  pic_name))
                flash("User updated successfully!", "success")
                #daca merge totul ok, unde ma duc ? profile.html sa afisez direct profilul modificat 
                return redirect(url_for('views.profile', username=username_updated.username,id_utilizator=current_user.id_utilizator))
            except:
                flash("Error!", "error")
                return render_template('updatedd.html',form=form,user=current_user,username_updated=username_updated)
        else:
            db.session.commit()
            flash("User updated successfully!", "success")
            #daca merge totul ok, unde ma duc ? profile.html sa afisez direct profilul modificat 
            return redirect(url_for('views.profile', username=username_updated.username,id_utilizator=current_user.id_utilizator))
    else:
        return render_template('updatedd.html', form=form,user=current_user,username_updated=username_updated)


class ChestionarForm(FlaskForm):
    data_nasterii = DateField('Data Nasterii', validators=[DataRequired()])
    locatie = StringField('Locatie', validators=[DataRequired()])
    Pseudonim = StringField('Pseudonim', validators=[DataRequired()])
    sex=StringField("sex")
    fotografie = FileField('fotografie')
    descriere = TextAreaField('Descriere')
    jocuri = StringField('Jocuri')
    submit = SubmitField('Trimite')

class change_pass(FlaskForm):
    Current_Password = PasswordField('Current Password', validators=[DataRequired(),Length(min=3)])
    New_Password = PasswordField('New Password', validators=[DataRequired(),Length(min=3)])
    ReNew_Password = PasswordField('Repeat your new password', validators=[DataRequired(),Length(min=3)])
    submit = SubmitField('Submit')


@updatedd.route('/update/change_password/<int:id_utilizator>', methods=['GET', 'POST'])
@login_required
def change_password(id_utilizator):
    form = change_pass()
    user = Utilizator.query.get(id_utilizator)
    if id_utilizator == current_user.id_utilizator:
        if form.validate_on_submit():
            old_password = form.Current_Password.data
            new_password = form.New_Password.data
            renew_password = form.ReNew_Password.data

            if not check_password_hash(user.parola, old_password):
                flash("Incorrect current password.", 'error')
            elif new_password != renew_password:
                flash("New passwords do not match.", 'error')
            else:
                user.parola = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
                flash('Password updated successfully!')
                return redirect(url_for('views.profile',id_utilizator=current_user.id_utilizator)) 
        
        return render_template('change_password.html', form=form, user=current_user)
    else:
        abort(403)
