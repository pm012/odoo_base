# Bookstore
The bookstore is ERP for simple book store writen uding Odoo 19. 
Further description and instructions TBD later as the project is in progress (features and demo)



--------------------------------------------------------------
# TECH
NB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Database: bookstore_db
NB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


For linux 
```bash
sudo chown -R $USER:$USER ./addons
chmod -R 775 ./addons
```

####################DOCKER#########################################

1. Obligatory reread the created folder 
```bash
docker compose down
docker compose up -d
```

2. Update application (mostly xml views if sutoupdate .py is set up  - if not both .py and .xml)
It is preferable before views update to restart docker web part
```bash
docker compose restart web
```

Update
```bash
docker compose exec web odoo -u bookstore -d bookstore_dev --stop-after-init
```

NB! if config not mounted:
```bash
docker compose exec web odoo -u bookstore -d bookstore_db -r odoo -w odoo --db_host=db --stop-after-init
```

or to reinstall
```bash
docker compose exec web odoo -i bookstore -d bookstore_db -r odoo -w odoo --db_host=db --stop-after-init
```
TBD: Security (hide some details)

3. See odoo logs:
```bash
 docker compose logs web --tail=100
 ```

###############DATA BASE################################

* backup database: 
```bash
docker compose exec db pg_dump -U odoo bookstore_db > backup_$(date +%Y%m%d).sql
```
* delete usles DB
```bash
docker compose exec db psql -U odoo -d postgres -c "DROP DATABASE bookstore_dev;"
```

If there is need to do something with database (using DBeaver or terminal): 
```bash
docker compose exec db psql -U odoo -d postgres -c "DROP DATABASE bookstore_dev;"
```

#######################ORM#####################################
Check validation via ORM
```bash
docker compose exec web odoo shell -d bookstore_db
```
and try

```bash
book = env['bookstore.book'].create({'name': 'Test Bad', 'price': -5})
```
to check that validation works on the ORM level
(Ctrl+D or exit() to exit)

