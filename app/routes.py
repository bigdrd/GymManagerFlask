from app import app,db
from . import tornello
import ftplib
from threading import Thread
from flask import render_template,session,make_response
from flask_login import current_user, login_user
from app.models import Gestori,Soci,Corsi,CorsiPerSocio,Insegnanti,Sale,Incassi,InsegnatiPerCorso,SalePerCorso,Ricevute,Extra,MensilePagati,ExtraPagati,RicevutePerSocio,EventiPerSocio,Uscite,Stipendi,EntratePerSocio,Entrate
from flask_login import logout_user
from flask_login import login_required
from app.forms import LoginForm,addSociForm,addInsegnantiForm,addSalaForm,preRicevutaForm,addExtraForm,addUscitaForm,stipendioForm
from flask import flash,redirect,url_for,request
from werkzeug.urls import url_parse
import datetime as dt
from datetime import datetime,date
from flask_weasyprint import HTML, render_pdf
import os

@app.before_first_request
def function_to_run_only_once():
    print("START TORNELLO")
    t = Thread(target=tornello.openOrCloseDoorListener, args=())
    t.start()
#########################################################################################################################################################
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file("templates/static/img/favicon.ico")

@app.route('/')
@app.route('/gestione')
@login_required
def incasso():
    incassoMensile = Incassi.getIncassiMensili()
    usciteMensili = Uscite.getUsciteMensili()
    entrateTornello = Entrate.getEntrateMensili()
    iscrizioniSettimanali = Soci.getNumeroIscrizioniSettimanali()
    eventi = EventiPerSocio.query.all()
    iscrizioniTotali = Soci.query.filter_by(active=1).count()
    return render_template('gestione.html',user=current_user,title="Gestione",entrateTornello=entrateTornello,incassoMensile=incassoMensile,incassiPercentuale=Incassi.getPercentuale(),iscrizioniSettimanali=iscrizioniSettimanali,sociTotali=iscrizioniTotali,eventi=eventi,usciteMensili=usciteMensili)
#########################################################################################################################################################
@app.route('/cerca/<attivo>')
@login_required
def soci(attivo):
    soci = Soci.query.all()
    corsi = Corsi.query.all()
    insegnanti = Insegnanti.query.all()
    sale = Sale.query.all()
    extra = Extra.query.all()
    uscite = Uscite.query.all()
    return render_template('cerca.html',user=current_user,title="Cerca",soci=soci,att=int(attivo),corsi=corsi,insegnanti=insegnanti,sale=sale,extra=extra,uscite=uscite)
############################################################### LOGIN ####################################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('incasso'))
    if Gestori.query.all() == []:
        a = Gestori(username="Michela",privilegi=0)
        a.set_password("mimaelca")
        b = Gestori(username="Martina",privilegi=0)
        b.set_password("mimaelca")
        db.session.add(a)
        db.session.add(b)
        db.session.commit()
    form = LoginForm()
    if form.validate_on_submit():
        user = Gestori.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        # session = ftplib.FTP('ftp.mbdancebackup.altervista.org','mbdancebackup','J8N9zgbKRxXa')
        # file = open('../backup/dbBACKUP.db','rb')
        # session.storbinary('STOR dbBACKUP.db', file)
        # file.close()
        # session.quit()
        return redirect(url_for('incasso',attivo=1))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
#############################################################################################################################################################
############################################################### ADD OBJECT ##################################################################################
@app.route('/success')
@login_required
def success():
    return render_template('success.html',user=current_user,title="Successo")

@app.route('/addUscita' , methods=['GET', 'POST'])
@login_required
def addUscita():
    form = addUscitaForm()
    if form.validate_on_submit():
        if form.metodoPagamento.data == 1:
            mod = "Contanti"
        elif form.metodoPagamento.data == 2:
            mod = "Bonifico"
        elif form.metodoPagamento.data == 3:
            mod = "Assegno"
        uscita = Uscite(desc=form.nome.data.strip().upper(),euro=float(form.euro.data),modPagamento=mod)
        db.session.add(uscita)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('addUscita.html',user=current_user,title="Inserisci Uscita",form=form)

