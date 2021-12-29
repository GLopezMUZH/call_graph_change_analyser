/* occurrence Table*/

/*
CREATE TABLE occurrence(
    element_id INTEGER NOT NULL, 
    source_location_id INTEGER NOT NULL, 
    PRIMARY KEY(element_id, source_location_id), 
    FOREIGN KEY(element_id) REFERENCES element(id) ON DELETE CASCADE, 
    FOREIGN KEY(source_location_id) REFERENCES source_location(id) ON DELETE CASCADE
    )
*/



CREATE TABLE occurrence_hist (
	element_id	INTEGER NOT NULL,
	source_location_id	INTEGER NOT NULL,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER occurrence_insert AFTER INSERT
ON occurrence
BEGIN
  INSERT INTO occurrence_hist(element_id, source_location_id, insert_date) VALUES (new.element_id, new.source_location_id, datetime('now'));
END;


CREATE TRIGGER occurrence_delete AFTER DELETE
ON occurrence
BEGIN
  UPDATE occurrence_hist set delete_date = datetime('now') WHERE element_id = old.element_id AND source_location_id = old.source_location_id;
END;


CREATE TRIGGER occurrence_before_delete
BEFORE DELETE 
ON occurrence FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM occurrence_hist WHERE element_id = old.element_id AND source_location_id = old.source_location_id)
BEGIN
      INSERT INTO occurrence_hist(element_id, source_location_id, oldest_reference_date) VALUES(old.element_id, old.source_location_id, datetime('now'));
END;


CREATE TRIGGER occurrence_update
AFTER UPDATE 
ON occurrence FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM occurrence_hist WHERE element_id = old.element_id AND source_location_id = old.source_location_id)
BEGIN
      INSERT INTO occurrence_hist(element_id, source_location_id, oldest_reference_date) VALUES(old.element_id, old.source_location_id, datetime('now'));
END;