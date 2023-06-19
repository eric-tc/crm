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

    # data = [
    #     {
    #         'name': 'John Doe',
    #         'email': 'john@example.com',
    #         'id': 1,
    #         'location': 'New York'
    #     },
    #     {
    #         'name': 'Jane Smith',
    #         'email': 'jane@example.com',
    #         'id': 2,
    #         'location': 'London'
    #     },
    #     {
    #         'name': 'Mike Johnson',
    #         'email': 'mike@example.com',
    #         'id': 3,
    #         'location': 'Paris'
    #     }
    # ]

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


@home.route("/clients")
def get_clients_list():
    clients = Clients.query.all()  # Retrieve all users from the User table
    client_list = [{'id': client.id, 'name': client.name,
                    'email': client.email} for client in clients]

    return render_template("page/home/clients_list.html", data=client_list)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_file_data(file_path):
    with open(file_path, 'rb') as file:
        return file.read()


def get_root_dir_abs_path() -> str:
    """
    Get the absolute path to the root directory of the application.
    """
    # Check if the application runs in a bundled executable from PyInstaller.
    # When executed, the bundled executable get's unpacked into the temporary directory sys._MEIPASS.
    # See also: https://pyinstaller.readthedocs.io/en/stable/runtime-information.html#using-file
    return getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))



@home.route("/scheda_preventivo", methods=["POST", "GET"])
def scheda_preventivo():


    order_id = request.args.get("order_id")
    client_id = request.args.get("client_id")
    client_name = request.args.get("client_name")

    if request.method == 'POST':
        irrisolta = request.form.get('irrisolta')
        altre_soluzioni = request.form.get('altre_soluzioni')
        non_funzionano = request.form.get('non_funzionano')
        investimento = request.form.get('investimento')
        costo_associato = request.form.get('costo_associato')
        soluzioni_proposte = request.form.get('soluzioni_proposte')
        sistema_regime = request.form.get('sistema_regime')
        altre_persone = request.form.get('altre_persone')
        clienti_lamentele = request.form.get('clienti_lamentele')
        segnali_positivi = request.form.get('segnali_positivi')


        form_data = OrderData(irrisolta=irrisolta, altre_soluzioni=altre_soluzioni,
                             non_funzionano=non_funzionano, investimento=investimento,
                             costo_associato=costo_associato, soluzioni_proposte=soluzioni_proposte,
                             sistema_regime=sistema_regime, altre_persone=altre_persone,
                             clienti_lamentele=clienti_lamentele, segnali_positivi=segnali_positivi,order_id=order_id)

        db_instance.db.session.add(form_data)
        db_instance.db.session.commit()

        # Process the form data as needed
        return render_template("page/home/scheda_preventivo.html",form_data=form_data)
        


    return render_template("page/home/scheda_preventivo.html",form_data={},order_id=order_id,client_id=client_id,client_name=client_name)

@home.route("/upload_preventivo", methods=["POST", "GET"])
def upload_preventivo():
    """
    Funzione per salvare il preventivo nella cartella static

    """
    id = request.args.get("id")
    name = request.args.get("name")
    importo = request.form.get("importo")
    file = request.files['file']
    nome_preventivo = request.form.get("nome_preventivo")
    data_possibile_vendita_str = request.form.get("data_possibile_vendita")
    # Convert the date string to a datetime object
    data_possibile_vendita = datetime.strptime(
        data_possibile_vendita_str, '%Y-%m-%d').date()

    print(data_possibile_vendita_str)
    print(request)
    print(f"nome preventivo {nome_preventivo}")
    print(f"IMPORTO {importo}")
    file_path = ""
    selected_id = request.form.get('selected_id')
    print(f"SELECT {selected_id}")
    if file:
        print("ADD PDF")

        save_directory = os.path.join(
            get_root_dir_abs_path(), "..", "static", "uploads", name)
        Path(save_directory).mkdir(parents=True, exist_ok=True)

        filename_path = Path(file.filename)

        filename = str(filename_path.stem)
        filename_ext = str(filename_path.suffix)
        filename = filename + "_" + str(int(time.time())) + "_" + filename_ext

        filename = secure_filename(filename)
        file_path = os.path.join(save_directory, filename)

        file.save(file_path)

    new_order = Order(nome_preventivo, data_possibile_vendita, path_pdf_preventivo=file_path, client_id=id,
                      id_stato_commessa=selected_id, valore_preventivo=importo)
    db_instance.db.session.add(new_order)
    db_instance.db.session.commit()

    return redirect(url_for("home.get_clients_list"))


@home.route("/update_preventivo", methods=["POST", "GET"])
def update_preventivo():

    id_preventivo = request.args.get("id")
    id_cliente = request.args.get("client_id")
    name_cliente = request.args.get("client_name")
    nome_preventivo = request.args.get("nome_preventivo")
    preventivo = Order.query.filter_by(id=id_preventivo).first()

    if request.method == 'POST':

        importo = request.form.get("importo")
        file = request.files['file']
        selected_id = request.form.get('selected_id')
        data_possibile_vendita_str = request.form.get("data_possibile_vendita")
        # Convert the date string to a datetime object
        data_possibile_vendita = datetime.strptime(
            data_possibile_vendita_str, '%Y-%m-%d').date()

        if file:
            print("ADD PDF")

            save_directory = os.path.join(
                get_root_dir_abs_path(), "..", "static", "uploads", name_cliente)
            Path(save_directory).mkdir(parents=True, exist_ok=True)

            filename_path = Path(file.filename)

            filename = str(filename_path.stem)
            filename_ext = str(filename_path.suffix)
            filename = filename + "_" + \
                str(int(time.time())) + "_" + filename_ext

            filename = secure_filename(filename)
            file_path = os.path.join(save_directory, filename)

            file.save(file_path)
            preventivo.path_pdf_preventivo = file_path

        preventivo.data_possibile_vendita = data_possibile_vendita
        preventivo.valore_preventivo = importo
        preventivo.order_status_id = selected_id

        db_instance.db.session.commit()

        return redirect(url_for("home.anagrafica_cliente", id=id_cliente, name=name_cliente))

    print(f"ID_PREVENTIVO {id_preventivo}")
    orders_status = OrderStatus.query.all()

    order_status_list = [{'id': order_status.id, 'status': order_status.order_status,
                          'percentage': order_status.percentage} for order_status in orders_status]

    return render_template("page/home/update_preventivo.html", id=id_cliente, name=name_cliente, order_status_list=order_status_list)


@home.route("/add_preventivo", methods=["POST", "GET"])
def add_preventivo():

    id = request.args.get("id")
    name = request.args.get("name")

    # file = request.files['file']
    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     file_path = os.path.join(UPLOAD_FOLDER, filename)
    #     file.save(file_path)

    # document = Document(name=filename, file_data=read_file_data(file_path))
    # db.session.add(document)
    # db.session.commit()

    orders_status = OrderStatus.query.all()

    order_status_list = [{'id': order_status.id, 'status': order_status.order_status,
                          'percentage': order_status.percentage} for order_status in orders_status]

    return render_template("page/home/aggiungi_preventivo.html", id=id, name=name, order_status_list=order_status_list)


@home.route('/pdf/', methods=["GET", "POST"])
def show_pdf():

    path = request.args.get("path_pdf_preventivo")
    print(path)
    # name = "eric/2210.05189.pdf"
    # save_directory = os.path.join(
    #     get_root_dir_abs_path(), "..", "static", "uploads", name)

    return send_file(path, mimetype='application/pdf')


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
