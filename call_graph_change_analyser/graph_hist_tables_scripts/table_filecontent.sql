/* filecontent Table*/

/*
CREATE TABLE filecontent(
    id INTEGER, 
    content TEXT, 
    PRIMARY KEY(id), 
    FOREIGN KEY(id) REFERENCES file(id)ON DELETE CASCADE ON UPDATE CASCADE
)
*/


CREATE TABLE filecontent_hist (
	file_id	INTEGER NOT NULL,
	content	TEXT,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER filecontent_insert AFTER INSERT
ON filecontent
BEGIN
  INSERT INTO filecontent_hist(file_id, content, insert_date) VALUES (new.id, "new.content", datetime('now'));
END;


CREATE TRIGGER filecontent_delete AFTER DELETE
ON filecontent
BEGIN
  UPDATE filecontent_hist set delete_date = datetime('now') WHERE file_id = old.id AND (delete_date is null or delete_date = '');
END;


CREATE TRIGGER filecontent_before_delete
BEFORE DELETE 
ON filecontent FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM filecontent_hist WHERE file_id = old.id AND (delete_date is null or delete_date = ''))
BEGIN
      INSERT INTO filecontent_hist(file_id, content, oldest_reference_date) VALUES(old.id, "old.content", datetime('now'));
END;


CREATE TRIGGER filecontent_update
AFTER UPDATE 
ON filecontent FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM filecontent_hist WHERE file_id = old.id AND (delete_date is null or delete_date = ''))
BEGIN
      INSERT INTO filecontent_hist(file_id, content, oldest_reference_date) VALUES(old.id, "old.content", datetime('now'));
END;