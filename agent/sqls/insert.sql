INSERT INTO "DOCUMENT_VECTORS" 
("SOURCE_FILE", "CHUNK_TEXT", "EMBEDDING", "SUMMARY", "DOC_TYPE", "FULL_METADATA", "CREATED_ON", "MODIFIED_ON")
VALUES
(:source_file, :chunk_text, :embedding, :summary, :doc_type, :full_metadata, :created_on, :modified_on)