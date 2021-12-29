/* file Table */

/*
CREATE TABLE file(
    id INTEGER NOT NULL, 
    path TEXT, 
    language TEXT, 
    modification_time TEXT, 
    indexed INTEGER, 
    complete INTEGER, 
    line_count INTEGER, 
    PRIMARY KEY(id), 
    FOREIGN KEY(id) REFERENCES node(id) ON DELETE CASCADE
    )
*/


CREATE TABLE file_hist (
	file_id	INTEGER NOT NULL,
    path TEXT, 	
	language TEXT,
    modification_time TEXT,
    indexed INTEGER,
    complete INTEGER, 
    line_count INTEGER, 
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER file_insert AFTER INSERT
ON file
BEGIN
  INSERT INTO file_hist(file_id, path, language, modification_time, indexed, complete, line_count, insert_date) VALUES (new.id, new.path, new.language, new.modification_time, new.indexed, new.complete, new.line_count, datetime('now'));
END;


CREATE TRIGGER file_delete AFTER DELETE
ON file
BEGIN
  UPDATE file_hist set delete_date = datetime('now') WHERE file_id = old.id AND path = old.path AND language = old.language AND (delete_date is null or delete_date = '');
END;


CREATE TRIGGER file_before_delete
BEFORE DELETE 
ON file FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM file_hist WHERE file_id = old.id AND path = old.path AND language = old.language AND (delete_date is null or delete_date = ''))
BEGIN
    INSERT INTO file_hist(file_id, path, language, modification_time, indexed, complete, line_count, oldest_reference_date) VALUES (old.id, old.path, old.language, old.modification_time, old.indexed, old.complete, old.line_count, datetime('now'));
END;


CREATE TRIGGER file_update
AFTER UPDATE 
ON file FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM file_hist WHERE file_id = old.id AND language = old.language AND (delete_date is null or delete_date = ''))
BEGIN
    INSERT INTO file_hist(file_id, path, language, modification_time, indexed, complete, line_count, oldest_reference_date) VALUES (old.id, old.path, old.language, old.modification_time, old.indexed, old.complete, old.line_count, datetime('now'));
END;