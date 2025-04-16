from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import data_model as model

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        error = None
        
        if not name:
            error = 'Le nom est requis.'
        elif not email:
            error = 'L\'email est requis.'
        elif not password:
            error = 'Le mot de passe est requis.'
        elif password != confirm_password:
            error = 'Les mots de passe ne correspondent pas.'
            
        if error is None:
            try:
                user_id = model.create_user(name, email, password)
                if user_id != -1:
                    # Créer des catégories par défaut pour le nouvel utilisateur
                    default_categories = ['Alimentation', 'Logement', 'Transport', 'Loisirs', 'Santé', 'Éducation']
                    for category in default_categories:
                        model.create_category(category, user_id)
                    
                    flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    error = 'L\'email ou le nom d\'utilisateur existe déjà.'
            except Exception as e:
                error = f"Erreur lors de l'inscription: {e}"
                
        flash(error, 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        error = None
        
        if not email:
            error = 'L\'email est requis.'
        elif not password:
            error = 'Le mot de passe est requis.'
            
        if error is None:
            user_id = model.login(email, password)
            if user_id != -1:
                session.clear()
                session['user_id'] = user_id
                flash('Connexion réussie !', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Email ou mot de passe incorrect.'
                
        flash(error, 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))