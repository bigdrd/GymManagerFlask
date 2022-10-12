from app import app
from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import and_
from datetime import datetime , timedelta,date
import pandas as pd
import calendar
from dateutil.relativedelta import *
    
class Gestori(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    privilegi = db.Column(db.Integer)
    def __repr__(self):
        return '<User {}>'.format(self.username)    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Soci(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    cognome = db.Column(db.String(64))
    dataNascita = db.Column(db.String(64))
    comuneNascita = db.Column(db.String(64))
    comuneResidenza = db.Column(db.String(64))
    viaResidenza = db.Column(db.String(64))
    codicePostaleResidenza = db.Column(db.String(64))
    codiceFiscale = db.Column(db.String(64))
    cellulare = db.Column(db.String(64))
    email = db.Column(db.String(64))
    noteExtra = db.Column(db.String(200))
    certificatoMedico = db.Column(db.Boolean())
    codTessera = db.Column(db.Integer)
    nome_genitore = db.Column(db.String(64),default="")
    cognome_genitore = db.Column(db.String(64),default="")
    codfiscale_genitore = db.Column(db.String(64),default="")
    active = db.Column(db.Integer,default=1)
    payDay = db.Column(db.Integer,default=-1)
    rDate = db.Column(db.DateTime,default=datetime.now())

    def getNumeroIscrizioniSettimanali():
        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return db.session.query(Soci).filter(and_(Soci.rDate <= end, Soci.rDate >= start)).count()

    def getSoldiDatiFinoAdOra(self):
        soldi = 0
        idRicevute = db.session.query(RicevutePerSocio.idRicevuta).filter_by(idSocio=self.id)
        for ric in db.session.query(Ricevute).filter(Ricevute.id.in_(idRicevute)).all():
            soldi += ric.euro
        return soldi

    def getEventi(self):
        return db.session.query(EventiPerSocio).filter_by(idSocio=self.id).all()
        
    def getCorsiIscrivibili(self):
        idCorsiFatti = db.session.query(CorsiPerSocio.idCorso).filter_by(idSocio=self.id)
        return db.session.query(Corsi).filter(Corsi.id.notin_(idCorsiFatti)).all()

    def getMesiAnticipo(self):
        mesi = pd.date_range(app.config["MESE_ANTICIPI_START"],app.config["MESE_ANTICIPI_END"], freq='MS').strftime("%Y-%m").tolist()
        if self.payDay != None:
            if int(datetime.today().strftime("%d")) < self.payDay:
                mesi.insert(0,datetime.today().strftime("%Y-%m"))
        return mesi

    def getMesiDaQuandoIscritto(self):
        dataDiIscrione = self.rDate.strftime("%Y-%m")  
        return pd.date_range(dataDiIscrione,app.config["MESE_CORRENTE"], freq='MS').strftime("%Y-%m").tolist()

    def getCorsi(self):
        c = db.session.query(CorsiPerSocio.idCorso).filter_by(idSocio=self.id)
        return db.session.query(Corsi).filter(Corsi.id.in_(c)).all()

    def getCorsiPerMesiPagati(self):
        mesiPagati = db.session.query(MensilePagati).filter_by(idSocio=self.id)
        out = []
        for m in mesiPagati:
            out.append((m.mese.strftime("%Y-%m"),m.idCorso))
        return out

    def getCorsiPerMesiDaPagareAnticipo(self):
        out = []
        for corsi in self.getCorsi():
            for mesi in self.getMesiAnticipo():
                if (mesi,corsi.id) not in self.getCorsiPerMesiPagati():
                    out.append((mesi,corsi))
        return out

    def getCorsiPerMesiDaPagare(self):
        out = []
        for corsi in self.getCorsi():
            print(",,,,,,",corsi.getMesiDaQuandoIscrittoAlCorso(self))
            for mesi in corsi.getMesiDaQuandoIscrittoAlCorso(self):
                if (mesi,corsi.id) not in self.getCorsiPerMesiPagati():
                    out.append((mesi,corsi))
        print(out)
        return out

    def getExtraDaPagare(self):
        extraPagatiId = db.session.query(ExtraPagati.idExtra).filter_by(idSocio=self.id)
        return db.session.query(Extra).filter(Extra.id.notin_(extraPagatiId)).all()

    def èInRegola(self):
        if self.getCorsiPerMesiDaPagare() == []:
            return True
        else:
            return False
        
    def èInRegolaExtra(self):
        if self.getExtraDaPagare() == []:
            return True
        else:
            return False

class Extra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    prezzo = db.Column(db.Float)
    noteExtra = db.Column(db.String(64))
    rDate = db.Column(db.DateTime,default=datetime.now())
    
    def getExtraById(id):
        return db.session.query(Extra).filter_by(id=id).first()

class Corsi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    noteExtra = db.Column(db.String(64))
    rDate = db.Column(db.DateTime,default=datetime.now())
    def getSala(self):
        s = []
        c = db.session.query(SalePerCorso.idSala).filter_by(idCorso=self.id)
        for t in db.session.query(Sale).filter(Sale.id.in_(c)).all():
            s.append(t.nome)
        return ", ".join(s)

    def quantoPaga(self,socioId):
        return db.session.query(CorsiPerSocio.euro).filter_by(idCorso=self.id,idSocio=socioId).first()[0]

    def getTotaleIncassoMensile(self):
        euro = 0
        for x in db.session.query(CorsiPerSocio.euro).filter_by(idCorso=self.id).all():
            euro += x[0]
        return euro

    def getNumeroIscrittiAlCorso(self):
        return db.session.query(CorsiPerSocio).filter_by(idCorso=self.id).count()

    def getSociIscritti(self):
        id = db.session.query(CorsiPerSocio.idSocio).filter_by(idCorso=self.id)
        return db.session.query(Soci).filter(Soci.id.in_(id)).all()

    def getInsegnanti(self):
        s = []
        idIns = db.session.query(InsegnatiPerCorso.idInsegnante).filter_by(idCorso=self.id)
        for t in db.session.query(Insegnanti).filter(Insegnanti.id.in_(idIns)).all():
            s.append(t.nome + " " + t.cognome)
        return ", ".join(s)

    def getInsegnantiObj(self):
        c = db.session.query(InsegnatiPerCorso.idInsegnante).filter_by(idCorso=self.id)
        return db.session.query(Insegnanti).filter(Insegnanti.id.in_(c)).all()

    def getCorsoById(id):
        return db.session.query(Corsi).filter_by(id=id).first()

    def getInsegnantiIscrivibili(self):
        idInsCheGiaPartecipano = db.session.query(InsegnatiPerCorso.idInsegnante).filter_by(idCorso=self.id)
        return db.session.query(Insegnanti).filter(Insegnanti.id.notin_(idInsCheGiaPartecipano)).all()
    
    def getMesiDaQuandoIscrittoAlCorso(self,socio):
        dataDiIscrione = db.session.query(CorsiPerSocio.rDate).filter_by(idSocio=socio.id,idCorso=self.id).first()[0].strftime("%Y-%m")
        mese_start = None
        if datetime.strptime(app.config["MESE_START"],"%Y-%m") > datetime.strptime(dataDiIscrione,"%Y-%m"):
            mese_start = app.config["MESE_START"]
        else:
            mese_start = dataDiIscrione
        mesi = pd.date_range(mese_start,app.config["MESE_CORRENTE"], freq='MS').strftime("%Y-%m").tolist()
        print(mesi)
        if socio.payDay != None:
            if len(mesi) != 1 and int(datetime.today().strftime("%d")) < socio.payDay:
                print("remove")
                try:
                    mesi.pop()
                except:
                    pass
        return mesi

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    noteExtra = db.Column(db.String(64))
    rDate = db.Column(db.DateTime,default=datetime.now())
    
class Insegnanti(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64))
    cognome = db.Column(db.String(64))
    dataNascita = db.Column(db.String(64))
    comuneNascita = db.Column(db.String(64))
    comuneResidenza = db.Column(db.String(64))
    viaResidenza = db.Column(db.String(64))
    codicePostaleResidenza = db.Column(db.String(64))
    codiceFiscale = db.Column(db.String(64))
    cellulare = db.Column(db.String(64))
    email = db.Column(db.String(64))
    certificatoMedico = db.Column(db.Boolean())
    noteExtra = db.Column(db.String(200))
    codTessera = db.Column(db.Integer)
    rDate = db.Column(db.DateTime,default=datetime.now())
    
    def checkIfStipendioPagatoQuestoMese(self):
        if db.session.query(Stipendi).filter_by(idInsegnante=self.id,mese=app.config["MESE_CORRENTE"]).count() > 0:
            return True
        return False


    def getCorsi(self):
        s = []
        idCorsi = db.session.query(InsegnatiPerCorso.idCorso).filter_by(idInsegnante=self.id)
        for t in db.session.query(Corsi.nome).filter(Corsi.id.in_(idCorsi)).all():
            s.append(t[0])
        return ", ".join(s)

    def getStipendioPagatiTable(self):
        return db.session.query(Stipendi).filter_by(idInsegnante=self.id).all()

    def getStipendioMensileTable(self):
            stipendio = []
            for x in db.session.query(InsegnatiPerCorso).filter_by(idInsegnante=self.id).all():
                c = db.session.query(Corsi).filter_by(id=x.idCorso).first()
                if x.metodo == "FISSO":
                    stipendio.append((c.nome,x.metodo,x.cifra,c.id))
                elif x.metodo == "PERCENTUALE":
                    stipendio.append((c.nome,x.metodo + " " + str(x.cifra) +"% di €" + str(c.getTotaleIncassoMensile()),(c.getTotaleIncassoMensile() * x.cifra)/100,c.id))
            return stipendio

    def getStipendioMensile(self):
        stipendio = 0
        for x in db.session.query(InsegnatiPerCorso).filter_by(idInsegnante=self.id).all():
            if x.metodo == "FISSO":
                stipendio += x.cifra
            elif x.metodo == "PERCENTUALE":
                c = db.session.query(Corsi).filter_by(id=x.idCorso).first()
                stipendio += (c.getTotaleIncassoMensile() * x.cifra)/100
        return stipendio

    def getPagatoPerIlCorso(self,idCorso):
        return db.session.query(InsegnatiPerCorso.metodo,InsegnatiPerCorso.cifra).filter_by(idInsegnante=self.id,idCorso=idCorso).first()

class Uscite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(64))
    euro = db.Column(db.Float)
    modPagamento = db.Column(db.String(64))
    rDate = db.Column(db.DateTime,default=datetime.now())

    def getResMensile():
        out = {}
        today = date.today()
        start = today.replace(day=1)
        end = today.replace(day = calendar.monthrange(today.year, today.month)[1])
        for data in pd.date_range(start,end, freq='D').strftime("%Y-%m-%d").tolist():
            giornataEntrata = {"totale":0,"range":""}
            giornataEntrata["totale"] = Ricevute.getRicevuteDi(data)[0]
            giornataEntrata["range"] = Ricevute.getRicevuteDi(data)[1]
            giornataUscita = {"totale":0,"desc":""}
            giornataUscita["totale"] = Uscite.getUsciteDi(data)[0]
            giornataUscita["desc"] = Uscite.getUsciteDi(data)[1]
            out[data] = {"e":giornataEntrata,"u":giornataUscita}
        return out

    def getUsciteMensili():
        today = date.today()
        start = today.replace(day=1)
        end = today.replace(day = calendar.monthrange(today.year, today.month)[1]) + timedelta(days=1)
        uscite = 0
        for x in db.session.query(Uscite).filter(and_(Uscite.rDate < end, Uscite.rDate >= start)):
            uscite += x.euro
        return uscite

    def getUsciteDiOggi():
        today = date.today()
        out = []
        for x in db.session.query(Uscite).all():
            if x.rDate.date() == today:
                out.append(x)
        return out

    def getUsciteDi(data):
        totale = 0
        desc = []
        for x in db.session.query(Uscite).all():
            if x.rDate.date().strftime("%Y-%m-%d") == data:
                totale += x.euro
                desc.append(x.desc)
        return (totale,", ".join(desc))

