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

/* element Table */

/*
CREATE TABLE element(id INTEGER, PRIMARY KEY(id))
*/


CREATE TABLE element_hist (
	element_id	INTEGER NOT NULL,
	insert_date	TEXT,
	oldest_reference_date TEXT,
	delete_date	TEXT
);

CREATE TRIGGER element_insert AFTER INSERT
ON element
BEGIN
  INSERT INTO element_hist(element_id, insert_date) VALUES (new.id, datetime('now'));
END;


CREATE TRIGGER element_delete AFTER DELETE
ON element
BEGIN
  UPDATE element_hist set delete_date = datetime('now') WHERE element_id = old.id;
END;


CREATE TRIGGER element_before_delete
BEFORE DELETE 
ON element FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM element_hist WHERE element_id = old.id)
BEGIN
      INSERT INTO element_hist(element_id, oldest_reference_date) VALUES(old.id, datetime('now'));
END;


CREATE TRIGGER element_update
AFTER UPDATE 
ON element FOR EACH ROW
WHEN NOT EXISTS (SELECT 1 FROM element_hist WHERE element_id = old.id)
BEGIN
      INSERT INTO element_hist(element_id, oldest_reference_date) VALUES(old.id, datetime('now'));
END;

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