@app.route('/addSoci' , methods=['GET', 'POST'])
@login_required
def addSoci():
    if request.method == "POST":

        dizCorsoPerSoci = {}
        for x in request.form.lists():
            if "corso" in x[0] or "euro" in x[0]:
                index = x[0].split("_")[0]
                if index not in dizCorsoPerSoci:
                    dizCorsoPerSoci[index] = {}
                dizCorsoPerSoci[index][x[0].split("_")[1]] = x[1][0]
        if "certificatoMedico" in request.form.to_dict():
            cM = True
        else:
            cM = False
        socio = Soci(nome=request.form.to_dict()["nome"].strip().upper(),
                    cognome=request.form.to_dict()["cognome"].strip().upper(),
                    dataNascita=request.form.to_dict()["dataNascita"].strip().upper(),
                    comuneNascita=request.form.to_dict()["comuneNascita"].strip().upper(),
                    comuneResidenza=request.form.to_dict()["comuneResidenza"].strip().upper(),
                    viaResidenza=request.form.to_dict()["viaResidenza"].strip().upper(),
                    codicePostaleResidenza=request.form.to_dict()["codicePostaleResidenza"].strip().upper(),
                    codiceFiscale=request.form.to_dict()["codiceFiscale"].strip().upper(),
                    cellulare=request.form.to_dict()["cellulare"].strip().upper(),
                    email=request.form.to_dict()["email"].strip().upper(),
                    noteExtra=request.form.to_dict()["noteExtra"].strip().upper(),
                    codTessera=request.form.to_dict()["codTessera"].strip(),
                    certificatoMedico=cM,
                    payDay=app.config["PAYDAY"])
        db.session.add(socio)
        db.session.flush()
        db.session.add(EventiPerSocio(idEvento=socio.id,idSocio=int(socio.id),desc="I"))
        for x in dizCorsoPerSoci:
            db.session.add(CorsiPerSocio(idCorso=int(dizCorsoPerSoci[x]["corso"]),idSocio=socio.id,euro=float(dizCorsoPerSoci[x]["euro"])))
            db.session.add(EventiPerSocio(idEvento=int(dizCorsoPerSoci[x]["corso"]),idSocio=int(socio.id),desc="IC"))
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('addSoci.html',user=current_user,title="Inserisci Socio",corsi=Corsi.query.all())

@app.route('/addCorsi' , methods=['GET', 'POST'])
@login_required
def addCorsi():
    if request.method == 'POST':
        nome = ""
        sale = []
        extra = ""
        dizInsPerCors = {}
        i = 0
        for x in request.form.lists():
            if x[0] == "nome":
                nome = x[1][0]
            elif x[0] == "sale":
                sale = x[1]
            elif x[0] == "extra":
                extra = x[1][0]
            else:
                index = x[0].split("_")[0]
                if index not in dizInsPerCors:
                    dizInsPerCors[index] = {}
                dizInsPerCors[index][x[0].split("_")[1]] = x[1][0]
        corso = Corsi(nome=nome.strip().upper(),noteExtra=extra.strip().upper())
        db.session.add(corso)
        db.session.flush()
        for x in sale:
            db.session.add(SalePerCorso(idCorso=corso.id,idSala=int(x)))
        db.session.flush()
        for x in dizInsPerCors:
            db.session.add(InsegnatiPerCorso(idCorso=corso.id,idInsegnante=int(dizInsPerCors[x]["insegnanti"]),metodo=dizInsPerCors[x]["modPagamento"].strip().upper(),cifra=float(dizInsPerCors[x]["europercentuale"])))
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('addCorsi.html',user=current_user,title="Inserisci Corso",insegnanti=Insegnanti.query.all(),sale=Sale.query.all())

@app.route('/addSala' , methods=['GET', 'POST'])
@login_required
def addSala():
    form = addSalaForm()
    if form.validate_on_submit():
        sala = Sale(nome=form.nome.data.strip().upper(),noteExtra=form.noteExtra.data.strip().upper())
        db.session.add(sala)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('addSala.html',user=current_user,title="Inserisci Sala",form=form)

@app.route('/addExtra' , methods=['GET', 'POST'])
@login_required
def addExtra():
    form = addExtraForm()
    if form.validate_on_submit():
        extra = Extra(nome=form.nome.data.strip().upper(),prezzo=float(form.euro.data),noteExtra=form.noteExtra.data.strip().upper())
        db.session.add(extra)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('addExtra.html',user=current_user,title="Inserisci Extra",form=form)

