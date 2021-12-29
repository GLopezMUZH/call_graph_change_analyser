/* component_access Table */

/*
CREATE TABLE component_access(
    node_id INTEGER NOT NULL, 
    type INTEGER NOT NULL, 
    PRIMARY KEY(node_id), 
    FOREIGN KEY(node_id) REFERENCES node(id) ON DELETE CASCADE)
*/


CREATE TABLE component_access_hist (
	node_id	INTEGER NOT NULL,
	type	INTEGER NOT NULL,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER component_access_insert AFTER INSERT
ON component_access
BEGIN
  INSERT INTO component_access_hist(node_id, type, insert_date) VALUES (new.node_id, new.type, datetime('now'));
END;


CREATE TRIGGER component_access_delete AFTER DELETE
ON component_access
BEGIN
  UPDATE component_access_hist set delete_date = datetime('now') WHERE node_id = old.node_id AND type = old.type;
END;


CREATE TRIGGER component_access_before_delete
BEFORE DELETE 
ON component_access FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM component_access_hist WHERE node_id = old.node_id AND type = old.type)
BEGIN
      INSERT INTO component_access_hist(node_id, type, oldest_reference_date) VALUES(old.node_id, old.type, datetime('now'));
END;


CREATE TRIGGER component_access_update
AFTER UPDATE 
ON component_access FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM component_access_hist WHERE node_id = old.node_id AND type = old.type)
BEGIN
      INSERT INTO component_access_hist(node_id, type, oldest_reference_date) VALUES(old.node_id, old.type, datetime('now'));
END;