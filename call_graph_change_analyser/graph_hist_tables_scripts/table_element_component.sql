/* element_component Table*/

/*
CREATE TABLE element_component(	
    id INTEGER, 	
    element_id INTEGER, 	
    type INTEGER, 	
    data TEXT, 	
    PRIMARY KEY(id), 	
    FOREIGN KEY(element_id) REFERENCES element(id) ON DELETE CASCADE
    )
*/


CREATE TABLE element_component_hist (
	element_component_id	INTEGER NOT NULL,
  element_id INTEGER, 	
	type	INTEGER NOT NULL,
  data TEXT, 	
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER element_component_insert AFTER INSERT
ON element_component
BEGIN
  INSERT INTO element_component_hist(element_component_id, element_id, type, data, insert_date) VALUES (new.id, new.element_id, new.type, new.data, datetime('now'));
END;


CREATE TRIGGER element_component_delete AFTER DELETE
ON element_component
BEGIN
  UPDATE element_component_hist set delete_date = datetime('now') WHERE element_component_id = old.id AND element_id = old.element_id AND type = old.type AND data = old.data;
END;


CREATE TRIGGER element_component_before_delete
BEFORE DELETE 
ON element_component FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM element_component_hist WHERE element_component_id = old.id AND element_id = old.element_id AND type = old.type AND data = old.data)
BEGIN
      INSERT INTO element_component_hist(element_component_id, element_id, type, data, oldest_reference_date) VALUES(old.id, old.element_id, old.type, old.data, datetime('now'));
END;


CREATE TRIGGER element_component_update
AFTER UPDATE 
ON element_component FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM element_component_hist WHERE element_component_id = old.id AND type = old.type AND data = old.data)
BEGIN
      INSERT INTO element_component_hist(element_component_id, element_id, type, data, oldest_reference_date) VALUES(old.id, old.element_id, old.type, old.data, datetime('now'));
END;