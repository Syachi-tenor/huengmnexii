# for postgres
backup.sql:
	docker compose exec -T db pg_dump -U appuser appdb > $@

# for sqlite
app.sql: %.sql: %.db
	sqlite3 $< .dump > $@

clean:
	rm -f *.sql *~ .*~
