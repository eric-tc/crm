from .database_instance import db_instance
from datetime import datetime

class Clients(db_instance.db.Model):

    print("LOCAL CLASS")
    id = db_instance.db.Column(db_instance.db.Integer, primary_key=True)
    name = db_instance.db.Column(db_instance.db.String(100))
    email = db_instance.db.Column(db_instance.db.String(100)) 
    orders = db_instance.db.relationship('Order', backref='clients', lazy=True)
    
    def __init__(self,name, email):

        self.name= name
        self.email=email

class OrderStatus(db_instance.db.Model):

    """
        Sono i valori pesati della commessa. Cioè la probabilità che 
        qusta si concluda in una vendita
    """ 
    id = db_instance.db.Column(db_instance.db.Integer, primary_key=True)
    order_status = db_instance.db.Column(db_instance.db.String(100))
    percentage = db_instance.db.Column(db_instance.db.String(100)) 
    #uselist=False set a one to one relationship
    orders = db_instance.db.relationship('Order', uselist=False, backref="order_status")
    
    @classmethod
    def create_predefined_rows(cls):
        """
        Crea le righe predefinite. Queste variabili non cambiano

        """
        predefined_rows = [
            OrderStatus(order_status='Buyer_Interest', percentage=25),
            OrderStatus(order_status='ROI_established', percentage=30),
            OrderStatus(order_status='Timing Known', percentage=40),
            OrderStatus(order_status='DMU_Established', percentage=60),
            OrderStatus(order_status='Proposal_Sent', percentage=75),
        ]
        
        db_instance.db.session.bulk_save_objects(predefined_rows)
        db_instance.db.session.commit()

class Order(db_instance.db.Model):
    id = db_instance.db.Column(db_instance.db.Integer, primary_key=True)
    date =db_instance.db.Column(db_instance.db.DateTime, default=datetime.utcnow)
    nome_preventivo=db_instance.db.Column(db_instance.db.String(255))
    data_possibile_vendita= db_instance.db.Column(db_instance.db.DateTime)
    path_pdf_preventivo=db_instance.db.Column(db_instance.db.String(255))
    valore_preventivo=db_instance.db.Column(db_instance.db.Float)
    #One to Many. One Client can have multiple order
    clients_id = db_instance.db.Column(db_instance.db.Integer, db_instance.db.ForeignKey('clients.id'), nullable=False)
    #One to One Relationship with Order Status
    order_status_id = db_instance.db.Column(db_instance.db.Integer, db_instance.db.ForeignKey('order_status.id'), nullable=False)
    
    
    def __init__(self, nome_preventivo,data_possibile_vendita,path_pdf_preventivo,client_id, id_stato_commessa,valore_preventivo):
        
        self.nome_preventivo= nome_preventivo
        self.data_possibile_vendita= data_possibile_vendita
        self.path_pdf_preventivo=path_pdf_preventivo
        self.clients_id=client_id
        self.order_status_id=id_stato_commessa
        self.valore_preventivo=valore_preventivo


class OrderData(db_instance.db.Model):
    
    id = db_instance.db.Column(db_instance.db.Integer, primary_key=True)
    irrisolta = db_instance.db.Column(db_instance.db.Text)
    altre_soluzioni = db_instance.db.Column(db_instance.db.Text)
    non_funzionano = db_instance.db.Column(db_instance.db.Text)
    investimento = db_instance.db.Column(db_instance.db.Text)
    costo_associato = db_instance.db.Column(db_instance.db.Text)
    soluzioni_proposte = db_instance.db.Column(db_instance.db.Text)
    sistema_regime = db_instance.db.Column(db_instance.db.Text)
    altre_persone = db_instance.db.Column(db_instance.db.Text)
    clienti_lamentele = db_instance.db.Column(db_instance.db.Text)
    segnali_positivi = db_instance.db.Column(db_instance.db.Text)
    order_id = db_instance.db.Column(db_instance.db.Integer, db_instance.db.ForeignKey('order.id'), nullable=False)

    def __init__(self, irrisolta, altre_soluzioni, non_funzionano, investimento, costo_associato,
                 soluzioni_proposte, sistema_regime, altre_persone, clienti_lamentele, segnali_positivi,order_id):
        self.irrisolta = irrisolta
        self.altre_soluzioni = altre_soluzioni
        self.non_funzionano = non_funzionano
        self.investimento = investimento
        self.costo_associato = costo_associato
        self.soluzioni_proposte = soluzioni_proposte
        self.sistema_regime = sistema_regime
        self.altre_persone = altre_persone
        self.clienti_lamentele = clienti_lamentele
        self.segnali_positivi = segnali_positivi
        self.order_id= order_id