# Recall Radar

Flask + MySQL app that estimates how much you've forgotten, using an
exponential forgetting curve computed in a SQL view (`topic_retention`).

    retention = 100 * exp(-days_since_last_touch / stability)
    stability = 1 + (sum of review confidences * 1.5) / difficulty

## Run
    pip install -r requirements.txt
    mysql -u root -p < schema.sql
    mysql -u root -p < seed.sql        # optional demo data
    export DB_USER=root DB_PASSWORD=yourpass
    python app.py                      # http://127.0.0.1:5000

## SQL queries worth reading (in app.py)
1. Weakest memory first (view ORDER BY retention)
2. "Fading now" (retention < 60)
3. Category health (GROUP BY + conditional SUM)
4. 7-day study streak (date bucketing)
5. Confidence trend (correlated subqueries, first vs latest review)

CRUD: topics (create/edit/delete with cascade to reviews) and reviews (create).