class Stipendi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idInsegnante = db.Column(db.String(64))
    idUscita = db.Column(db.Integer)
    mese = db.Column(db.String(64)) 
    rDate = db.Column(db.DateTime,default=datetime.now())

    def getEuro(self):
        return db.session.query(Uscite.euro).filter_by(id=self.idUscita).first()
        
class Incassi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(64))
    euro = db.Column(db.Float)
    rDate = db.Column(db.DateTime,default=datetime.now())

    def getIncassiMensili():
        today = date.today()
        start = today.replace(day=1)
        end = today.replace(day = calendar.monthrange(today.year, today.month)[1]) + timedelta(days=1)
        print("ENDDDDDDDD",end)
        incassoSettimanale = 0
        for x in db.session.query(Incassi).filter(and_(Incassi.rDate < end, Incassi.rDate >= start)):
            print(x)
            incassoSettimanale += x.euro
        return incassoSettimanale
    
    def getPercentuale():
        today = date.today() + relativedelta(months=-1)
        start = today.replace(day=1) 
        end = today.replace(day = calendar.monthrange(today.year, today.month)[1]) + timedelta(days=1)
        incassoMeseS = 0
        for x in db.session.query(Incassi).filter(and_(Incassi.rDate < end, Incassi.rDate >= start)):
            incassoMeseS += x.euro
        if incassoMeseS == 0:
            return ("*",0)

        percentuale = (Incassi.getIncassiMensili() * 100) / incassoMeseS
        if percentuale > 100:
            return ("+",percentuale)
        elif percentuale == 100:
            return ("=",percentuale)
        else:
            return ("-",100-percentuale)