@app.route('/addInsegnante' , methods=['GET', 'POST'])
@login_required
def addInsegnanti():
    form = addInsegnantiForm()
    if form.validate_on_submit():
        ins = Insegnanti(nome=form.nome.data.strip().upper(),
                        cognome=form.cognome.data.strip().upper(),
                        dataNascita=form.dataNascita.data.strip().upper(),
                        comuneNascita=form.comuneNascita.data.strip().upper(),
                        comuneResidenza=form.comuneResidenza.data.strip().upper(),
                        viaResidenza=form.viaResidenza.data.strip().upper(),
                        codicePostaleResidenza=form.codicePostale.data.strip().upper(),
                        codiceFiscale=form.codiceFiscale.data.strip().upper(),
                        cellulare=form.cellulare.data.strip().upper(),
                        email=form.email.data.strip().upper(),
                        noteExtra=form.noteExtra.data.strip().upper(),
                        codTessera=form.codiceTessera.data.strip().upper())
        db.session.add(ins)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('addInsegnanti.html',user=current_user,title="Inserisci Insegnante",form=form)
###########################################################################################################################################################
############################################################### PROFILI ###################################################################################
@app.route('/socio/<int:id>', methods=["POST","GET"])
@login_required
def socio(id):
    if request.method == "POST":
        dati = request.form.to_dict()
        print(dati)
        if "certificatoMedico" in dati:
            if dati["certificatoMedico"] == "on":
                dati["certificatoMedico"] = True
        else:
            dati["certificatoMedico"] = False
        if "codTessera" in dati and dati["codTessera"] != "":
            with open('../NONTOCCARE/cod_nuovo_tornello.txt',"w+") as f:
                pass
        Soci.query.filter_by(id=id).update(dati)
        db.session.commit()
        return redirect(url_for('socio',id=id))
        
    socio = Soci.query.filter_by(id=id).first()
    return render_template('socio.html',user=current_user,title=socio.nome + " " + socio.cognome,socio=socio,corsi=Corsi.query.all())


@app.route("/sala/<int:id>", methods=["POST","GET"])
@login_required
def sale(id):
    sala = Sale.query.filter_by(id=id).first()
    if request.method == "POST":
        dati = request.form.to_dict()
        Sale.query.filter_by(id=id).update(dati)
        db.session.commit()
        return redirect(url_for('sale',id=id))
    return render_template('sala.html',user=current_user,title=sala.nome,sala=sala)

@app.route("/extra/<int:id>", methods=["POST","GET"])
@login_required
def extra(id):
    extra = Extra.query.filter_by(id=id).first()
    if request.method == "POST":
        dati = request.form.to_dict()
        Extra.query.filter_by(id=id).update(dati)
        db.session.commit()
        return redirect(url_for('extra',id=id))
    return render_template('extra.html',user=current_user,title=extra.nome,extra=extra)

@app.route("/uscita/<int:id>", methods=["POST","GET"])
@login_required
def uscitaP(id):
    sala = Sale.query.filter_by(id=id).first()
    return render_template('sala.html',user=current_user,title=corso.nome,sala=sala)

@app.route("/insegnante/<int:id>", methods=["POST","GET"])
@login_required
def insegnante(id):
    if request.method == "POST":
        dati = request.form.to_dict()
        print(request.form)
        if "certificatoMedico" in dati:
                if dati["certificatoMedico"] == "on":
                    dati["certificatoMedico"] = True
        else:
            dati["certificatoMedico"] = False
        if "codTessera" in dati and dati["codTessera"] != "":
            with open('../NONTOCCARE/cod_nuovo_tornello.txt',"w+") as f:
                pass
        Insegnanti.query.filter_by(id=id).update(dati)
        db.session.commit()
    ins = Insegnanti.query.filter_by(id=id).first()
    return render_template('insegnante.html',user=current_user,title=ins.nome + " " + ins.cognome,ins=ins)

@app.route("/corso/<int:id>", methods=["POST","GET"])
@login_required
def corso(id):
    if request.method == "POST":
        dati = request.form.to_dict()
        print(request.form)
        Corsi.query.filter_by(id=id).update(dati)
        db.session.commit()
    c = Corsi.query.filter_by(id=id).first()
    return render_template('corso.html',user=current_user,title=c.nome,corso=c)
