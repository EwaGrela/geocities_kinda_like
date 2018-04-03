from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    make_response
)
from datetime import datetime
import sqlite3


app = Flask(__name__)

DATABASE = "database.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def home():
	return "OK, that works"

@app.route("/cities", methods =["POST", "GET"])
def all_cities():
	if request.method =="GET":
		return cities()
	elif request.method == "POST":
		return add_cities()
def cities():
	title = "All cities"
	cn = request.args.get('country_name')
	lim = request.args.get('per_page')
	offs = request.args.get('page')
	db = get_db()
	if cn is None:
		if lim is not None and offs is not None:
			cities = db.execute('SELECT city FROM city ORDER BY city COLLATE NOCASE ASC LIMIT :lim OFFSET :offs', {'lim':int(lim), 'offs':(int(offs)-1)*int(lim)}).fetchall()
		else:
			cities = db.execute('SELECT city FROM city ORDER BY city COLLATE NOCASE ASC').fetchall()
	else:
		if lim is not None and offs is not None:
			cities = db.execute(
			'SELECT city FROM city WHERE country_id = (SELECT country_id FROM country WHERE country = :country_name) ORDER BY city COLLATE NOCASE ASC LIMIT :lim OFFSET :offs', 
			{'country_name': cn, 'lim':int(lim), 'offs':(int(offs)-1)*int(lim)}).fetchall()
		else:	
			cities = db.execute(
			'SELECT city FROM city WHERE country_id = (SELECT country_id FROM country WHERE country = :country_name) ORDER BY city COLLATE NOCASE ASC', 
			{'country_name': cn}).fetchall()
	c = []
	for city in cities:
		c.append(city['city'])
	return jsonify(c)

def add_cities():
	data = request.get_json()
	print(data, type(data))
	db = get_db()
	print(data["country_id"])
	# keys = tuple(data.keys())
	# vals = tuple(data.values())
	# print(keys)
	# print(vals)

	ids = db.execute('SELECT DISTINCT country_id FROM city').fetchall()
	maxim = db.execute('select max(city_id) as maxim from city').fetchone()
	idxs = [i["country_id"] for i in ids]
	if data["country_id"] in idxs:
		created = db.execute('INSERT INTO city (city_id, city, country_id, last_update) VALUES (:city_id, :city, :country_id, :last_update)', 
			{'city_id':(maxim['maxim']+1), 'city': data['city_name'], 'country_id':data['country_id'], 'last_update': str(datetime.utcnow())})
		db.commit()
		print(created, type(created))
		res = {}
		return make_response('added', 200)
	else:
		return make_response('bad country_id!', 400, {'error' : 'wrong country_id'})

	return "ok"


@app.route("/lang_roles")
def lang_roles():
	title = "Roles in language"
	db = get_db()
	view = db.execute('CREATE view if not exists lang_roles as select film.film_id, film.language_id, film_list.actors, language.name from language left join film on language.language_id = film.language_id join film_list on film.film_id = film_list.FID')
	langs = db.execute('SELECT * from language')
	results = {}
	for lang in langs:
		row = db.execute('select name, count(film_id || actors) as result from lang_roles group by name having name = :lang', {'lang': lang['name']}).fetchone()
		if row is not None:
			results[lang['name']] = row['result']
		else:
			results[lang['name']] = 0
	return jsonify(results)

		


if __name__ == '__main__':
	app.run(debug=True)