from app import app,db
from app.models import Soci,Insegnanti,EventiPerSocio,EntratePerSocio,Entrate
import socket
from datetime import datetime , timedelta,date
import time

def puoEntrare(entratePerSocio):
    if entratePerSocio.count == 0:
        entratePerSocio.count += 1
        return True
    elif entratePerSocio.count == 1:
        entratePerSocio.count += 1
        return True
    elif entratePerSocio.count == 2:
        if datetime.now() < entratePerSocio.lastTime + timedelta(minutes = 10):
            return False
        else:
            entratePerSocio.count = 1
            entratePerSocio.lastTime = datetime.now()
            return True  


def convertByteToIdCard(fromTornello):
    try:
        raw = fromTornello.strip()
        hex = raw.hex()
        cod = int(hex,16)
        return cod
    except:
        return -1


def openOrCloseDoorListener():
    while 1:
        try:
            with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
                file_object.write("--------------------------------------------STARTED\n")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((app.config["IP_TORNELLO"], app.config["PORT_TORNELLO"]))
            s.settimeout(50)
        except Exception as e: 
            with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
                    file_object.write(str(e) + "\n")
            time.sleep(2)
            continue
        with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
            file_object.write("OPENED SOCKET \n")
        while(1): 
            try:    
                data = s.recv(1024)
                cod = convertByteToIdCard(data)
                if data == 0 or len(data) == 0 or cod == -1:
                    with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
                        file_object.write("EXITED \n")
                    break
                with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
                    file_object.write(str(cod) + "\n")
                if cod == 5199153: #qualcuno passa per l'uscita
                    pass
                elif cod == 5199154: #qualcuno passa per l'entrata
                    pass
                else:
                    if db.session.query(Soci).filter_by(codTessera=cod).first() != None:
                        socio = db.session.query(Soci).filter_by(codTessera=cod).first()
                        if socio.èInRegola() == True:
                            if db.session.query(EntratePerSocio).filter_by(idSocio=socio.id).first() == None:
                                db.session.add(EntratePerSocio(idSocio=int(socio.id),count=0,lastTime=datetime.now()))
                            if puoEntrare(db.session.query(EntratePerSocio).filter_by(idSocio=socio.id).first()) == False:
                                continue
                            e = Entrate()
                            db.session.add(e)
                            db.session.flush()
                            print("COD ACCETTATO")
                            s.send(b"OP1\n")
                            db.session.add(EventiPerSocio(idEvento=e.id,idSocio=int(db.session.query(Soci).filter_by(codTessera=cod).first().id),desc="E"))
                        db.session.commit()
                    elif db.session.query(Insegnanti).filter_by(codTessera=cod).first() != None:
                        print("COD ACCETTATO")
                        s.send(b"OP1\n")
                    else:
                        print("COD NON RICONOSCIUTO")
                        file_object = open('../NONTOCCARE/cod_nuovo_tornello.txt', 'w+')
                        file_object.write(str(cod))
                        file_object.close()
            except Exception as e:
                with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
                    file_object.write(str(e) + "\n")
                break
        with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
            file_object.write("CLOSE SOCKET \n")
        try:
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except Exception as e:
            with open("../NONTOCCARE/log_tornello.txt", "a+") as file_object:
                file_object.write(str(e) + "\n")



