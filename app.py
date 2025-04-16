from flask import Flask, render_template, redirect, url_for, session, flash, g
import os
from functools import wraps
from controllers.auth_controller import auth_bp
from controllers.expense_controller import expense_bp
from controllers.category_controller import category_bp
from controllers.budget_controller import budget_bp
import data_model as model


app = Flask(__name__)


app.secret_key = os.urandom(24)

# Enregistrement des blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(category_bp)
app.register_blueprint(budget_bp)

# Middleware pour vérifier si l'utilisateur est connecté
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = model.get_user(user_id)

# Décorateur pour les routes qui nécessitent une authentification
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Vous devez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

# Route principale - Tableau de bord
@app.route('/')
@login_required
def dashboard():
    # Récupérer les données pour le tableau de bord
    user_id = session['user_id']
    
    # Récupérer les dépenses récentes
    recent_expenses = model.get_expenses(user_id, None, None, None)
    if recent_expenses:
        recent_expenses = recent_expenses[:5]  # Limiter à 5 dépenses
        
    # Récupérer les totaux mensuels
    monthly_totals = model.get_monthly_expense_totals(user_id)
    
    # Récupérer le résumé par catégorie pour le mois en cours
    current_month = model.datetime.date.today().strftime('%Y-%m')
    category_summary = model.get_expense_summary_by_category(user_id, current_month)
    
    # Récupérer le budget pour le mois en cours
    current_budget = model.get_budget(current_month, user_id)

    if current_budget:
        total_allocated = sum(item['allocated_amount'] for item in current_budget['items'])
        total_spent = sum(item.get('actual_amount', 0) for item in current_budget['items'])
        
        current_budget['total_allocated'] = total_allocated
        current_budget['total_spent'] = total_spent
    
    return render_template('dashboard.html', 
                          recent_expenses=recent_expenses,
                          monthly_totals=monthly_totals,
                          category_summary=category_summary,
                          current_budget=current_budget,
                          current_month=current_month)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)