###########################################################################################################################################################
############################################################### RICEVUTE ##################################################################################
@app.route('/ricevuta/<string:id>',methods=['GET', 'POST'])
@login_required
def ricevuta(id=""):
    nR = Ricevute.query.order_by(Ricevute.id.desc()).first()
    if nR == None:
        nR = 0
    else:
        nR = nR.id
    if request.method == 'GET':
        sociIntestatari = db.session.query(Soci).filter(Soci.id.in_(id.split("_"))).all()
    if request.method == 'POST':
        sociList = set()
        dizChecked = {}
        descrizioni = []
        modPagamento = ""
        include_genitore = "off"
        euro = 0
        sconto = request.form.to_dict()["sconto"]
        noteExtra = {}
        print(request.form.to_dict())
        for x in request.form.to_dict():
            if x[0] == "C":
                
                dati = x.split("+")[1]
                print(dati)
                idSocio = dati.split("_")[0]
                sociList.add(idSocio)
                idCorso = dati.split("_")[1]
                mese = datetime.strptime(dati.split("_")[2],"%Y-%m")
                descrizioni.append(Corsi.getCorsoById(idCorso).nome + " " + mese.strftime("%Y-%m"))
                db.session.add(MensilePagati(idCorso=int(idCorso),idSocio=int(idSocio),mese=mese,rDate=datetime.now()))
                if db.session.query(Soci).filter_by(id=idSocio).one().payDay == -1 or db.session.query(Soci).filter_by(id=idSocio).one().payDay == None:
                    Soci.query.filter_by(id=idSocio).update({"payDay":app.config["PAYDAY"]})
                
                #PER PDF   
                socio = db.session.query(Soci).filter_by(id=idSocio).one()
                socioIndex = socio.nome + " " + socio.cognome
                noteExtra[socioIndex] = request.form.to_dict()["noteExtra-" + idSocio]
                corso = Corsi.getCorsoById(idCorso)
                if  socioIndex not in dizChecked:
                    dizChecked[socioIndex] = {}
                dizChecked[socioIndex]["Mensile " + corso.nome + " " + mese.strftime("%Y-%m")] = corso.quantoPaga(socio.id)

                
            # if x[0] == "E":
            #     dati = x.split("+")[1]
            #     idSocio = dati.split("_")[0]
            #     sociList.add(idSocio)
            #     idExtra = dati.split("_")[1]
            #     descrizioni.append(Extra.getExtraById(idExtra).nome)
            #     db.session.add(ExtraPagati(idSocio=int(idSocio),idExtra=int(idExtra)))
                
            #     #PER PDF
            #     socio = db.session.query(Soci).filter_by(id=idSocio).one()
            #     socioIndex = socio.nome + " " + socio.cognome
            #     extra = db.session.query(Extra).filter_by(id=idExtra).one()
            #     if socioIndex not in dizChecked:
            #         dizChecked[socioIndex] = {}
            #     dizChecked[socioIndex][extra.nome] = extra.prezzo

            if x == "euro":
                euro = request.form.to_dict()[x].replace("€","")

            if x == "mod":
                mod = request.form.to_dict()[x]
            
            if x == "include_genitore":
                include_genitore = request.form.to_dict()[x]
                print("INCLUDE:",include_genitore)

        #SISTEMA MODELLO FATTURA E INCASSI
        ric = Ricevute(euro=float(euro),desc=", ".join(descrizioni).strip().upper(),modPagamento=mod,rDate=datetime.now())
        db.session.add(ric)
        db.session.add(Incassi(desc=", ".join(descrizioni).strip().upper(),euro=float(euro),rDate=datetime.now()))
        db.session.flush()
        for soci in db.session.query(Soci).filter(Soci.id.in_(list(sociList))).all():
            db.session.add(RicevutePerSocio(idRicevuta=ric.id,idSocio=int(soci.id),rDate=datetime.now()))
            db.session.add(EventiPerSocio(idEvento=ric.id,idSocio=int(soci.id),desc="R",rDate=datetime.now()))
        db.session.commit()

        #RENDERIZZA PDF
        html = render_template('pdfRicevuta.html',nR=nR+1,dataOggi=dt.date.today().strftime("%d-%m-%Y"),sociIntestatari=db.session.query(Soci).filter(Soci.id.in_(list(sociList))).all(),totale=float(euro),dati=dizChecked,modPagamento=mod,noteExtra=noteExtra,sconto=sconto,include_genitore=include_genitore)
        pdf = HTML(string=html) 
        with open('../ricevute/ricevuta-n'+str(nR+1)+".pdf", "w+") as file1:
            pdf.write_pdf('../ricevute/ricevuta-n'+str(nR+1)+".pdf")
        return render_pdf(pdf)

    return render_template('ricevuta.html',user=current_user,title="Ricevuta",numeroRicevuta=nR+1,sociIntestatari=sociIntestatari,dataOggi=dt.date.today())

