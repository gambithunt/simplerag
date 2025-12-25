#!/bin/bash

  echo "=== Document Status Summary ==="
  docker exec airag_postgres psql -U postgres -d app_db -c "
  SELECT status, COUNT(*) as count
  FROM documents
  GROUP BY status
  ORDER BY status;
  "

  echo -e "\n=== Stuck Documents (processing > 5 min) ==="
  docker exec airag_postgres psql -U postgres -d app_db -c "
  SELECT id, original_filename, status,
         EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_stuck
  FROM documents
  WHERE status = 'processing'
    AND created_at < NOW() - INTERVAL '5 minutes'
  ORDER BY created_at;
  "

  echo -e "\n=== Failed Documents ==="
  docker exec airag_postgres psql -U postgres -d app_db -c "
  SELECT id, original_filename,
         LEFT(error_message, 100) as error_preview
  FROM documents
  WHERE status = 'failed';
  "

  echo -e "\n=== Vector Storage ==="
  echo "Qdrant points: $(curl -s http://localhost:6333/collections/documents | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['points_count'])")"
  echo "DB chunks: $(docker exec airag_postgres psql -U postgres -d app_db -t -c "SELECT COUNT(*) FROM document_chunks;")"
