from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
import data_model as model
from functools import wraps
from datetime import datetime

budget_bp = Blueprint('budget', __name__, url_prefix='/budgets')

# Décorateur pour vérifier si l'utilisateur est connecté
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Vous devez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@budget_bp.route('/')
@login_required
def list_budgets():
    user_id = session['user_id']
    
    # Récupérer tous les budgets
    budgets = model.get_all_budgets(user_id)
    
    return render_template('budgets/list.html', budgets=budgets)

@budget_bp.route('/edit/<string:month>', methods=['GET', 'POST'])
@login_required
def edit_budget(month):
    user_id = session['user_id']
    
    # Récupérer les catégories
    categories = model.get_categories(user_id)
    
    # Récupérer le budget s'il existe
    budget = model.get_budget(month, user_id)
    
    if request.method == 'POST':
        category_allocations = {}
        
        for category in categories:
            amount_str = request.form.get(f"category_{category['id']}")
            if amount_str:
                try:
                    amount = float(amount_str)
                    if amount > 0:
                        category_allocations[category['id']] = amount
                except ValueError:
                    pass
        
        if not category_allocations:
            flash('Veuillez saisir au moins une allocation de budget.', 'danger')
        else:
            try:
                budget_id = model.create_or_update_budget(month, user_id, category_allocations)
                flash(f"Budget pour {month} créé/mis à jour avec succès!", 'success')
                return redirect(url_for('budget.list_budgets'))
            except Exception as e:
                flash(f"Erreur lors de la création/mise à jour du budget: {e}", 'danger')
    
    return render_template('budgets/edit.html', 
                          categories=categories,
                          budget=budget,
                          month=month)

@budget_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_budget():
    if request.method == 'POST':
        month = request.form['month']
        
        if not month:
            flash('Veuillez sélectionner un mois.', 'danger')
            return redirect(url_for('budget.create_budget'))
        
        return redirect(url_for('budget.edit_budget', month=month))
    
    # Générer une liste des mois à venir
    months = []
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    
    for i in range(12):
        month_num = (current_month + i - 1) % 12 + 1
        year = current_year + (current_month + i - 1) // 12
        month_str = f"{year}-{month_num:02d}"
        month_name = datetime(year, month_num, 1).strftime('%B %Y')
        months.append({'value': month_str, 'name': month_name})
    
    return render_template('budgets/create.html', months=months)

    


@budget_bp.route('/delete/<string:month>', methods=['POST'])
@login_required
def delete_budget(month):
    user_id = session['user_id']
    
    try:
        success = model.delete_budget(month, user_id)
        if success:
            flash(f"Budget pour {month} supprimé avec succès!", 'success')
        else:
            flash(f"Erreur lors de la suppression du budget pour {month}.", 'danger')
    except Exception as e:
        flash(f"Erreur lors de la suppression du budget: {e}", 'danger')
    
    return redirect(url_for('budget.list_budgets'))






@budget_bp.route('/api/details/<string:month>', methods=['GET'])
@login_required
def api_budget_details(month):
    user_id = session['user_id']
    budget = model.get_budget(month, user_id)
    
    if budget:
        return jsonify(budget)
    else:
        return jsonify({'error': 'Budget not found'}), 404