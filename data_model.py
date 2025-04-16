import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

DBFILENAME = 'budget_app.db'

# ============ Utility Database Functions ============

def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    """Execute a query and fetch results, returning them as dictionaries"""
    with sqlite3.connect(db_name) as conn:
        # Allow access to columns by name
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        # Convert to a python dictionary for convenience
        if all:
            res = cur.fetchall()
            if res:
                res = [dict(e) for e in res]
            else:
                res = []
        else:
            res = cur.fetchone()
            if res:
                res = dict(res)
    return res

def db_insert(query, args=(), db_name=DBFILENAME):
    """Execute an insertion query and return the last inserted row ID"""
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid

def db_run(query, args=(), db_name=DBFILENAME):
    """Execute a query without expecting a return value"""
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()

def db_update(query, args=(), db_name=DBFILENAME):
    """Execute an update query and return the number of affected rows"""
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.rowcount

# ============ User Functions ============

def login(email, password):
    """Authenticate a user and return user_id or -1 if authentication fails"""
    user = db_fetch('SELECT id, password_hash FROM users WHERE email = ?', (email,))
    if user and check_password_hash(user['password_hash'], password):
        return user['id']
    return -1

def create_user(name, email, password):
    """Create a new user and return the user_id"""
    password_hash = generate_password_hash(password)
    try:
        return db_insert('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', 
                        (name, email, password_hash))
    except sqlite3.IntegrityError:
        # Email or name already exists
        return -1

def get_user(user_id):
    """Get user information by ID"""
    return db_fetch('SELECT id, name, email FROM users WHERE id = ?', (user_id,))

def update_user(user_id, name=None, email=None, password=None):
    """Update user information"""
    updates = []
    params = []
    
    if name:
        updates.append("name = ?")
        params.append(name)
    if email:
        updates.append("email = ?")
        params.append(email)
    if password:
        updates.append("password_hash = ?")
        params.append(generate_password_hash(password))
        
    if not updates:
        return False
        
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    params.append(user_id)
    
    try:
        rows_updated = db_update(query, params)
        return rows_updated > 0
    except sqlite3.IntegrityError:
        return False

# ============ Category Functions ============

def create_category(name, user_id):
    """Create a new expense category and return the category_id"""
    return db_insert('INSERT INTO categories (name, user_id) VALUES (?, ?)', 
                    (name, user_id))

def get_categories(user_id):
    """Get all categories for a user"""
    return db_fetch('SELECT id, name FROM categories WHERE user_id = ? ORDER BY name', 
                    (user_id,), all=True)

def get_category(category_id, user_id):
    """Get a specific category"""
    return db_fetch('SELECT id, name FROM categories WHERE id = ? AND user_id = ?', 
                    (category_id, user_id))

def update_category(category_id, name, user_id):
    """Update a category name"""
    rows_updated = db_update('UPDATE categories SET name = ? WHERE id = ? AND user_id = ?', 
                            (name, category_id, user_id))
    return rows_updated > 0

def delete_category(category_id, user_id):
    """Delete a category and update related expenses"""
    # Set category_id to NULL for related expenses
    db_run('UPDATE expenses SET category_id = NULL WHERE category_id = ? AND user_id = ?', 
           (category_id, user_id))
    
    # Delete the category
    rows_deleted = db_update('DELETE FROM categories WHERE id = ? AND user_id = ?', 
                            (category_id, user_id))
    return rows_deleted > 0

# ============ Expense Functions ============

def add_expense(title, amount, date, category_id, user_id):
    """Add a new expense and return the expense_id"""
    return db_insert(
        'INSERT INTO expenses (title, amount, date, category_id, user_id) VALUES (?, ?, ?, ?, ?)', 
        (title, amount, date, category_id, user_id))

def get_expenses(user_id, start_date=None, end_date=None, category_id=None):
    """Get expenses for a user with optional filters"""
    query = '''
        SELECT e.id, e.title, e.amount, e.date, e.category_id, 
               c.name as category_name
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ?
    '''
    params = [user_id]
    
    if start_date:
        query += " AND e.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND e.date <= ?"
        params.append(end_date)
    if category_id:
        query += " AND e.category_id = ?"
        params.append(category_id)
        
    query += " ORDER BY e.date DESC"
    
    return db_fetch(query, params, all=True)

def get_expense(expense_id, user_id):
    """Get a specific expense by ID"""
    return db_fetch('''
        SELECT e.id, e.title, e.amount, e.date, e.category_id, 
               c.name as category_name
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE e.id = ? AND e.user_id = ?
    ''', (expense_id, user_id))

def update_expense(expense_id, title, amount, date, category_id, user_id):
    """Update an expense"""
    rows_updated = db_update('''
        UPDATE expenses 
        SET title = ?, amount = ?, date = ?, category_id = ?
        WHERE id = ? AND user_id = ?
    ''', (title, amount, date, category_id, expense_id, user_id))
    return rows_updated > 0

def delete_expense(expense_id, user_id):
    """Delete an expense"""
    rows_deleted = db_update('DELETE FROM expenses WHERE id = ? AND user_id = ?', 
                            (expense_id, user_id))
    return rows_deleted > 0