class Ricevute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(64))
    euro = db.Column(db.Float)
    modPagamento = db.Column(db.String(64),default="a")
    rDate = db.Column(db.DateTime,default=datetime.now())
    
    def getRicevuteDi(data):
        totale = 0
        tmp = []
        for x in db.session.query(Ricevute).all():
            if x.rDate.date().strftime("%Y-%m-%d") == data:
                tmp.append(x)
                totale += x.euro
        if tmp == []:
            range = ""
        else:
            range = "Ricevute nell'intervallo " + str(tmp[0].id) +"-"+ str(tmp[-1].id)
        return (totale,range)

    def getRicevuteDiOggi():
        today = date.today()
        out = []
        for x in db.session.query(Ricevute).all():
            if x.rDate.date() == today:
                out.append(x)
        return out

class RicevutePerSocio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idRicevuta = db.Column(db.Integer)
    idSocio = db.Column(db.Integer)
    rDate = db.Column(db.DateTime,default=datetime.now())

class InsegnatiPerCorso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idInsegnante = db.Column(db.Integer)
    idCorso = db.Column(db.Integer)
    metodo = db.Column(db.String(64))
    cifra = db.Column(db.Float)
    rDate = db.Column(db.DateTime,default=datetime.now())

class CorsiPerSocio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idCorso = db.Column(db.Integer)
    idSocio = db.Column(db.Integer)
    euro = db.Column(db.Float)
    rDate = db.Column(db.DateTime,default=datetime.now())

