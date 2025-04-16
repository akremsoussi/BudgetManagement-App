from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
import data_model as model
from functools import wraps
from datetime import datetime

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

# Décorateur pour vérifier si l'utilisateur est connecté
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Vous devez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@expense_bp.route('/')
@login_required
def list_expenses():
    user_id = session['user_id']
    
    # Récupérer les paramètres de filtrage
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    if category_id:
        try:
            category_id = int(category_id)
        except ValueError:
            category_id = None
    
    # Récupérer les dépenses
    expenses = model.get_expenses(user_id, start_date, end_date, category_id)
    
    # Récupérer les catégories pour le filtre
    categories = model.get_categories(user_id)
    
    # Calculer le total des dépenses affichées
    total_amount = sum(expense['amount'] for expense in expenses) if expenses else 0
    
    return render_template('expenses/list.html', 
                          expenses=expenses, 
                          categories=categories,
                          start_date=start_date,
                          end_date=end_date,
                          selected_category=category_id,
                          total_amount=total_amount)

@expense_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    user_id = session['user_id']
    
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        date = request.form['date']
        category_id = request.form['category_id'] if request.form['category_id'] else None
        
        error = None
        
        if not title:
            error = 'Le titre est requis.'
        elif not amount:
            error = 'Le montant est requis.'
        elif not date:
            error = 'La date est requise.'
            
        try:
            amount = float(amount)
            if amount <= 0:
                error = 'Le montant doit être positif.'
        except ValueError:
            error = 'Le montant doit être un nombre.'
            
        if error is None:
            try:
                expense_id = model.add_expense(title, amount, date, category_id, user_id)
                flash('Dépense ajoutée avec succès!', 'success')
                return redirect(url_for('expense.list_expenses'))
            except Exception as e:
                error = f"Erreur lors de l'ajout de la dépense: {e}"
                
        flash(error, 'danger')
    
    # Récupérer les catégories pour le formulaire
    categories = model.get_categories(user_id)
    
    # Date du jour par défaut
    default_date = datetime.today().strftime('%Y-%m-%d')
    
    return render_template('expenses/add.html', 
                          categories=categories,
                          expense=None,
                          default_date=default_date)

@expense_bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    user_id = session['user_id']
    
    # Récupérer la dépense
    expense = model.get_expense(expense_id, user_id)
    if not expense:
        flash('Dépense introuvable.', 'danger')
        return redirect(url_for('expense.list_expenses'))
    
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        date = request.form['date']
        category_id = request.form['category_id'] if request.form['category_id'] else None
        
        error = None
        
        if not title:
            error = 'Le titre est requis.'
        elif not amount:
            error = 'Le montant est requis.'
        elif not date:
            error = 'La date est requise.'
            
        try:
            amount = float(amount)
            if amount <= 0:
                error = 'Le montant doit être positif.'
        except ValueError:
            error = 'Le montant doit être un nombre.'
            
        if error is None:
            try:
                success = model.update_expense(expense_id, title, amount, date, category_id, user_id)
                if success:
                    flash('Dépense mise à jour avec succès!', 'success')
                    return redirect(url_for('expense.list_expenses'))
                else:
                    error = 'Erreur lors de la mise à jour de la dépense.'
            except Exception as e:
                error = f"Erreur lors de la mise à jour de la dépense: {e}"
                
        flash(error, 'danger')
    
    # Récupérer les catégories pour le formulaire
    categories = model.get_categories(user_id)
    
    return render_template('expenses/add.html', 
                          categories=categories,
                          expense=expense)

@expense_bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    user_id = session['user_id']
    
    success = model.delete_expense(expense_id, user_id)
    if success:
        flash('Dépense supprimée avec succès!', 'success')
    else:
        flash('Erreur lors de la suppression de la dépense.', 'danger')
        
    return redirect(url_for('expense.list_expenses'))