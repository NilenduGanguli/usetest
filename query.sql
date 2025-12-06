SELECT segment_type,
       ROUND(SUM(bytes) / 1024 / 1024, 2) AS size_mb
FROM dba_segments
WHERE owner = UPPER(NVL('&SCHEMA', USER))
  AND (
       segment_name = UPPER('&TABLE_NAME')
       OR segment_name IN (
            SELECT index_name
            FROM dba_indexes
            WHERE table_owner = UPPER(NVL('&SCHEMA', USER))
              AND table_name = UPPER('&TABLE_NAME')
       )
       OR segment_name IN (
            SELECT segment_name
            FROM dba_lobs
            WHERE owner = UPPER(NVL('&SCHEMA', USER))
              AND table_name = UPPER('&TABLE_NAME')
       )
      )
GROUP BY segment_type
ORDER BY size_mb DESC;