def get_expense_summary_by_category(user_id, month=None):
    """Get expense summary grouped by category"""
    query = '''
        SELECT c.name as category_name, COALESCE(c.id, 0) as category_id, 
               SUM(e.amount) as total_amount, 
               COUNT(e.id) as transaction_count
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ?
    '''
    params = [user_id]
    
    if month:
        query += " AND substr(e.date, 1, 7) = ?"
        params.append(month)  # Format should be 'YYYY-MM'
        
    query += '''
        GROUP BY c.id
        ORDER BY total_amount DESC
    '''
    
    return db_fetch(query, params, all=True)

def get_monthly_expense_totals(user_id, year=None):
    """Get monthly expense totals"""
    query = '''
        SELECT substr(date, 1, 7) as month, 
               SUM(amount) as total_amount,
               COUNT(id) as transaction_count
        FROM expenses
        WHERE user_id = ?
    '''
    params = [user_id]
    
    if year:
        query += " AND substr(date, 1, 4) = ?"
        params.append(str(year))
        
    query += '''
        GROUP BY substr(date, 1, 7)
        ORDER BY month DESC
    '''
    
    return db_fetch(query, params, all=True)

# ============ Budget Functions ============

def ensure_budget_items_table():
    """Ensure the budget_items table exists"""
    db_run('''
        CREATE TABLE IF NOT EXISTS budget_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(budget_id) REFERENCES budgets(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')

def create_or_update_budget(month, user_id, category_allocations):
    """Create or update a budget with category allocations
    
    Args:
        month: Format 'YYYY-MM'
        user_id: User ID
        category_allocations: Dictionary of {category_id: amount}
    
    Returns:
        budget_id
    """
    ensure_budget_items_table()
    
    # Check if budget exists for this month
    budget = db_fetch('''
        SELECT id FROM budgets 
        WHERE month = ? AND user_id = ?
    ''', (month, user_id))
    
    if budget:
        budget_id = budget['id']
        # Clear existing budget items to recreate them
        db_run('DELETE FROM budget_items WHERE budget_id = ?', (budget_id,))
    else:
        # Create new budget
        budget_id = db_insert('''
            INSERT INTO budgets (month, user_id) 
            VALUES (?, ?)
        ''', (month, user_id))
    
    # Insert budget items
    for category_id, amount in category_allocations.items():
        db_run('''
            INSERT INTO budget_items (budget_id, category_id, amount) 
            VALUES (?, ?, ?)
        ''', (budget_id, category_id, amount))
    
    return budget_id

def get_budget(month, user_id):
    """Get a budget with its category allocations and spending data"""
    ensure_budget_items_table()
    
    # Check if budget exists
    budget = db_fetch('''
        SELECT id FROM budgets 
        WHERE month = ? AND user_id = ?
    ''', (month, user_id))
    
    if not budget:
        return None
        
    budget_id = budget['id']
    
    # Get budget items
    items = db_fetch('''
        SELECT bi.category_id, c.name as category_name, bi.amount as allocated_amount
        FROM budget_items bi
        JOIN categories c ON bi.category_id = c.id
        WHERE bi.budget_id = ?
    ''', (budget_id,), all=True)
    
    # Get actual spending for comparison
    actual_spending = get_expense_summary_by_category(user_id, month)
    
    # Create a dictionary for easy lookup
    spending_by_category = {item['category_id']: item for item in actual_spending}
    
    # Add actual spending to budget items
    for item in items:
        category_id = item['category_id']
        if category_id in spending_by_category:
            item['actual_amount'] = spending_by_category[category_id]['total_amount']
            item['remaining'] = item['allocated_amount'] - item['actual_amount']
        else:
            item['actual_amount'] = 0
            item['remaining'] = item['allocated_amount']
    
    return {
        'budget_id': budget_id,
        'month': month,
        'items': items
    }

def delete_budget(month, user_id):
    """Delete a budget"""
    ensure_budget_items_table()
    
    # Get the budget id
    budget = db_fetch('''
        SELECT id FROM budgets 
        WHERE month = ? AND user_id = ?
    ''', (month, user_id))
    
    if not budget:
        return False
        
    budget_id = budget['id']
    
    # Delete budget items first
    db_run('DELETE FROM budget_items WHERE budget_id = ?', (budget_id,))
    
    # Then delete the budget
    db_run('DELETE FROM budgets WHERE id = ?', (budget_id,))
    
    return True

def get_all_budgets(user_id):
    """Get all budgets for a user with summary information"""
    ensure_budget_items_table()
    
    budgets = db_fetch('''
        SELECT id, month FROM budgets 
        WHERE user_id = ?
        ORDER BY month DESC
    ''', (user_id,), all=True)
    
    for budget in budgets:
        budget_id = budget['id']
        budget_month = budget['month']
        
        # Get total allocated
        allocation = db_fetch('''
            SELECT SUM(amount) as total_allocated
            FROM budget_items
            WHERE budget_id = ?
        ''', (budget_id,))
        
        budget['total_allocated'] = allocation['total_allocated'] if allocation and allocation['total_allocated'] else 0
        
        # Get total spent
        actual_spending = get_expense_summary_by_category(user_id, budget_month)
        total_spent = sum(item['total_amount'] for item in actual_spending) if actual_spending else 0
        budget['total_spent'] = total_spent
    
    return budgets