#!/usr/bin/env bash
# Install DVWA only inside the NAT/host-only Kali training VM. Safe to re-run.
set -euo pipefail
DVWA_DIR="/var/www/html/DVWA"
sudo apt-get update
sudo apt-get install -y apache2 mariadb-server git php php-mysql php-gd php-curl php-xml php-mbstring
sudo systemctl enable --now apache2 mariadb
if [ ! -d "$DVWA_DIR/.git" ]; then
  sudo git clone https://github.com/digininja/DVWA.git "$DVWA_DIR"
else
  echo "DVWA already exists; leaving its checked-out version unchanged."
fi
sudo cp -n "$DVWA_DIR/config/config.inc.php.dist" "$DVWA_DIR/config/config.inc.php" || true
# Default security level is configuration/session based in modern DVWA, not a DB column.
sudo sed -i "s/\$_DVWA\[ 'db_user' \].*/\$_DVWA[ 'db_user' ]     = 'dvwa';/; s/\$_DVWA\[ 'db_password' \].*/\$_DVWA[ 'db_password' ] = 'dvwa_password';/; s/\$_DVWA\[ 'default_security_level' \].*/\$_DVWA[ 'default_security_level' ] = 'low';/" "$DVWA_DIR/config/config.inc.php"
sudo mariadb <<'SQL'
CREATE DATABASE IF NOT EXISTS dvwa;
CREATE USER IF NOT EXISTS 'dvwa'@'localhost' IDENTIFIED BY 'dvwa_password';
GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa'@'localhost';
FLUSH PRIVILEGES;
SQL
sudo chown -R www-data:www-data "$DVWA_DIR"
sudo a2enmod rewrite remoteip
# This is intentionally safe only in the NAT/host-only training VM: it lets
# Apache record the simulator's X-Forwarded-For training address.
printf '%s\n' 'RemoteIPHeader X-Forwarded-For' | sudo tee /etc/apache2/conf-available/cyberlab-remoteip.conf >/dev/null
sudo a2enconf cyberlab-remoteip
sudo systemctl restart apache2
echo "Open http://localhost/DVWA/setup.php once and select Create / Reset Database."
echo "Then log in at http://localhost/DVWA with admin / password (DVWA default)."
echo "Apache logs simulator source IPs in standard combined format at /var/log/apache2/access.log."
