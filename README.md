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


######################DEBUG##################################

Build
```bash
docker compose build web
```
Run
```bash
docker compose up -d
```
Check version of debugpy
```bash
docker compose exec web python3 -n debugpy --version
```



Set Breakpoint
Create forlder .vscode and file launch.json with the following content:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach (Odoo)",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "127.0.0.1",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/addons",
                    "remoteRoot": "/mnt/extra-addons"
                }
            ],
            "justMyCode": false,
            "subProcess": false
        }
    ]
}
```


```bash
docker compose down && DEBUGPY=wait docker compose up -d
```

FINAL
If not started
```bash
docker compse up -d
```
then

```bash
docker compose stop web
docker compose run --rm --entrypoint /usr/bin/odoo web -u bookstore -d bookstore_db --stop-after-init
DEBUGPY=wait docker compose up -d web
```
in VSCode F5 - to connect to odoo (otherwise won't work)


# ROADMAP

✅ 1. Инфраструктура (odoo.conf, dev/prod, бэкапы)	
✅ 2. Remote Debugging (debugpy)	
✅ 3. REST API controllers (for authors only), RPC (for books) + API for external extended modules (partners)
✅ 4. Many2many (Genres)
✅ 5. @api.constrains
✅ 6. @api.onchange 
✅ 7. _inherit — extending res.partner 
✅ 8. CRUD overrides (create/write/unlink + sequence)	(override create() via super())
✅ 9. Graph/Pivot views	
⬜ 10. QWeb PDF reports	
⬜ 11. Autotests (unittest)	
⬜ 12. CI/CD	



### API coverage
1. REST API in Odoo — type='http', HTTP-methods, JSON-bodies, statuses.
2. JSON-RPC — type='json', POST for all (Odoo-native).
3. Difference between 2 above and when to use each of them.
4. API versioning — /api/v1/.
5. Thin controllers + thick models — correct architecture.
6. @api.model methods - for operations on model level.
7. Mixins — ApiMixin for shared helpers.
8. Errors handling - ValueError -> HTTP 400.
9. Serialization - to_api_dict().
10. Correct HTTP-contract — 200, 201, 400, 404.

### CRUD coverage
1. @api.constrains('favorite_genre_ids') 
2. @api.model_create_multi + create() with  super() 
3. write() с super() and logging added
4. Test 1 (6 жанров) → ValidationError
5. Test 2 (create/write) → log in  docker compose logs
Create/update check in logs:
```bash 
docker compose logs web --tail=10 | grep "Bookstore"
```
7. Test 4 (search) → works

```bash
docker compose exec web odoo shell -d bookstore_db
#----------------------------------------------------
genre = env['bookstore.genre'].search([('name', '=', 'Fiction')], limit=1)
partners = env['res.partner'].search([('favorite_genre_ids', 'in', genre.id)])
print(partners.mapped('name'))
# Expected: list of partners with a genre Fiction
```