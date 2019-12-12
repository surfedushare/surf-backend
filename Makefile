media-to-local:
	rsync -zrthv --progress $(remote):/volumes/surf/media .

media-to-remote:
	rsync -zrthv --progress media $(remote):/volumes/surf/

tests:
	docker-compose -f docker-compose-local.yml run --rm backend python manage.py test --settings=surf.settings.tests --nomigrations $(filter)

backup-db:
	docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) pg_dump -h localhost -U surf -c surf > edushare.${now}.postgres.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) psql -h localhost -U surf surf
