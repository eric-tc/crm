from flask import render_template
from . import home
from .database_instance import db_instance
from flask import Flask, request, jsonify, url_for, redirect, send_file
from sqlalchemy import inspect

# need to import all Tables
from .database_schema import Clients, OrderStatus, Order,OrderData
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from .views_client import get_clients_list,insert_client,get_anagrafica_cliente
from .views_order import order_notes,update_order,upload_order, add_order,show_pdf

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}


def check_table_records(table):
    has_records = db_instance.db.session.query(
        db_instance.db.exists().where(table.id != None)).scalar()
    return has_records


"""
DOVE SONO ARRIVATO

Ho completato il salvataggio del PDF nel form per aggiungere il preventivo
Dopo aver inserito il preventivo sono reindirizzato alla lista clients. Sarebbe meglio ritornare nella scheda cliente

I preventivi sono salvati nella cartella static/uploads/nome_cliente/ nome_preventivo.pdf

COSE DA FARE

1) Salvare il preventivo a database con il nome del flie. Devo aggiungere la nome del preventivo il timestamp OK
In questo modo non rischio di sovrascriver i file
2) Mostrare la lista dei preventivi nell'anagrafica cliente OK
3) Permettere di modificare il preventivo. Utilizzo lo stesso form. OK
3BIS) Aggiungere il pulsante show che nella tabella riassuntiva dei preventivi carica una pagina per vedere il pdf.
La pagina esiste già si chiama /pdf devo aggiungere solo il passaggio del path da parametro in GET OK

4) Iniziare il sales forecasting avendo in memoria tutti i preventivi di clienti diversi OK

5) Manca il nome del preventivo OK


COSE DA POTER AGGIUNGERE

1) Per Ogni cliente aggiungere il contatto fisico che devo chiamare
2) Aggiungere le analytics tramite Linkedin per scaricare i dati delle campagne
3) Monitorare in automatico l'andamento del sito tramite google Analitycs
4) Aggiungere per ogni preventivo uno spazio di testo per prendere note sul motivo o meno
di una vendita conclusa oppure no.

5) Aggiungere le spese correnti 



VENDITA

Scheda Cliente

1) Per Ogni Preventivo Aggiungere le domande da fare per creare fiducia 

"""


@home.route("/")
def homepage():
    """
    Render the homepage template on the / route
    """
    print("RENDER HOME PAGE")
    db_instance.db.create_all()

    if not check_table_records(OrderStatus):

        print("ADD DEFAULT VALUE")
        OrderStatus.create_predefined_rows()

  

    clients = Clients.query.all()  # Retrieve all users from the User table
    # client_list = [{'id': client.id, 'name': client.name,
    #                 'email': client.email} for client in clients]

    client_dict = {}
    orders_status_dict = {}
    for client in clients:
        client_dict[client.id] = {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "valore_Q1": 0.0,
            "valore_Q1_pesato": 0.0,
            "valore_Q2": 0.0,
            "valore_Q2_pesato": 0.0,
            "valore_Q3": 0.0,
            "valore_Q3_pesato": 0.0}

    orders_status = OrderStatus.query.all()

    for order_status in orders_status:
        orders_status_dict[order_status.id] = {"order_status": order_status.order_status,
                                               "percentage": order_status.percentage}

    start_date = datetime.now()
    next_3_months = start_date + relativedelta(months=3)
    next_6_months = start_date + relativedelta(months=6)
    next_9_months = start_date + relativedelta(months=9)

    Q1 = Order.query.filter(Order.data_possibile_vendita.between(
        start_date, next_3_months)).all()
    Q2 = Order.query.filter(Order.data_possibile_vendita.between(
        next_3_months + relativedelta(days=1), next_6_months)).all()
    Q3 = Order.query.filter(Order.data_possibile_vendita.between(
        next_6_months + relativedelta(days=1), next_9_months)).all()

    totale_q1 = 0
    totale_q1_pesato = 0
    totale_q2 = 0
    totale_q2_pesato = 0
    totale_q3 = 0
    totale_q3_pesato = 0

    print(orders_status_dict[1])
    for q1 in Q1:

        print(q1.order_status_id)
        client_dict[q1.clients_id]["valore_Q1"] = client_dict[q1.clients_id]["valore_Q1"] + \
            q1.valore_preventivo

        valore_pesato = (float(q1.valore_preventivo) *
                         float(orders_status_dict[q1.order_status_id]["percentage"])/100)
        client_dict[q1.clients_id]["valore_Q1_pesato"] = client_dict[q1.clients_id]["valore_Q1_pesato"] + valore_pesato
        print(q1.valore_preventivo)

        totale_q1_pesato = totale_q1_pesato + valore_pesato
        totale_q1 = q1.valore_preventivo + totale_q1

    for q2 in Q2:

        client_dict[q2.clients_id]["valore_Q2"] = client_dict[q2.clients_id]["valore_Q2"] + \
            q2.valore_preventivo
        totale_q2 = q2.valore_preventivo + totale_q2

        valore_pesato = (float(q2.valore_preventivo) *
                         float(orders_status_dict[q2.order_status_id]["percentage"])/100)
        client_dict[q2.clients_id]["valore_Q2_pesato"] = client_dict[q2.clients_id]["valore_Q2_pesato"] + valore_pesato
        totale_q2_pesato = totale_q2_pesato + valore_pesato

    for q3 in Q3:

        client_dict[q3.clients_id]["valore_Q3"] = client_dict[q3.clients_id]["valore_Q3"] + \
            q3.valore_preventivo
        totale_q3 = q3.valore_preventivo + totale_q3

        valore_pesato = (float(q3.valore_preventivo) *
                         float(orders_status_dict[q3.order_status_id]["percentage"])/100)
        client_dict[q3.clients_id]["valore_Q3_pesato"] = client_dict[q3.clients_id]["valore_Q3_pesato"] + valore_pesato
        totale_q3_pesato = totale_q3_pesato + valore_pesato

    print(client_dict)
    return render_template("page/home/index.html", data=client_dict,
                           totale_q1=totale_q1,
                           totale_q2=totale_q2,
                           totale_q3=totale_q3,
                           totale_q1_pesato=totale_q1_pesato,
                           totale_q2_pesato=totale_q2_pesato,
                           totale_q3_pesato=totale_q3_pesato
                           )


@home.route("/order_status")
def get_order_status():

    orders_status = OrderStatus.query.all()

    order_status_list = [{'id': order_status.id, 'status': order_status.order_status,
                          'percentage': order_status.percentage} for order_status in orders_status]

    return jsonify({"result": order_status_list})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_file_data(file_path):
    with open(file_path, 'rb') as file:
        return file.read()



@home.route('/update', methods=['POST'])
def update():
    print("UPDATE ENDPOINT")
    row_data = request.form.to_dict()

    print(row_data)
    # Process the updated row data as needed (e.g., update the database)

    # Return a response if needed
    return 'Row data updated successfully'


@home.route("/dashboard")
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template("page/home/dashboard.html", title="Dashboard")
