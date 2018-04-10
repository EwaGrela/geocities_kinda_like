
ALTER TABLE film ADD category_id INTEGER;

CREATE VIEW helper as SELECT film_list.category, film_list.title, category.category_id FROM film_list JOIN film ON film_list.title = film.title JOIN category ON film_list.category = category.name;

UPDATE film SET category_id = (SELECT category_id FROM helper WHERE film.title = helper.title);

DROP VIEW helper;

DROP TABLE film_category;