class SalePerCorso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idSala = db.Column(db.Integer)
    idCorso = db.Column(db.Integer)
    rDate = db.Column(db.DateTime,default=datetime.now())

class ExtraPagati(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idExtra = db.Column(db.Integer)
    idSocio = db.Column(db.Integer)
    rDate = db.Column(db.DateTime,default=datetime.now())

class MensilePagati(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idCorso = db.Column(db.Integer)
    idSocio = db.Column(db.Integer)
    mese = db.Column(db.DateTime)
    rDate = db.Column(db.DateTime,default=datetime.now())
    
class EventiPerSocio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idEvento = db.Column(db.Integer)
    idSocio = db.Column(db.Integer)
    desc = db.Column(db.String(64))
    rDate = db.Column(db.DateTime,default=datetime.now())

    def getCorso(self):
        return db.session.query(Corsi).filter_by(id=self.idEvento).first()
    def getRicevuta(self):
        return db.session.query(Ricevute).filter_by(id=self.idEvento).first()
    def getSocio(self):
        return db.session.query(Soci).filter_by(id=self.idSocio).first()


class Entrate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rDate = db.Column(db.DateTime,default=datetime.now())

    def getEntrateMensili():
        today = date.today()
        start = today.replace(day=1)
        end = today.replace(day = calendar.monthrange(today.year, today.month)[1]) + timedelta(days=1)
        incassoSettimanale = 0
        for x in db.session.query(Entrate).filter(and_(EntratePerSocio.rDate < end, EntratePerSocio.rDate >= start)):
            incassoSettimanale += 1
        return incassoSettimanale

class EntratePerSocio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idSocio = db.Column(db.Integer)
    count = db.Column(db.Integer)
    lastTime = db.Column(db.DateTime)
    rDate = db.Column(db.DateTime,default=datetime.now())

    


@login.user_loader
def load_user(id):
    return Gestori.query.get(int(id))