# odoo_base
NB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Database: bookstore_db
NB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

for linux 
sudo chown -R $USER:$USER ./addons
chmod -R 775 ./addons

abligatory reread the created folder (docker compose down, docker compose up -d)


docker compose exec web odoo -u bookstore -d bookstore_db -r odoo -w odoo --db_host=db --stop-after-init

або 
docker compose exec web odoo -i bookstore -d bookstore_db -r odoo -w odoo --db_host=db --stop-after-init

sometimes before this you need to do 
docker compose restart web

logging: docker compose logs web --tail=100

