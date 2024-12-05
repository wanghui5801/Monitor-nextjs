#!/bin/bash

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Print message function
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if the user is root
if [ "$EUID" -ne 0 ]; then
    print_message "Please run as root" "$RED"
    exit 1
fi

# Get user input
read -p "Enter your domain name (e.g., monitor.1101949.xyz): " DOMAIN_NAME
read -p "Enter your email for SSL certificate: " EMAIL

# Install necessary packages
print_message "Installing required packages..." "$GREEN"
apt-get update
apt-get install -y nginx certbot

# Stop nginx to get the certificate
systemctl stop nginx

# Get SSL certificate
print_message "Obtaining SSL certificate..." "$GREEN"
certbot certonly --standalone -d "${DOMAIN_NAME}" --non-interactive --agree-tos --email "${EMAIL}"

# Configure Nginx
print_message "Configuring Nginx..." "$GREEN"
cat > /etc/nginx/sites-available/${DOMAIN_NAME}.conf << EOL
server {
    listen 80;
    server_name ${DOMAIN_NAME};
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name ${DOMAIN_NAME};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Enable site configuration
ln -sf /etc/nginx/sites-available/${DOMAIN_NAME}.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Update frontend configuration
print_message "Updating frontend configuration..." "$GREEN"
cd /opt/server-monitor || exit

# Update frontend/config/config.ts
cat > frontend/config/config.ts << EOL
const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    return \`https://\${hostname}\`;
  }
  
  return 'http://localhost:5000';
};

export const API_URL = getApiUrl();
EOL

# Update API URL in ecosystem.config.js
sed -i "s|NEXT_PUBLIC_API_URL: 'http://localhost:5000'|NEXT_PUBLIC_API_URL: 'https://${DOMAIN_NAME}'|" ecosystem.config.js

# Rebuild frontend
cd frontend || exit
npm run build

# Restart services
print_message "Restarting services..." "$GREEN"
pm2 restart all

# Test Nginx configuration
nginx -t

# Start Nginx
systemctl start nginx

print_message "Domain setup completed successfully!" "$GREEN"
print_message "Your application is now available at:" "$GREEN"
print_message "https://${DOMAIN_NAME}" "$GREEN"
print_message "Please update your existing clients to use the new domain." "$YELLOW"