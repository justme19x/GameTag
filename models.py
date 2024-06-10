from website_start import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Participare_eveniment(db.Model):
    utilizator_id = db.Column(db.Integer, db.ForeignKey('utilizator.id_utilizator'), primary_key=True)
    eveniment_id = db.Column(db.Integer, db.ForeignKey('eveniment.id_Eveniment'), primary_key=True)
    data_inscriere = db.Column(db.Date)

    utilizator = relationship("Utilizator", back_populates="participari_evenimente")
    eveniment = relationship("Eveniment", back_populates="participari_evenimente")
    
def get_username(id_utilizator):
    utilizator = db.session.query(Utilizator).filter_by(id_utilizator=id_utilizator).first()
    if utilizator:
        return utilizator.username
    return None

def get_user_id(username):
    utilizator = Utilizator.query.filter_by(username=username).first()
    if utilizator:
        return utilizator.id_utilizator
    return None

class Utilizator(db.Model,UserMixin):
    id_utilizator= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255),unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    parola = db.Column(db.String(555))
    data_nasterii = db.Column(db.Date)
    data_inregistrare = db.Column(db.DateTime(timezone=True), default=func.now())
    fotografie= db.Column(db.String(255), nullable=True)
    descriere= db.Column(db.String(255), nullable=True)
    locatie= db.Column(db.String(255), nullable=True)
    jocuri= db.Column(db.String(900), nullable=True)
    Nivel = db.Column(db.Integer,default=1)
    Pseudonim= db.Column(db.String(255), nullable=True)
    sex = db.Column(db.String(1), CheckConstraint('sex IN ("M", "F","N")'),default="N")
    biblioteca_joc = relationship("Biblioteca_joc", back_populates="utilizator")
    participari_evenimente = relationship("Participare_eveniment", back_populates="utilizator")
    recenzii = relationship('Recenzie', backref='utilizator', lazy=True)
    postari = db.relationship('Postare', backref='autor', lazy=True)
    comentarii = db.relationship('Comentariu', backref='autor', lazy=True)

    def get_id(self):
        return str(self.id_utilizator)
    
    def check_email_exists(email):
        existing_user = Utilizator.query.filter_by(email=email).first()
        if existing_user:
            return True
        else:
            return False
        
    def count_events(self):
        return Eveniment.query.filter_by(created_by=self.id_utilizator).count()

    

class Mesaje_chat(db.Model):
    id_Mesaje = db.Column(db.Integer, primary_key=True)
    utilizatorul_mesaj_1 = db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))
    utilizatorul_mesaj_2 = db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))
    data_trimitere = db.Column(db.Date)
    text_mesaj = db.Column(db.String(255)) 

class Friendship(db.Model):
    id_Friendship = db.Column(db.Integer, primary_key=True)
    id_utilizator_1= db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))
    id_utilizator_2= db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))
    data_cerere= db.Column(db.Date)
    data_acceptare= db.Column(db.Date)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_utilizator = db.Column(db.Integer, db.ForeignKey('utilizator.id_utilizator'))
    id_Friendship = db.Column(db.Integer,db.ForeignKey('friendship.id_Friendship'))
    id_eveniment=db.Column(db.Integer,db.ForeignKey('eveniment.id_Eveniment'))
    info = db.Column(Enum('Friends', 'Message','Event','Others'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    details=db.Column(db.String(255), nullable=True)
    friendship = relationship("Friendship")
    user = db.relationship('Utilizator', foreign_keys=[id_utilizator], backref=db.backref('notifications', lazy=True))

    #cauta numele dupa id
    def sender_username(self):
        sender = Utilizator.query.get(self.id_utilizator_sender)
        if sender:
            return sender.username
        return None
    
    def __repr__(self):
        return f"Notification('{self.content}', '{self.created_at}')"
    
    
class Postare(db.Model):
    id_postare = db.Column(db.Integer, primary_key=True)
    text_postare=db.Column(db.String(255))
    data_postare= db.Column(db.Date)
    id_utilizator_postare= db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))
    tip_postare=db.Column(db.String(255))
    comentarii = db.relationship('Comentariu', backref='postare', lazy=True)

class Comentariu(db.Model):
    id_Comentariu= db.Column(db.Integer, primary_key=True)
    text_comentariu= db.Column(db.String(255))
    data_comentariu= db.Column(db.Date)
    id_postare=  db.Column(db.Integer,db.ForeignKey('postare.id_postare'))
    id_utilizator=  db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))

class Joc(db.Model):
    id_Joc = db.Column(db.Integer, primary_key=True)
    nume_joc = db.Column(db.String(255))
    dezvoltator = db.Column(db.String(255))
    gen = db.Column(db.String(255))
    an_lansare = db.Column(db.Date)
    pret = db.Column(db.Integer)
    poza=db.Column(db.String(255))
    content=db.Column(db.Text())
    chat=db.Column(db.Text())
    biblioteca_joc = relationship("Biblioteca_joc", back_populates="joc")
    recenzii = relationship('Recenzie', backref='joc', lazy=True)

class Biblioteca_joc(db.Model):
    id_utilizator = db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'), primary_key=True)
    id_joc = db.Column(db.Integer,db.ForeignKey('joc.id_Joc') ,primary_key=True)
    data_adaugare = db.Column(db.Date)
    last_played = db.Column(db.Date)
    play = db.Column(db.Boolean) 
    
    utilizator = relationship("Utilizator", back_populates="biblioteca_joc")
    joc = relationship("Joc", back_populates="biblioteca_joc")



class Recenzie(db.Model):
    id_Recenzie= db.Column(db.Integer, primary_key=True)
    id_utilizator= db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))
    id_joc= db.Column(db.Integer,db.ForeignKey('joc.id_Joc'))
    text_recenzie= db.Column(db.String(255))
    Nota= db.Column(db.Integer)
    data_recenzie= db.Column(db.Date)
















class Eveniment(db.Model):
    id_Eveniment= db.Column(db.Integer, primary_key=True)
    created_by=db.Column(db.Integer,db.ForeignKey('utilizator.id_utilizator'))
    nume_eveniment=  db.Column(db.String(255),unique=True)
    descriere= db.Column(db.String(255))
    data_postare= db.Column(db.Date)
    data_inceput_ev= db.Column(db.Date)
    data_final_ev= db.Column(db.Date)
    tags= db.Column(db.String(255))
    type_event=db.Column(Enum('System', 'User','Community','Others'), default='User')
    participari_evenimente = relationship("Participare_eveniment", back_populates="eveniment")
