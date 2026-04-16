
-- Check sessions across all tables
SELECT
    MAX(CASE WHEN table_name = 'SystemRank' THEN max_total END) AS SystemRank_max_total,
    MAX(CASE WHEN table_name = 'SymptomSystemKG' THEN max_total END) AS SymptomSystemKG_max_total,
    MAX(CASE WHEN table_name = 'KnowledgeGraphs' THEN max_total END) AS KnowledgeGraphs_max_total,
    MAX(CASE WHEN table_name = 'SessionMetric' THEN max_total END) AS SessionMetric_max_total,
    MAX(CASE WHEN table_name = 'Summary' THEN max_total END) AS Summary_max_total,
    MAX(CASE WHEN table_name = 'Turn' THEN max_total END) AS Turn_max_total,
    MAX(CASE WHEN table_name = 'Session' THEN max_total END) AS Session_max_total
FROM (
    SELECT
        'SymptomRank' AS table_name, MAX(SessionId) AS max_total FROM SymptomRank
    UNION ALL
    SELECT
        'SystemRank' AS table_name, MAX(SessionId) AS max_total FROM SystemRank
    UNION ALL
    SELECT
        'SymptomSystemKG' AS table_name, MAX(SessionId) AS max_total FROM SymptomSystemKG
    UNION ALL
    SELECT
        'KnowledgeGraphs' AS table_name, MAX(SessionId) AS max_total FROM KnowledgeGraphs
    UNION ALL
    SELECT
        'SessionMetric' AS table_name, MAX(SessionId) AS max_total FROM SessionMetric
    UNION ALL
    SELECT
        'Summary' AS table_name, MAX(SessionId) AS max_total FROM Summary
    UNION ALL
    SELECT
        'Turn' AS table_name, MAX(SessionId) AS max_total FROM Turn
    UNION ALL
    SELECT
        'Session' AS table_name, MAX(SessionId) AS max_total FROM Session
) AS all_tables;