@app.route('/preRicevuta',methods=['GET', 'POST'])
@login_required
def preRicevuta():
    nR = Ricevute.query.order_by(Ricevute.id.desc()).first()
    if nR == None:
        nR = 0
    else:
        nR = nR.id
    form = preRicevutaForm()
    if form.validate_on_submit():
        return redirect("/ricevuta/" + "_".join([str(int) for int in form.soci.data]))
    return render_template('preRicevuta.html',user=current_user,title="Ricevuta",form=form,numeroRicevuta=nR+1)
###########################################################################################################################################################
############################################################### STIPENDI ##################################################################################
@app.route('/preStipendio' , methods=['GET', 'POST'])
@login_required
def stipendioIns():
    form = stipendioForm()
    if form.validate_on_submit():
        return redirect("/stipendio/" + "_".join([str(int) for int in [form.ins.data]]))
    return render_template('preStipendio.html',user=current_user,title="Stipendio",form=form)

@app.route('/stipendio/<string:id>',methods=['GET', 'POST'])
@login_required
def stipendio(id=""):
    insIntestatari = db.session.query(Insegnanti).filter(Insegnanti.id.in_(id.split("_"))).all()
    if request.method == 'POST':
        print(request.form.to_dict())
        dati = request.form.to_dict()
        desc = []
        for x in insIntestatari:
            desc.append("Stipendio " + x.nome + " " + x.cognome)
        uscita = Uscite(desc=" ".join(desc).strip().upper(),euro=float(dati["euro"].split("€")[1]))
        db.session.add(uscita)
        db.session.flush()
        mese = datetime.now().strftime("%Y-%m")
        for x in insIntestatari:
            stipendio = Stipendi(idInsegnante=x.id,idUscita=uscita.id,mese=mese)
            db.session.add(stipendio)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('stipendio.html',user=current_user,title="Stipendio",insIntestatari=insIntestatari,dataOggi=dt.date.today())
###########################################################################################################################################################
############################################################### RESOCONTI #################################################################################
@app.route('/resGiornaliero')       
@login_required
def resGiornaliero():
    #RENDERIZZA PDF
    ricevuteOggi = Ricevute.getRicevuteDiOggi()
    usciteOggi = Uscite.getUsciteDiOggi()
    bilancioOggi = 0
    for x in ricevuteOggi:
        bilancioOggi += x.euro
    for x in usciteOggi:
        bilancioOggi -= x.euro
    if bilancioOggi >= 0:
        bilancioOggi = "+" + str(bilancioOggi)
    else:
        str(bilancioOggi)
    html = render_template('pdfResGiornaliero.html',dataOggi=dt.date.today().strftime("%d-%m-%Y"),ricevuteOggi=ricevuteOggi,usciteOggi=usciteOggi,bilancioOggi=bilancioOggi)
    pdf = HTML(string=html)
    print(os.getcwd())
    with open('../resocontiGiornalieri/resG-'+dt.date.today().strftime("%d-%m-%Y")+".pdf", "w+") as file1:
        pdf.write_pdf('../resocontiGiornalieri/resG-'+dt.date.today().strftime("%d-%m-%Y")+".pdf")
    return render_pdf(pdf)

@app.route('/resMensile')       
@login_required
def resMensile():
    #RENDERIZZA PDF
    resMensile = Uscite.getResMensile()
    html = render_template('pdfResMensile.html',dataOggi=dt.date.today().strftime("%Y-%m"),resMensile=resMensile)
    pdf = HTML(string=html) 
    with open('../resocontiMensili/resM-'+dt.date.today().strftime("%Y-%m")+".pdf", "w+") as file1:
        pdf.write_pdf('../resocontiMensili/resM-'+dt.date.today().strftime("%Y-%m")+".pdf")
    return render_pdf(pdf)
######################################################################################################################################################
############################################################### API ##################################################################################
@app.route('/api/getLastCodCard',methods=['GET', 'POST'])
@login_required
def getLastCodCard():
    try:
        with open('../NONTOCCARE/cod_nuovo_tornello.txt') as f:
            cod = f.readline()
        return {"success":1,"cod":str(cod)}
    except Exception as e:
        print(e)
        return {"success":0,"cod":""}
    

