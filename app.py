from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer 
import yagmail 

app = Flask(__name__)

# Config Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '4f5d6e7a8b9c0d1e2f3a4b5c6d7e8f9a'  

# extension SQLAlchemy
db = SQLAlchemy(app)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    verified = db.Column(db.Boolean, default=False)  

# Crée bd
with app.app_context():
    db.create_all()

def send_verification_email(email, username):
    
    token = serializer.dumps(email, salt='email-verification')

    verification_link = f"http://localhost:5000/verify/{token}"

    sender_email = 'badrgloo@yahoo.com'
    sender_password = 'ghfdsimxdijbxhgq'  

    yag = yagmail.SMTP(sender_email, sender_password, host='smtp.mail.yahoo.com', port=465)

    subject = 'Vérifiez votre adresse e-mail'
    body = f'''
    Bonjour {username},

    Merci de vous être inscrit sur notre plateforme.
    Veuillez cliquer sur le lien suivant pour vérifier votre adresse e-mail :

    {verification_link}

    Cordialement,
    L'équipe de support
    '''
    
    try:
        yag.send(to=email, subject=subject, contents=body)
        print(f"E-mail envoyé avec succès à {email}.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

# la pag accueil
@app.route('/')
def index():
    return render_template('login.html')

# l'inscription
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Vérif si user exist déja
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Cet e-mail est déjà utilisé.')
            return redirect(url_for('index'))

        # Add user at bd
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # sending mail
        send_verification_email(email, username)

        flash('Inscription réussie ! Un e-mail de vérification a été envoyé.')
        return redirect(url_for('index'))

# RT verification
@app.route('/verify/<token>')
def verify(token):
    try:
        # Valider le token et récupérer l'e-mail
        email = serializer.loads(token, salt='email-verification', max_age=3600)  # Token valide pendant 1 heure

        # Trouver l'utilisateur associé à l'e-mail
        user = User.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            flash('Votre adresse e-mail a été vérifiée avec succès.')
        else:
            flash('Utilisateur non trouvé.')
    except Exception as e:
        flash('Le lien de vérification est invalide ou a expiré.')
        print(f"Erreur : {e}")

    # Rediriger vers la page d'accueil après vérification
    return redirect(url_for('index'))

# RT for connex
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Vérifier les informations de connexion
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            if user.verified:
                flash('Connexion réussie !')
            else:
                flash('Veuillez vérifier votre e-mail avant de vous connecter.')
        else:
            flash('E-mail ou mot de passe incorrect.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)