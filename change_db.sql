
ALTER TABLE film ADD category_id INTEGER;

-- tworzymy pomocniczy view, do usuniecia potem 
CREATE VIEW helper as SELECT film_list.category, film_list.title, category.category_id FROM film_list JOIN film ON film_list.title = film.title JOIN category ON film_list.category = category.name;
 -- ustawiamy wartosci
UPDATE film SET category_id = (SELECT category_id FROM helper WHERE film.title = helper.title);
-- usuwamy z bazy view 
DROP VIEW helper;
-- usuwamy nadmiarową tabelę
DROP TABLE film_category;