@app.route('/api/elimina/<string:tipo>/<int:id>',methods=['GET', 'POST'])
@login_required
def elimina(tipo,id):
    if tipo == "corso":
        Corsi.query.filter_by(id=id).delete()
        db.session.query(CorsiPerSocio).filter_by(idCorso=id).delete()
        db.session.query(SalePerCorso).filter_by(idCorso=id).delete()
        db.session.query(InsegnatiPerCorso).filter_by(idCorso=id).delete()
    elif tipo == "sala":
        Sale.query.filter_by(id=id).delete()
        db.session.query(SalePerCorso).filter_by(idSala=id).delete()
    elif tipo == "socio":
        Soci.query.filter_by(id=id).update({"active":0})
        db.session.query(CorsiPerSocio).filter_by(idSocio=id).delete()
    elif tipo == "insegnante":
        Insegnanti.query.filter_by(id=id).delete()
        db.session.query(InsegnatiPerCorso).filter_by(idInsegnante=id).delete()
    elif tipo == "ricevuta":
        Ricevute.query.filter_by(id=id).delete()
        db.session.query(RicevutePerSocio).filter_by(idRicevuta=id).delete()
    elif tipo == "uscita":
        Uscite.query.filter_by(id=id).delete()
        db.session.query(Stipendi).filter_by(idUscita=id).delete()
    db.session.commit()
    return redirect(url_for('success'))

@app.route('/api/modificaCorsiPerSoci/<int:idSocio>/<int:idCorso>/<euro>',methods=['GET', 'POST'])
@login_required
def modificaCorsiPerSoci(idSocio,idCorso,euro):
    CorsiPerSocio.query.filter_by(idCorso=idCorso,idSocio=idSocio).update({"euro":float(euro)})
    db.session.commit()
    return {}

@app.route('/api/addCorsiPerSoci/<int:idSocio>/<int:idCorso>/<euro>',methods=['GET', 'POST'])
@login_required
def addCorsiPerSoci(idSocio,idCorso,euro):
    print(euro)
    db.session.add(CorsiPerSocio(idCorso=idCorso,idSocio=idSocio,euro=float(euro)))
    db.session.commit()
    return {}

@app.route('/api/eliminaCorsiPerSoci/<int:idSocio>/<int:idCorso>',methods=['GET', 'POST'])
@login_required
def eliminaCorsiPerSoci(idSocio,idCorso):
    CorsiPerSocio.query.filter_by(idCorso=idCorso,idSocio=idSocio).delete()
    db.session.commit()
    return {}

@app.route('/api/addInsegnantiPerCorso/<int:idCorso>/<int:idInsegnante>/<int:modPagamento>/<euro>',methods=['GET', 'POST'])
@login_required
def addInsegnantiPerCorso(idCorso,idInsegnante,modPagamento,euro):
    if modPagamento == 2:
        mod="FISSO"
    elif modPagamento == 1:
        mod = "PERCENTUALE"
    db.session.add(InsegnatiPerCorso(idCorso=idCorso,idInsegnante=idInsegnante,cifra=float(euro),metodo=mod))
    db.session.commit()
    return {}

@app.route('/api/eliminaInsegnantiPerCorso/<int:idCorso>/<int:idInsegnante>',methods=['GET', 'POST'])
@login_required
def eliminaInsegnantiPerCorso(idCorso,idInsegnante):
    InsegnatiPerCorso.query.filter_by(idCorso=idCorso,idInsegnante=idInsegnante).delete()
    db.session.commit()
    return {}

@app.route('/api/modificaInsegnantiPerCorso/<int:idCorso>/<int:idInsegnante>/<int:modPagamento>/<euro>',methods=['GET', 'POST'])
@login_required
def modificaInsegnantiPerCorso(idCorso,idInsegnante,modPagamento,euro):
    print(idCorso,idInsegnante,modPagamento,euro)
    if modPagamento == 2:
        mod="FISSO"
    elif modPagamento == 1:
        mod = "PERCENTUALE"
    InsegnatiPerCorso.query.filter_by(idCorso=idCorso,idInsegnante=idInsegnante).update({"cifra":float(euro),"metodo":mod})
    db.session.commit()
    return {}
######################################################################################################################################################
############################################################### ERROR HANDLING #######################################################################
@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html',user=current_user), 404

@app.errorhandler(500)
def internalError(e):
    session = ftplib.FTP('ftp.mbdancebackup.altervista.org','mbdancebackup','J8N9zgbKRxXa')
    file = open('../backup/logServer.txt','rb')
    session.storbinary('STOR logServer.txt', file)
    file.close()
    file = open('../backup/logMigrations.txt','rb')
    session.storbinary('STOR logMigrations.txt', file)
    file.close()
    session.quit()
    return render_template('500.html',user=current_user), 500

















