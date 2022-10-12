from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectMultipleField,TextAreaField,SelectField,FieldList,FormField,IntegerField,FloatField
from wtforms.validators import DataRequired
from app import db
from app.models import Corsi,Insegnanti,Sale,Soci

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Avvia')

class addSociForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    cognome = StringField('Cognome', validators=[DataRequired()])
    dataNascita = StringField('Data',validators=[DataRequired()])
    comuneNascita = StringField('comuneNascita', validators=[DataRequired()])
    comuneResidenza = StringField('comuneResidenza', validators=[DataRequired()])
    viaResidenza = StringField('viaResidenza', validators=[DataRequired()])
    codicePostale = StringField('codicePostale', validators=[DataRequired()])
    codiceFiscale = StringField('codiceFiscale', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    cellulare = StringField('cellulare', validators=[DataRequired()])
    noteExtra = TextAreaField('noteExtra')
    certificatoMedico = BooleanField('certificatoMedico')
    codiceTessera = StringField('cod')   
    corsi = SelectMultipleField('corsi', validators=[DataRequired()],coerce=int)
    submit = SubmitField('Iscrivi')

    def __init__(self, *args, **kwargs):
        super(addSociForm, self).__init__(*args, **kwargs)
        self.corsi.choices = [("123","Seleziona Corsi")]
        for x in Corsi.query.all():
            self.corsi.choices.append((x.id,x.nome))
    

class pagamento(FlaskForm):
    corso = SelectField('corsi',coerce=int)
    metodoPagamento = SelectField('corsi',coerce=int)
    euro = StringField('corsi', validators=[DataRequired()])
    def __init__(self, *args, **kwargs):
        super(pagamento, self).__init__(*args, **kwargs)
        self.corso.choices = [("123","Seleziona Corsi")]
        for x in Corsi.query.all():
            self.corso.choices.append((x.id,x.nome))
        self.metodoPagamento.choices = [("123","Seleziona Metodo"),("1","Percentuale"),("2","Tariffa Oraria")]

class addInsegnantiForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    cognome = StringField('Cognome', validators=[DataRequired()])
    dataNascita = StringField('Data',validators=[DataRequired()])
    comuneNascita = StringField('comuneNascita', validators=[DataRequired()])
    comuneResidenza = StringField('comuneResidenza', validators=[DataRequired()])
    viaResidenza = StringField('viaResidenza', validators=[DataRequired()])
    codicePostale = StringField('codicePostale', validators=[DataRequired()])
    codiceFiscale = StringField('codiceFiscale', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    cellulare = StringField('cellulare', validators=[DataRequired()])
    noteExtra = TextAreaField('noteExtra')
    codiceTessera = StringField('cod')
    submit = SubmitField('CREA')
    def __init__(self, *args, **kwargs):
        super(addInsegnantiForm, self).__init__(*args, **kwargs)


class addSalaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    noteExtra = TextAreaField('noteExtra')
    submit = SubmitField('Crea')

class addExtraForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    euro = FloatField('Euro', validators=[DataRequired()])
    noteExtra = TextAreaField('noteExtra')
    submit = SubmitField('Crea')

class preRicevutaForm(FlaskForm):
    soci = SelectMultipleField('Soci', validators=[DataRequired()],coerce=int)  
    submit = SubmitField('CREA')

    def __init__(self, *args, **kwargs):
        super(preRicevutaForm, self).__init__(*args, **kwargs)
        self.soci.choices = [("123","Seleziona Soci")]
        for x in Soci.query.all():
            self.soci.choices.append((x.id,x.nome + " " + x.cognome))

class addUscitaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    euro = FloatField('Euro', validators=[DataRequired()])
    metodoPagamento = SelectField('corsi',coerce=int)
    submit = SubmitField('Crea')
    def __init__(self, *args, **kwargs):
            super(addUscitaForm, self).__init__(*args, **kwargs)
            self.metodoPagamento.choices = [("123","Seleziona Metodo Pagamento"),("1","Contanti"),("2","Bonifico"),("3","Assegno")]
            
class stipendioForm(FlaskForm):
    ins = SelectField('Ins', validators=[DataRequired()],coerce=int)  
    submit = SubmitField('Crea')

    def __init__(self, *args, **kwargs):
        super(stipendioForm, self).__init__(*args, **kwargs)
        self.ins.choices = [("123","Seleziona Insegnanti")]
        for x in Insegnanti.query.all():
            self.ins.choices.append((x.id,x.nome + " " + x.cognome))