/* source_location Table */

/*
CREATE TABLE source_location(
    id INTEGER NOT NULL, 
    file_node_id INTEGER, 
    start_line INTEGER, 
    start_column INTEGER, 
    end_line INTEGER, 
    end_column INTEGER, 
    type INTEGER, 
    PRIMARY KEY(id), 
    FOREIGN KEY(file_node_id) REFERENCES node(id) ON DELETE CASCADE
    )
*/



CREATE TABLE source_location_hist (
	source_location_id	INTEGER NOT NULL,
    file_node_id INTEGER, 	
	start_line TEXT,
    start_column INTEGER,
    end_line INTEGER,
    end_column INTEGER, 
    type INTEGER, 
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER source_location_insert AFTER INSERT
ON source_location
BEGIN
  INSERT INTO source_location_hist(source_location_id, file_node_id, start_line, start_column, end_line, end_column, type, insert_date) 
  VALUES (new.id, new.file_node_id, new.start_line, new.start_column, new.end_line, new.end_column, new.type, datetime('now'));
END;


CREATE TRIGGER source_location_delete AFTER DELETE
ON source_location
BEGIN
  UPDATE source_location_hist set delete_date = datetime('now') 
  WHERE source_location_id = old.id AND file_node_id = old.file_node_id AND start_line = old.start_line AND (delete_date is null or delete_date = '');
END;


CREATE TRIGGER source_location_before_delete
BEFORE DELETE 
ON source_location FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM source_location_hist WHERE source_location_id = old.id AND file_node_id = old.file_node_id AND start_line = old.start_line AND (delete_date is null or delete_date = ''))
BEGIN
    INSERT INTO source_location_hist(source_location_id, file_node_id, start_line, start_column, end_line, end_column, type, oldest_reference_date) VALUES (old.id, old.file_node_id, old.start_line, old.start_column, old.end_line, old.end_column, old.type, datetime('now'));
END;


CREATE TRIGGER source_location_update
AFTER UPDATE 
ON source_location FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM source_location_hist WHERE source_location_id = old.id AND start_line = old.start_line AND (delete_date is null or delete_date = ''))
BEGIN
    INSERT INTO source_location_hist(source_location_id, file_node_id, start_line, start_column, end_line, end_column, type, oldest_reference_date) VALUES (old.id, old.file_node_id, old.start_line, old.start_column, old.end_line, old.end_column, old.type, datetime('now'));
END;