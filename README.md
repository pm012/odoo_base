# odoo_base

for linux 
sudo chown -R $USER:$USER ./addons
chmod -R 775 ./addons

abligatory reread the created folder (docker compose down, docker compose up -d)
docker compose exec web odoo -u bookstore -d bookstore_dev -r odoo -w odoo --db_host=db --stop-after-init



