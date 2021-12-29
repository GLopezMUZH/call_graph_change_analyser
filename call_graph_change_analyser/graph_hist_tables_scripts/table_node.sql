/* node Table */

/*
CREATE TABLE node(
id INTEGER NOT NULL, 
type INTEGER NOT NULL, 
serialized_name TEXT, 
PRIMARY KEY(id),
FOREIGN KEY(id) REFERENCES element(id) ON DELETE CASCADE
)
*/

CREATE TABLE node_hist (
	node_id	INTEGER NOT NULL,
	type	INTEGER NOT NULL,
	serialized_name	TEXT,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER node_insert AFTER INSERT
ON node
BEGIN
  INSERT INTO node_hist(node_id, type, serialized_name, insert_date) VALUES (new.id, new.type, new.serialized_name, datetime('now'));
END;


CREATE TRIGGER node_delete AFTER DELETE
ON node
BEGIN
  UPDATE node_hist set delete_date = datetime('now') WHERE node_id = old.id AND type = old.type AND serialized_name = old.serialized_name;
END;


CREATE TRIGGER node_before_delete
BEFORE DELETE 
ON node FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM node_hist WHERE node_id = old.id AND type = old.type AND serialized_name = old.serialized_name)
BEGIN
      INSERT INTO node_hist(node_id, type, serialized_name, oldest_reference_date) VALUES(old.id, old.type, old.serialized_name, datetime('now'));
END;


CREATE TRIGGER node_update
AFTER UPDATE 
ON node FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM node_hist WHERE node_id = old.id AND type = old.type AND serialized_name = old.serialized_name)
BEGIN
      INSERT INTO node_hist(node_id, type, serialized_name, oldest_reference_date) VALUES(old.id, old.type, old.serialized_name, datetime('now'));
END;