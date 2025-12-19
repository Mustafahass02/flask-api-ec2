# flask-api-ec2
# Flask Task Manager API on AWS EC2

## Overview
A RESTful API for task management deployed on AWS EC2, demonstrating cloud deployment, security configuration, and production-ready practices.

## Architecture
```
┌─────────┐
│  User   │
└────┬────┘
     │ HTTP Request (port 5000)
     │
     v
┌────────────────────────────────────┐
│   Security Group                   │
│   - SSH (22): Your IP only         │
│   - HTTP (5000): 0.0.0.0/0        │
│                                    │
│  ┌──────────────────────────────┐ │
│  │   EC2 Instance (t2.micro)    │ │
│  │   Ubuntu 22.04 LTS           │ │
│  │                              │ │
│  │   ┌────────────────────┐    │ │
│  │   │  Gunicorn          │    │ │
│  │   │  (WSGI Server)     │    │ │
│  │   │        ↓           │    │ │
│  │   │  Flask Application │    │ │
│  │   │  (Task Manager)    │    │ │
│  │   └────────────────────┘    │ │
│  │                              │ │
│  │   systemd manages process    │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘
```

## Technologies
- **Python 3.10** + Flask web framework
- **AWS EC2** (t2.micro, Ubuntu 22.04)
- **Gunicorn** (production WSGI server)
- **systemd** (process management)
- **RESTful API** design

## API Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/health` | Health check | None |
| GET | `/tasks` | List all tasks | None |
| POST | `/tasks` | Create new task | `{"title": "string", "description": "string"}` |
| GET | `/tasks/<id>` | Get specific task | None |
| PUT | `/tasks/<id>` | Update task | `{"title": "string", "description": "string", "completed": bool}` |
| DELETE | `/tasks/<id>` | Delete task | None |

## Setup Instructions

### Prerequisites
- AWS account with EC2 access
- SSH key pair for EC2 access
- Basic Linux/terminal knowledge

### 1. Launch EC2 Instance

**In AWS Console:**
1. Go to EC2 → Launch Instance
2. Choose Ubuntu Server 22.04 LTS (free tier)
3. Instance type: t2.micro
4. Create/select key pair (download .pem file)
5. Security group rules:
   - SSH (22): Your IP
   - Custom TCP (5000): 0.0.0.0/0
6. Launch instance

### 2. Connect to EC2
```bash
# Set key permissions
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@<PUBLIC_IP>
```

### 3. Deploy Application

**On EC2 instance:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git

# Clone repository
git clone https://github.com/YOUR_USERNAME/flask-api-ec2.git
cd flask-api-ec2

# Run deployment script
chmod +x deployment/setup.sh
./deployment/setup.sh

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Set Up Production Service

**Create systemd service:**
```bash
sudo nano /etc/systemd/system/flask-app.service
```

**Add:**
```ini
[Unit]
Description=Flask Task Manager API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/flask-api-ec2
Environment="PATH=/home/ubuntu/flask-api-ec2/venv/bin"
ExecStart=/home/ubuntu/flask-api-ec2/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app
sudo systemctl status flask-app
```

### 5. Test the API
```bash
# Health check
curl http://<PUBLIC_IP>:5000/health

# Create task
curl -X POST http://<PUBLIC_IP>:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn AWS","description":"Complete EC2 deployment"}'

# List tasks
curl http://<PUBLIC_IP>:5000/tasks

# Get specific task
curl http://<PUBLIC_IP>:5000/tasks/1

# Update task
curl -X PUT http://<PUBLIC_IP>:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Delete task
curl -X DELETE http://<PUBLIC_IP>:5000/tasks/1
```

## Security Considerations

### Implemented:
✅ Security group restricts SSH to your IP only  
✅ Application runs as non-root user (ubuntu)  
✅ systemd service with automatic restart on failure  
✅ Structured logging for monitoring  

