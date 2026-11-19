USE recall_radar;
INSERT INTO topics (name, category, difficulty, created_at) VALUES
 ('Dijkstra algorithm', 'DSA', 4, NOW() - INTERVAL 12 DAY),
 ('SQL window functions', 'SQL', 3, NOW() - INTERVAL 9 DAY),
 ('React useEffect cleanup', 'Web', 3, NOW() - INTERVAL 6 DAY),
 ('Transformers attention', 'GenAI', 5, NOW() - INTERVAL 10 DAY),
 ('Normalization (3NF)', 'SQL', 2, NOW() - INTERVAL 4 DAY);
INSERT INTO reviews (topic_id, reviewed_at, confidence, notes) VALUES
 (1, NOW() - INTERVAL 11 DAY, 2, 'shaky on heap version'),
 (1, NOW() - INTERVAL 5 DAY, 4, 'solved 2 problems'),
 (2, NOW() - INTERVAL 8 DAY, 3, NULL),
 (2, NOW() - INTERVAL 1 DAY, 5, 'solid'),
 (3, NOW() - INTERVAL 5 DAY, 2, NULL),
 (5, NOW() - INTERVAL 2 DAY, 4, NULL);
