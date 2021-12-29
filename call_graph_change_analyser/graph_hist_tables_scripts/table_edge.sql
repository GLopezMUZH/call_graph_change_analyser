/*edge Table*/

/*
CREATE TABLE edge(
    id INTEGER NOT NULL, 
    type INTEGER NOT NULL, 
    source_node_id INTEGER NOT NULL, 
    target_node_id INTEGER NOT NULL, 
    PRIMARY KEY(id), 
    FOREIGN KEY(id) REFERENCES element(id) ON DELETE CASCADE, 
    FOREIGN KEY(source_node_id) REFERENCES node(id) ON DELETE CASCADE, 
    FOREIGN KEY(target_node_id) REFERENCES node(id) ON DELETE CASCADE)
*/



CREATE TABLE edge_hist (
	edge_id	INTEGER NOT NULL,
	type	INTEGER NOT NULL,
  source_node_id INTEGER NOT NULL, 
  target_node_id INTEGER NOT NULL, 
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER edge_insert AFTER INSERT
ON edge
BEGIN
  INSERT INTO edge_hist(edge_id, type, source_node_id, target_node_id, insert_date) VALUES (new.id, new.type, new.source_node_id, new.target_node_id, datetime('now'));
END;


CREATE TRIGGER edge_delete AFTER DELETE
ON edge
BEGIN
  UPDATE edge_hist set delete_date = datetime('now') WHERE edge_id = old.id AND type = old.type AND source_node_id = old.source_node_id AND target_node_id = old.target_node_id;
END;


CREATE TRIGGER edge_before_delete
BEFORE DELETE 
ON edge FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM edge_hist WHERE edge_id = old.id AND type = old.type)
BEGIN
      INSERT INTO edge_hist(edge_id, type, source_node_id, target_node_id, oldest_reference_date) VALUES(old.id, old.type, old.source_node_id, old.target_node_id, datetime('now'));
END;


CREATE TRIGGER edge_update
AFTER UPDATE 
ON edge FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM edge_hist WHERE edge_id = old.id AND type = old.type)
BEGIN
      INSERT INTO edge_hist(edge_id, type, source_node_id, target_node_id, oldest_reference_date) VALUES(old.id, old.type, old.source_node_id, old.target_node_id, datetime('now'));
END;