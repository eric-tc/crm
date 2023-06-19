

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
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}


@home.route("/clients")
def get_clients_list():
    clients = Clients.query.all()  # Retrieve all users from the User table
    client_list = [{'id': client.id, 'name': client.name,
                    'email': client.email} for client in clients]

    return render_template("page/home/clients_list.html", data=client_list)


@home.route("/insert_client", methods=["GET", "POST"])
def insert_client():

    # new_user = Clients(name='John Doe', email='john@example.com')
    # db_instance.db.session.add(new_user)
    # db_instance.db.session.commit()

    if request.method == 'POST':
        email = request.form.get("email")
        name = request.form.get("name")

        existing_user = Clients.query.filter_by(email=email).first()

        if existing_user:
            print("EMAIL ALREADY EXISTS CANNOT CREATE")
        else:
            new_user = Clients(name=name, email=email)
            db_instance.db.session.add(new_user)
            db_instance.db.session.commit()
            print("DATA INSERTED")

            return redirect(url_for("home.get_clients_list"))

    return render_template("page/home/insert_client.html")



@home.route('/anagrafica_cliente/', methods=["GET", "POST"])
def get_anagrafica_cliente():

    if request.method == 'POST':
        # Submitted from form to update user value
        id = request.form.get("client_id")
        print(f"ID FORM {id}")
        email = request.form.get("client_email")
        name = request.form.get("client_name")

        client = Clients.query.filter_by(id=id).first()

        if client:
            client_data = {'id': client.id,
                           'name': client.name, 'email': client.email}

            print("UPDATE USER VALUE")
            client.name = name
            client.email = email

            db_instance.db.session.commit()
            return render_template("page/home/anagrafica_cliente.html", name=name, data=client_data)
        else:

            return render_template("page/home/anagrafica_cliente.html", name=name, data=client_data)

    id = request.args.get("client_id")
    name = request.args.get("client_name")
    client = Clients.query.filter_by(id=id).first()

    if client:
        client_data = {'client_id': client.id,
                       'client_name': client.name, 'client_email': client.email}

    # Recupera tutti gli ordini del cliente
    orders = Order.query.filter(Order.clients_id == client.id).all()
    orders_status = OrderStatus.query.all()

    print(f"ORDERS {len(orders)}")
    print(f"ORDER STATUS {orders_status}")
    orders_data = []

    orders_data = [{'order_id': order_data.id,
                    'nome_preventivo': order_data.nome_preventivo,
                    'date': order_data.data_possibile_vendita.date(),
                    'path_pdf_preventivo': order_data.path_pdf_preventivo,
                    'valore_preventivo': order_data.valore_preventivo,
                    'clients_id': order_data.clients_id,
                    'order_status_id': orders_status[int(order_data.order_status_id)-1].order_status,
                    'order_percentage': orders_status[int(order_data.order_status_id)-1].percentage}
                   for order_data in orders]

    print(orders_data)
    return render_template("page/home/anagrafica_cliente.html", name=name, client_data=client_data, orders_data=orders_data)

