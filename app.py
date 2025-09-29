from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import boto3
import psycopg2
from psycopg2 import sql
import os
import json
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# AWS Configuration
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'eu-central-1')
DB_SECRET_ARN = os.environ.get('DB_SECRET_ARN')

class DatabaseManager:
    def __init__(self):
        self.secrets_client = boto3.client('secretsmanager', region_name=AWS_REGION)
        
    def get_database_connection_details(self):
        """Retrieve complete database connection details from AWS Secrets Manager"""
        if not DB_SECRET_ARN:
            raise ValueError("DB_SECRET_ARN environment variable not set")
        
        try:
            response = self.secrets_client.get_secret_value(SecretId=DB_SECRET_ARN)
            secret = json.loads(response['SecretString'])
            return secret
        except Exception as e:
            print(f"Error retrieving database connection secret: {e}")
            raise
        
    def get_db_connection(self):
        """Get database connection using complete connection details from secrets"""
        try:
            db_details = self.get_database_connection_details()
            
            # Connect to PostgreSQL using all details from secret
            connection = psycopg2.connect(
                host=db_details['host'],
                port=db_details['port'],
                database=db_details['dbname'],
                user=db_details['username'],
                password=db_details['password'],
                sslmode='require'
            )
            return connection
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            # Fallback to environment variables for local testing
            return psycopg2.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                port=os.environ.get('DB_PORT', '5432'),
                database=os.environ.get('DB_NAME', 'cashabl'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'password')
            )
    
    def init_db(self):
        """Initialize database tables"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    transaction_id VARCHAR(50) UNIQUE NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {str(e)}")

db_manager = DatabaseManager()

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
            INSERT INTO transactions (transaction_id, amount, status)
            VALUES (%s, %s, %s)
        """, (transaction_id, amount, 'deposited'))
        
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
            WHERE transaction_id = %s
        """, (transaction_id,))
        
        result = cursor.fetchone()
        
        if not result:
            flash('Transaction ID not found', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        
        amount, status = result
        
        if status == 'withdrawn':
            flash('This transaction has already been withdrawn', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        
        # Update status to withdrawn
        cursor.execute("""
            UPDATE transactions 
            SET status = 'withdrawn', updated_at = CURRENT_TIMESTAMP
            WHERE transaction_id = %s
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
        
        return render_template('transactions.html', transactions=transactions)
        
    except Exception as e:
        flash(f'Error fetching transactions: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize database on startup
    db_manager.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