### Production Improvements:
- [ ] Add HTTPS with SSL/TLS certificate (AWS Certificate Manager + Application Load Balancer)
- [ ] Implement authentication (JWT tokens or API keys)
- [ ] Use RDS/DynamoDB instead of in-memory storage
- [ ] Deploy in private subnet with bastion host
- [ ] Add rate limiting and request validation
- [ ] Enable CloudWatch logging and alarms
- [ ] Implement IAM role for AWS service access
- [ ] Add CORS headers for frontend integration

## Monitoring

**Check application logs:**
```bash
sudo journalctl -u flask-app -f
```

**Check service status:**
```bash
sudo systemctl status flask-app
```

**Restart service:**
```bash
sudo systemctl restart flask-app
```

## Cost Breakdown
- **EC2 t2.micro:** Free tier (750 hours/month for 12 months)
- **Data transfer:** Free tier (1GB/month outbound)
- **Elastic IP (if used):** $0 while attached, $0.005/hour if unattached
- **EBS storage:** Free tier (30GB for 12 months)

**Estimated monthly cost after free tier:** ~$8-10/month

## What I Learned

### Technical Skills:
- Deploying Python applications to cloud infrastructure
- Configuring EC2 security groups and network access
- Using systemd for service management
- Production deployment with Gunicorn
- RESTful API design patterns
- Linux server administration

### AWS Services:
- EC2 instance management
- Security group configuration
- SSH key pair authentication
- Elastic IP allocation (optional)

### Best Practices:
- Never run applications as root user
- Use virtual environments for dependency isolation
- Implement health check endpoints
- Structure logs for observability
- Document deployment procedures

## Challenges Faced

### Challenge 1: Application not accessible from public internet
**Problem:** Could curl localhost:5000 on EC2 but not from external IP  
**Solution:** Security group wasn't configured correctly—added inbound rule for port 5000 from 0.0.0.0/0

### Challenge 2: App stops when SSH session closes
**Problem:** Running `python app.py` directly terminates when disconnecting  
**Solution:** Implemented systemd service for persistent background execution with auto-restart

### Challenge 3: Permission denied on key file
**Problem:** SSH refused connection with "permissions too open" error  
**Solution:** Changed key file permissions with `chmod 400 your-key.pem`

## Future Enhancements
- [ ] Add PostgreSQL database using AWS RDS
- [ ] Implement CI/CD pipeline with GitHub Actions
- [ ] Add comprehensive unit and integration tests
- [ ] Deploy behind Application Load Balancer for high availability
- [ ] Configure Auto Scaling based on CPU metrics
- [ ] Add CloudWatch alarms for error rates and latency
- [ ] Implement Blue/Green deployment strategy
- [ ] Containerize with Docker and deploy to ECS
- [ ] Add API documentation with Swagger/OpenAPI
- [ ] Implement caching layer with ElastiCache

## Repository Structure
```
flask-api-ec2/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── deployment/
│   └── setup.sh             # Automated deployment script
├── screenshots/             # Project screenshots
│   ├── ec2-console.png
│   ├── api-response.png
│   └── systemd-status.png
└── README.md                # This file
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u flask-app -n 50

# Check if port is in use
sudo netstat -tulpn | grep 5000

# Verify file paths in service file
sudo systemctl cat flask-app
```

### Can't connect from browser
- Verify security group allows port 5000
- Check if service is running: `sudo systemctl status flask-app`
- Verify you're using HTTP (not HTTPS): `http://PUBLIC_IP:5000`

### Dependencies won't install
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

## License
MIT License - feel free to use this project for learning purposes

## Author
Mustafa Hassan  
[LinkedIn](www.linkedin.com/in/mustafa-hassan-b13a86226)

## Acknowledgments
- Flask documentation: https://flask.palletsprojects.com/
- AWS EC2 documentation: https://docs.aws.amazon.com/ec2/
- Gunicorn documentation: https://docs.gunicorn.org/
