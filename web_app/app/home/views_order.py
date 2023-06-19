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

def get_root_dir_abs_path() -> str:
    """
    Get the absolute path to the root directory of the application.
    """
    # Check if the application runs in a bundled executable from PyInstaller.
    # When executed, the bundled executable get's unpacked into the temporary directory sys._MEIPASS.
    # See also: https://pyinstaller.readthedocs.io/en/stable/runtime-information.html#using-file
    return getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))



@home.route("/order_notes", methods=["POST", "GET"])
def order_notes():


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
        return render_template("page/home/order_notes.html",form_data=form_data)
        


    return render_template("page/home/order_notes.html",form_data={},order_id=order_id,client_id=client_id,client_name=client_name)

@home.route("/upload_order", methods=["POST", "GET"])
def upload_order():
    """
    Funzione per salvare il preventivo nella cartella static

    """
    client_id = request.args.get("client_id")
    client_name = request.args.get("client_name")
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
            get_root_dir_abs_path(), "..", "static", "uploads", client_name)
        Path(save_directory).mkdir(parents=True, exist_ok=True)

        filename_path = Path(file.filename)

        filename = str(filename_path.stem)
        filename_ext = str(filename_path.suffix)
        filename = filename + "_" + str(int(time.time())) + "_" + filename_ext

        filename = secure_filename(filename)
        file_path = os.path.join(save_directory, filename)

        file.save(file_path)

    new_order = Order(nome_preventivo, data_possibile_vendita, path_pdf_preventivo=file_path, client_id=client_id,
                      id_stato_commessa=selected_id, valore_preventivo=importo)
    db_instance.db.session.add(new_order)
    db_instance.db.session.commit()

    return redirect(url_for("home.get_clients_list"))


@home.route("/update_order", methods=["POST", "GET"])
def update_order():

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

    return render_template("page/home/order_update.html", id=id_cliente, name=name_cliente, order_status_list=order_status_list)


@home.route("/add_order", methods=["POST", "GET"])
def add_order():

    client_id = request.args.get("client_id")
    client_name = request.args.get("client_name")

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

    return render_template("page/home/order_add.html", client_id=client_id, client_name=client_name, order_status_list=order_status_list)


@home.route('/pdf/', methods=["GET", "POST"])
def show_pdf():

    path = request.args.get("path_pdf_preventivo")
    print(path)
    # name = "eric/2210.05189.pdf"
    # save_directory = os.path.join(
    #     get_root_dir_abs_path(), "..", "static", "uploads", name)

    return send_file(path, mimetype='application/pdf')