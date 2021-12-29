/* local_symbol Table*/

/*
CREATE TABLE local_symbol(
    id INTEGER NOT NULL, 
    name TEXT, 
    PRIMARY KEY(id), 
    FOREIGN KEY(id) REFERENCES element(id) ON DELETE CASCADE
    )
*/


CREATE TABLE local_symbol_hist (
	element_id	INTEGER NOT NULL,
	name	TEXT,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER local_symbol_insert AFTER INSERT
ON local_symbol
BEGIN
  INSERT INTO local_symbol_hist(element_id, name, insert_date) VALUES (new.id, new.name, datetime('now'));
END;


CREATE TRIGGER local_symbol_delete AFTER DELETE
ON local_symbol
BEGIN
  UPDATE local_symbol_hist set delete_date = datetime('now') WHERE element_id = old.id AND name = old.name;
END;


CREATE TRIGGER local_symbol_before_delete
BEFORE DELETE 
ON local_symbol FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM local_symbol_hist WHERE element_id = old.id AND name = old.name)
BEGIN
      INSERT INTO local_symbol_hist(element_id, name, oldest_reference_date) VALUES(old.id, old.name, datetime('now'));
END;


CREATE TRIGGER local_symbol_update
AFTER UPDATE 
ON local_symbol FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM local_symbol_hist WHERE element_id = old.id AND name = old.name)
BEGIN
      INSERT INTO local_symbol_hist(element_id, name, oldest_reference_date) VALUES(old.id, old.name, datetime('now'));
END;