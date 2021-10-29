#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
this admin script allows you to :
  - la base minimale du programme : ./administration 1
  - base de test : ./administration 2
  - add an user to the db : ./administration 0 email password (firstname timezone)

"""

from sys import argv, exc_info
from app import models
from app.models import User, Spending
from flask import Flask
from babel.dates import datetime

coreApp = Flask(__name__)
coreApp.config.from_object('config')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(coreApp)


def addUser(*args):
    """adding an user in the database: (email, passwd, firstname, timezone)"""
    #timezone = 'fr_FR'
    user = models.User(email=email, password=passwd, firstname=firstname, timezone=timezone)
    db.session.add(user)
    user.set_password(passwd)
    db.session.commit()
    print("User added: {}, {}, {}, {}".format(email, passwd, firstname, timezone))

def addBill(s_type, s_label, s_total, s_payer_id, s_user_ids):
    """
        create a Spending in the database.
          1) create the Spending model and fill its attributes except parts
          2) estimate parts and add them to our Spending
          3) adjust balance for each User with this parts
          4) until no errors: add all of this in the database
    """
    try:
        bill = Spending()
        bill.timestamp = datetime.utcnow()
        bill.s_type = s_type
        bill.label = label
        bill.total = total
        bill.payer_id = payer_id
        db.session.add(bill)

        db.session.query(User).get(payer_id).given_money += bill.total
     
        
        tmp_parts = bill.computeParts(db.session, len(s_user_ids))
        user_parts = []
        for idx, i in enumerate(tmp_parts):
            db.session.add(
                Spending.Part(
                    spending=bill,
                    total=i, # == tmp_parts[idx],
                    user_id=s_user_ids[idx]
                )
            )
            user_parts.append([s_user_ids[idx], i])
        

        for user_id, user_bill in user_parts:
            db.session.query(User).get(user_id).borrowed_money += user_bill

        db.session.commit()
        return 1
    except:
        db.session.rollback()
        print(exc_info())
        return 0

def addTypes():
    db.session.add(models.Spending.Type(name=u"Alimentation (🍆)"))
    db.session.add(models.Spending.Type(name=u"Alimentation (🍖)"))
    db.session.add(models.Spending.Type(name=u"Alcool"))
    db.session.add(models.Spending.Type(name=u"Divers"))
    db.session.add(models.Spending.Type(name=u"Charges"))
    db.session.add(models.Spending.Type(name=u"Bien-être"))
    db.session.add(models.Spending.Type(name=u"Sorties"))
    db.session.add(models.Spending.Type(name=u"Maison"))
    db.session.add(models.Spending.Type(name=u"Virement"))
    db.session.commit()


def delete_spendings_before_date():
    # WARNING, IT WILL BREAKS BALANCES!!

    from datetime import date
    db_session = db.session()  # it may not work: use the line below
    # db_session = db.object_session(list(models.Spending.query)[0])

    # list(models.Spending.query.filter(models.Spending.s_date>date(year=2021, month=9, day=1)).order_by(models.Spending.s_date.asc()))[3]
    for spending in models.Spending.query.filter(models.Spending.s_date < date(year=2021, month=9, day=1)):
        for part in spending.parts:
            db_session.delete(part)
        db_session.delete(spending)

    db_session.commit()


if __name__ == '__main__':
    if argv[1] == str(0):
        email = argv[2]
        passwd = argv[3]
        try:
            firstname = argv[4]
        except:
            firstname = None
        try:
            timezone = argv[5]
        except:
            timezone = None

        addUser(email, passwd, firstname, timezone)
    
    # initialization
    if (argv[1] == str(1)) or (argv[1] == "init"):
        addTypes()
        a = models.User(email='b@t', firstname='Batoo')
        a.set_password('coucou')
        db.session.add(a)
        db.session.commit()
    
    # test of adding a bill
    if argv[1] == str(2):
        s_type = 'Alimentation'
        label = 'Carottes'
        total = 56.12
        payer_id = 1
        user_ids = [1, 2]
        addBill(s_type, label, total, payer_id, user_ids) #spend=models.Spending.query.filter_by(id=1).first())
        
        print('données de test initiales ajoutées: OK.')
