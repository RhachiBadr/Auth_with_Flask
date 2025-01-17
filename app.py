from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer 
from flask import session

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
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)  # Token valide 1 heure

        user = User.query.filter_by(email=email).first()
        if user:
            if not user.verified:
                user.verified = True  # Marq user as virified
                db.session.commit()

            session['user_id'] = user.id  
            flash('Votre adresse e-mail a été vérifiée avec succès. Vous êtes maintenant connecté.')
            return redirect(url_for('dashboard'))
        else:
            flash('Utilisateur non trouvé.')
    except Exception as e:
        flash('Le lien de vérification est invalide ou a expiré.')
        print(f"Erreur : {e}")

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
                session['user_id'] = user.id
                flash('Connexion réussie !')
                return redirect(url_for('dashboard'))
            else:
                flash('Veuillez vérifier votre e-mail avant de vous connecter.')
        else:
            flash('E-mail ou mot de passe incorrect.')
        return redirect(url_for('index'))
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.')
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    flash('Vous êtes déconnecté.')
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run(debug=True)