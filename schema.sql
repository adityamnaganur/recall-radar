CREATE DATABASE IF NOT EXISTS recall_radar;
USE recall_radar;

CREATE TABLE IF NOT EXISTS topics (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120) NOT NULL,
    category    VARCHAR(60)  NOT NULL DEFAULT 'General',
    difficulty  TINYINT      NOT NULL DEFAULT 3,   -- 1 (easy) .. 5 (hard)
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_difficulty CHECK (difficulty BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS reviews (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    topic_id     INT         NOT NULL,
    reviewed_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confidence   TINYINT     NOT NULL,              -- 1 (blank) .. 5 (solid)
    notes        VARCHAR(255) NULL,
    CONSTRAINT fk_review_topic FOREIGN KEY (topic_id)
        REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT chk_confidence CHECK (confidence BETWEEN 1 AND 5),
    INDEX idx_reviews_topic_time (topic_id, reviewed_at)
);

-- Estimated retention per topic using an exponential forgetting curve:
--   retention = 100 * exp(-days_since_last_touch / stability)
--   stability = 1 + (sum of review confidences * 1.5) / difficulty
-- More (and more confident) reviews => slower decay. Harder topics decay faster.
CREATE OR REPLACE VIEW topic_retention AS
SELECT
    t.id,
    t.name,
    t.category,
    t.difficulty,
    COUNT(r.id)                                   AS review_count,
    COALESCE(MAX(r.reviewed_at), t.created_at)    AS last_touch,
    ROUND(
        TIMESTAMPDIFF(HOUR, COALESCE(MAX(r.reviewed_at), t.created_at), NOW()) / 24.0, 1
    )                                             AS days_since,
    ROUND(1 + COALESCE(SUM(r.confidence), 0) * 1.5 / t.difficulty, 2) AS stability,
    ROUND(100 * EXP(
        -(TIMESTAMPDIFF(HOUR, COALESCE(MAX(r.reviewed_at), t.created_at), NOW()) / 24.0)
        / (1 + COALESCE(SUM(r.confidence), 0) * 1.5 / t.difficulty)
    ), 1)                                         AS retention
FROM topics t
LEFT JOIN reviews r ON r.topic_id = t.id
GROUP BY t.id, t.name, t.category, t.difficulty, t.created_at;
