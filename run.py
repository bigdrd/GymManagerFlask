from app import app,db
from app.models import Gestori,Soci,Corsi,CorsiPerSocio,Ricevute,MensilePagati,Extra,ExtraPagati,Incassi,InsegnatiPerCorso,EventiPerSocio,Insegnanti,Stipendi,Uscite
import os 
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Gestori': Gestori, 'Corsi':Corsi,'CorsiPerSocio':CorsiPerSocio,'Ricevute':Ricevute,"Insegnanti":Insegnanti,'Soci':Soci,'MensilePagati':MensilePagati,'Extra':Extra,'ExtraPagati':ExtraPagati,"Incassi":Incassi,"IPC":InsegnatiPerCorso,"EventiPerSocio":EventiPerSocio,"Stipendi":Stipendi,"Uscite":Uscite}


if __name__ == "__main__":
    app.run(host="0.0.0.0",port="5000",debug=True)


#resoconto giornaliero staccare entrate uscite
#assegnare ricevute al socio per poterle vedere dal suo profilo e poterle eliminare
#decidere di che mese fare il resoconto
#sistemare Extra, sulla ricevuta
#risolvere problema corrente

#sistemare orario del db
