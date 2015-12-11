# -*- coding: utf8 -*-

from app import db
from babel.dates import format_date
from config import WHOOSH_ENABLED # pour le support de la recherche dans les factures, voir : https://github.com/miguelgrinberg/microblog/blob/master/app/models.py

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64))
    firstname = db.Column(db.String(64), index=True, default='inconnu(e)')
    last_connection = db.Column(db.DateTime)
    timezone = db.Column(db.String(5), default='fr_FR')
    spends = db.relationship('Spending', backref='payer', lazy='dynamic') # so we can use Spending.payeur to get the User instance that created a Spending

    @staticmethod
    def useless_method():
        "I am static, that's why you can call me without any user (self) parameter !"
        print 'i am an useless static method'

    def avatar(self):
        return 'chemin-vers-l-image'

    def is_authenticated(self):
        "should just return True unless the object represents a user that should not be allowed to authenticate for some reason"
        print 'AUTHENTICATED'
        print 'user_id:', self.get_id()
        return True 

    def is_active(self):
    #TODO: useless function?
        "should return True for users unless they are inactive, for example because they have been banned"
        return True
    def is_anonymous(self):
    #TODO: useless function?
        "should return True only for fake users that are not supposed to log in to the system"
        return False

    def get_id(self):
        "should return a unique identifier for the user, in unicode format"
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def getPasswd(self):
        "envoie un mail avec un nouveau mot de passe"
        #à implémenter
        return True
        #si ça ne fonctionne pas
        return False

    def getLastConnection(self):
        """return user (self) lastConnection attribute according to user timezone"""
        return format_date(self.last_connection, locale=self.timezone)

    @staticmethod
    def getName(ID):
        user = User.query.filter_by(id=ID).first().firstname
        if user == "inconnu(e)":
            return User.query.filter_by(id=ID).first().email
        return user

    def __repr__(self):
        return '<User %r> (%r)' % (self.email, self.firstname)



class WallMessage(db.Model):
    """ (EN CHANTIER)
        manager du mur principal de messages.
        doit être unique (implémenter template singleton)

    """
    id = db.Column(db.Integer, primary_key = True)




class Spending(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    timestamp = db.Column(db.DateTime) # attention, à l'utilisation : enregistrer le temps UTC, parce qu'on a potentiellement des users du monde entier !
    type = db.Column(db.String(30)) # maybe an enumerate type in the future?
    label = db.Column(db.String(50))
    total = db.Column(db.Float(10))
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parts = db.relationship('Part', backref='spending', lazy='dynamic')
    #comment = db.Column(db.String(140))


    #immplémenter le formulaire ! relation 1..* en sqlalchemy ?
    """
    def __repr__(self):
        return '<Dépense %r (n°%r) payer:%r>' % (self.label, self.id, self.payer_id)
    """
    def compute_parts(self, Users):
        """Users passé est une liste de user_id
        """
        # parts est un dico (User_id, part_réel)
        return parts

    def getDate(self, user):
        """return spending (self) bought date attribute according to user timezone"""

        return format_date(self.timestamp, "d MMM", locale=user.timezone)

    @staticmethod
    def getPart(Spending, user_id):
        for part in Spending.parts:
            if part.user_id == user_id:
                return part.total
        return 0  # this user_id doesn't have to pay this bill



    class Part(db.Model): # Part.spending doit pouvoir récupérr le spending
        id = db.Column(db.Integer, primary_key = True)
        spending_id = db.Column(db.Integer, db.ForeignKey('spending.id'))
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        total = db.Column(db.Float(10))
