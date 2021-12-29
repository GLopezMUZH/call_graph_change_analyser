/* symbol Table */

/*
CREATE TABLE symbol(
    id INTEGER NOT NULL, 
    definition_kind INTEGER NOT NULL, 
    PRIMARY KEY(id), 
    FOREIGN KEY(id) REFERENCES node(id) ON DELETE CASCADE
    )
*/


CREATE TABLE symbol_hist (
	node_id	INTEGER NOT NULL,
	definition_kind	INTEGER NOT NULL,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER symbol_insert AFTER INSERT
ON symbol
BEGIN
  INSERT INTO symbol_hist(node_id, definition_kind, insert_date) VALUES (new.id, new.definition_kind, datetime('now'));
END;


CREATE TRIGGER symbol_delete AFTER DELETE
ON symbol
BEGIN
  UPDATE symbol_hist set delete_date = datetime('now') WHERE node_id = old.id AND definition_kind = old.definition_kind;
END;


CREATE TRIGGER symbol_before_delete
BEFORE DELETE 
ON symbol FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM symbol_hist WHERE node_id = old.id AND definition_kind = old.definition_kind)
BEGIN
      INSERT INTO symbol_hist(node_id, definition_kind, oldest_reference_date) VALUES(old.id, old.definition_kind, datetime('now'));
END;


CREATE TRIGGER symbol_update
AFTER UPDATE 
ON symbol FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM symbol_hist WHERE node_id = old.id AND definition_kind = old.definition_kind)
BEGIN
      INSERT INTO symbol_hist(node_id, definition_kind, oldest_reference_date) VALUES(old.id, old.definition_kind, datetime('now'));
END;