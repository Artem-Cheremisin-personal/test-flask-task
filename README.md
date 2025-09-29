# Cashabl Flask Application

A dummy Flask application that mimics payabl.com style, designed to demonstrate cash transfer functionality with AWS Aurora PostgreSQL integration.

## Features

- **Cash Transfer**: Enter amount and ID to deposit cash into the database
- **Cash Withdrawal**: Search by transaction ID and withdraw funds
- **Transaction History**: View all transactions with status tracking
- **AWS Integration**: Uses boto3 to connect to Aurora PostgreSQL
- **Modern UI**: Responsive design inspired by payabl.com

## Prerequisites

- Python 3.8+
- AWS Account with RDS Aurora PostgreSQL cluster
- PostgreSQL (for local testing)

## Installation

1. **Clone or create the project directory:**
   ```bash
   cd /home/artem/payabl_flask_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your actual AWS and database credentials.

## AWS Aurora PostgreSQL Setup

### 1. Create Aurora PostgreSQL Cluster

```bash
# Create Aurora cluster
aws rds create-db-cluster \
    --db-cluster-identifier cashabl-cluster \
    --engine aurora-postgresql \
    --master-username postgres \
    --master-user-password YourSecurePassword \
    --database-name cashabl_db \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name your-subnet-group

# Create cluster instance
aws rds create-db-instance \
    --db-instance-identifier cashabl-cluster-instance-1 \
    --db-instance-class db.r5.large \
    --engine aurora-postgresql \
    --db-cluster-identifier cashabl-cluster
```

### 2. Configure IAM for RDS Authentication

Create an IAM policy for RDS access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rds-db:connect"
            ],
            "Resource": [
                "arn:aws:rds-db:us-east-1:123456789012:dbuser:cluster-id/postgres"
            ]
        }
    ]
}
```

### 3. Enable IAM Database Authentication

```bash
aws rds modify-db-cluster \
    --db-cluster-identifier payabl-cluster \
    --enable-iam-database-authentication \
    --apply-immediately
```

## Environment Variables

Update your `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# RDS Configuration  
RDS_CLUSTER_IDENTIFIER=cashabl-cluster
DB_NAME=cashabl_db
DB_USERNAME=postgres

# Flask Configuration
SECRET_KEY=your-super-secret-key-here
```

## Database Schema

The application automatically creates the following table:

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Running the Application

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

### Using Docker

```bash
# Build the image
docker build -t cashabl-app .

# Run the container
docker run -p 5000:5000 --env-file .env cashabl-app
```

## Usage

### 1. Transfer Cash
- Enter amount to transfer
- Optionally provide a transaction ID (auto-generated if not provided)
- Click "Transfer Money"

### 2. Withdraw Cash  
- Enter the transaction ID
- Click "Withdraw Cash"
- The system will search for the transaction and mark it as withdrawn

### 3. View Transactions
- Click "View All Transactions" to see transaction history
- View status, amounts, and timestamps

## API Endpoints

- `GET /` - Main application page
- `POST /transfer` - Process cash transfer
- `POST /withdraw` - Process cash withdrawal  
- `GET /transactions` - View transaction history

## Security Features

- AWS IAM authentication for database access
- Input validation and sanitization
- SQL injection protection with parameterized queries
- CSRF protection with Flask secret key
- SSL/TLS connections to RDS

## Troubleshooting

### Database Connection Issues

1. **Check AWS credentials:**
   ```bash
   aws sts get-caller-identity
   ```

2. **Test RDS connectivity:**
   ```bash
   psql -h your-cluster.cluster-xxx.us-east-1.rds.amazonaws.com -p 5432 -U postgres -d payabl_db
   ```

3. **Verify security groups:** Ensure port 5432 is open from your application

### Common Errors

- **Connection timeout**: Check VPC, subnets, and security groups
- **Authentication failed**: Verify IAM policies and RDS IAM auth is enabled  
- **Table doesn't exist**: The app auto-creates tables on startup

## Deployment

### AWS ECS/Fargate

1. Push Docker image to ECR
2. Create ECS task definition
3. Deploy to Fargate cluster
4. Configure load balancer and security groups

### AWS Elastic Beanstalk

1. Create application zip file
2. Deploy to Elastic Beanstalk
3. Configure environment variables
4. Set up RDS connection

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is for demonstration purposes only.
