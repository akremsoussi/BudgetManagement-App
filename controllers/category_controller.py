from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
import data_model as model
from functools import wraps

category_bp = Blueprint('category', __name__, url_prefix='/categories')

# Décorateur pour vérifier si l'utilisateur est connecté
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Vous devez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@category_bp.route('/')
@login_required
def manage_categories():
    user_id = session['user_id']
    
    # Récupérer les catégories
    categories = model.get_categories(user_id)
    
    return render_template('categories/manage.html', categories=categories)

@category_bp.route('/add', methods=['POST'])
@login_required
def add_category():
    user_id = session['user_id']
    name = request.form['name']
    
    if not name:
        flash('Le nom de la catégorie est requis.', 'danger')
        return redirect(url_for('category.manage_categories'))
    
    try:
        category_id = model.create_category(name, user_id)
        flash('Catégorie ajoutée avec succès!', 'success')
    except Exception as e:
        flash(f"Erreur lors de l'ajout de la catégorie: {e}", 'danger')
    
    return redirect(url_for('category.manage_categories'))

@category_bp.route('/edit/<int:category_id>', methods=['POST'])
@login_required
def edit_category(category_id):
    user_id = session['user_id']
    name = request.form['name']
    
    if not name:
        flash('Le nom de la catégorie est requis.', 'danger')
        return redirect(url_for('category.manage_categories'))
    
    try:
        success = model.update_category(category_id, name, user_id)
        if success:
            flash('Catégorie mise à jour avec succès!', 'success')
        else:
            flash('Erreur lors de la mise à jour de la catégorie.', 'danger')
    except Exception as e:
        flash(f"Erreur lors de la mise à jour de la catégorie: {e}", 'danger')
    
    return redirect(url_for('category.manage_categories'))

@category_bp.route('/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    user_id = session['user_id']
    
    try:
        success = model.delete_category(category_id, user_id)
        if success:
            flash('Catégorie supprimée avec succès!', 'success')
        else:
            flash('Erreur lors de la suppression de la catégorie.', 'danger')
    except Exception as e:
        flash(f"Erreur lors de la suppression de la catégorie: {e}", 'danger')
    
    return redirect(url_for('category.manage_categories'))

@category_bp.route('/api/list', methods=['GET'])
@login_required
def api_list_categories():
    user_id = session['user_id']
    categories = model.get_categories(user_id)
    return jsonify(categories)