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

Step 3: Re-upload the files

The original files are still in the uploads folder at:
ls -lah /Users/delon/Documents/code/projects/ai-rag-system/uploads/

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

-- Check for stuck documents (processing > 5 mins)
SELECT id, original_filename, status,
NOW() - created_at as age
FROM documents
WHERE status = 'processing'
AND created_at < NOW() - INTERVAL '5 minutes';

-- Exit psql
\q

1. pgAdmin (Most Popular)

- Download: https://www.pgadmin.org/download/
- Connection details:
  - Host: localhost
  - Port: 5432
  - Database: app_db
  - Username: postgres
  - Password: postgres

Check system health:

# Document counts by status

docker exec airag_postgres psql -U postgres -d app_db -c "
SELECT status, COUNT(\*) as count FROM documents GROUP BY status;
"

# Vector count in Qdrant

curl -s http://localhost:6333/collections/documents | python3 -m json.tool | grep points_count

# Expected vs actual chunks

docker exec airag_postgres psql -U postgres -d app_db -c "
SELECT
d.id,
d.original_filename,
d.chunk_count as expected_chunks,
COUNT(dc.id) as actual_chunks,
d.status
FROM documents d
LEFT JOIN document_chunks dc ON d.id = dc.document_id
GROUP BY d.id, d.original_filename, d.chunk_count, d.status
ORDER BY d.id;
"

Quick Reference: Connection Details

PostgreSQL Database

Host: localhost
Port: 5432
Database: app_db
Username: postgres
Password: postgres

Qdrant Vector DB

Host: localhost
Port: 6333 (HTTP API)
Port: 6334 (gRPC)
Web UI: http://localhost:6333/dashboard

Application API

Base URL: http://localhost:8000
Docs: http://localhost:8000/docs (Swagger UI)
Frontend: http://localhost:8000
