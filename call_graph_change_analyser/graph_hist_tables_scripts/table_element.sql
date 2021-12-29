/* element Table */

/*
CREATE TABLE element(id INTEGER, PRIMARY KEY(id))
*/


CREATE TABLE element_hist (
	element_id	INTEGER NOT NULL,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER element_insert AFTER INSERT
ON element
BEGIN
  INSERT INTO element_hist(element_id, insert_date) VALUES (new.id, datetime('now'));
END;


CREATE TRIGGER element_delete AFTER DELETE
ON element
BEGIN
  UPDATE element_hist set delete_date = datetime('now') WHERE element_id = old.id;
END;


CREATE TRIGGER element_before_delete
BEFORE DELETE 
ON element FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM element_hist WHERE element_id = old.id)
BEGIN
      INSERT INTO element_hist(element_id, oldest_reference_date) VALUES(old.id, datetime('now'));
END;


CREATE TRIGGER element_update
AFTER UPDATE 
ON element FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM element_hist WHERE element_id = old.id)
BEGIN
      INSERT INTO element_hist(element_id, oldest_reference_date) VALUES(old.id, datetime('now'));
END;