This servers as a list of available commands for the application.

1. Check the db
   curl -s http://localhost:8000/api/documents/ | python3 -m json.tool
   Look for documents with status: "processing" or status: "failed"

2. Fix stuck documents

```
docker exec airag_postgres psql -U postgres -d app_db -c "
  SELECT id, original_filename, status
  FROM documents
  WHERE status IN ('processing', 'failed', 'pending');
  "
```

Step 2: Delete stuck documents (replace 3,4,9 with actual IDs)

# Delete chunks first (if any)

```
docker exec airag_postgres psql -U postgres -d app_db -c "
DELETE FROM document_chunks WHERE document_id IN (3,4,9);
"
```

# Then delete documents

```
docker exec airag_postgres psql -U postgres -d app_db -c "
DELETE FROM documents WHERE id IN (3,4,9);
```

3. Best Tools to Check the Database

Option A: Command Line (Quick & Easy)

Basic connection:
docker exec -it airag_postgres psql -U postgres -d app_db

Once connected, useful commands:
-- List all tables
\dt

-- Describe documents table structure
\d documents

-- View all documents
SELECT \* FROM documents ORDER BY created_at DESC;
