#!/usr/bin/env python3
"""
Local testing version of the Cashabl Flask Application
This version uses local PostgreSQL for testing without AWS
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import psycopg2
from psycopg2 import sql
import os
from datetime import datetime
import uuid
import sqlite3

app = Flask(__name__)
app.secret_key = 'test-secret-key'

class LocalDatabaseManager:
    def __init__(self):
        self.db_path = 'cashabl_local.db'
        
    def get_db_connection(self):
        """Get SQLite connection for local testing"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize SQLite database tables"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Create transactions table (SQLite version)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    transaction_id TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Local SQLite database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")

db_manager = LocalDatabaseManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transfer', methods=['POST'])
def transfer_cash():
    """Handle cash transfer request"""
    try:
        amount = float(request.form.get('amount'))
        transaction_id = request.form.get('transaction_id')
        
        if not transaction_id:
            transaction_id = str(uuid.uuid4())[:8].upper()
        
        if amount <= 0:
            flash('Amount must be greater than 0', 'error')
            return redirect(url_for('index'))
        
        # Insert into database
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transactions (id, transaction_id, amount, status)
            VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), transaction_id, amount, 'deposited'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Successfully deposited ${amount:.2f} with ID: {transaction_id}', 'success')
        return redirect(url_for('index'))
        
    except ValueError:
        flash('Invalid amount entered', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error processing transfer: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/withdraw', methods=['POST'])
def withdraw_cash():
    """Handle cash withdrawal request"""
    try:
        transaction_id = request.form.get('withdraw_id')
        
        if not transaction_id:
            flash('Transaction ID is required', 'error')
            return redirect(url_for('index'))
        
        # Search and withdraw from database
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        
        # Check if transaction exists and is not already withdrawn
        cursor.execute("""
            SELECT amount, status FROM transactions 
            WHERE transaction_id = ?
        """, (transaction_id,))
        
        result = cursor.fetchone()
        
        if not result:
            flash('Transaction ID not found', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        
        amount, status = result['amount'], result['status']
        
        if status == 'withdrawn':
            flash('This transaction has already been withdrawn', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        
        # Update status to withdrawn
        cursor.execute("""
            UPDATE transactions 
            SET status = 'withdrawn', updated_at = CURRENT_TIMESTAMP
            WHERE transaction_id = ?
        """, (transaction_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Successfully withdrew ${amount:.2f} for transaction ID: {transaction_id}', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error processing withdrawal: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/transactions')
def view_transactions():
    """View all transactions"""
    try:
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT transaction_id, amount, status, created_at, updated_at
            FROM transactions
            ORDER BY created_at DESC
        """)
        
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to list of tuples for template compatibility
        transactions_list = []
        for row in transactions:
            transactions_list.append((
                row['transaction_id'], 
                row['amount'], 
                row['status'], 
                row['created_at'], 
                row['updated_at']
            ))
        
        return render_template('transactions.html', transactions=transactions_list)
        
    except Exception as e:
        flash(f'Error fetching transactions: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize database on startup
    db_manager.init_db()
    print("🚀 Starting Cashabl Flask Application (Local Testing Mode)")
    print("📊 Using SQLite database for local testing")
    print("🌐 Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
