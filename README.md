# Recall Radar

A forgetting-curve tracker built with **Flask** and **MySQL**.

You log what you study and how confident you feel. Recall Radar estimates how much of each topic you have probably forgotten and tells you what to revise next.

## What it does

Most people study something once and then forget it. Recall Radar models that forgetting with a simple exponential curve, so you can see which topics are fading before they are gone.

- Add the topics you are learning, with a category and a difficulty from 1 to 5
- Log a review each time you revise a topic, with a confidence score from 1 to 5 and an optional note
- See an estimated **retention %** for every topic, weakest first
- Get a "fading now" list of topics that have dropped below 60%
- Track your progress with category health, a 7-day study streak and confidence trends

## Features

- Full CRUD for topics (create, edit, delete) and create for reviews
- Deleting a topic also deletes its reviews (`ON DELETE CASCADE`)
- Retention is calculated inside MySQL, in a view called `topic_retention`
- Dashboard built from five SQL queries
- Database password kept in a `.env` file, not in the code

## How retention is calculated

```
retention = 100 * exp(-days_since_last_touch / stability)
stability = 1 + (sum of review confidences * 1.5) / difficulty
```

- More reviews, and higher confidence, make `stability` larger, so the memory fades more slowly.
- Harder topics have a lower `stability`, so they fade faster.
- A topic with no reviews starts decaying from the day it was created.

This is a simplified model for learning and practice. It is not a scientifically calibrated spaced-repetition algorithm.

## Tech stack

- Python 3 and Flask
- MySQL 8+ (using `mysql-connector-python`)
- HTML templates (Jinja2)

## Setup

### 1. Clone the project

```
git clone https://github.com/adityamnaganur/recall-radar.git
cd recall-radar
```

### 2. Install the Python packages

```
pip install -r requirements.txt
```

### 3. Create the database

Log in to MySQL and load the schema and the optional demo data:

```
mysql -u root -p
```

```
source schema.sql;
source seed.sql;
```

`seed.sql` is optional. Run it only once, or you will get duplicate demo topics.

On macOS or Linux you can also run `mysql -u root -p < schema.sql` directly.

### 4. Add your database password

Copy the example settings file and put your MySQL password in it:

```
copy .env.example .env
```

On macOS or Linux use `cp .env.example .env`. Then open `.env` and edit it:

```
DB_USER=root
DB_PASSWORD=your_mysql_password
```

Optional settings: `DB_HOST` (default `localhost`), `DB_NAME` (default `recall_radar`) and `SECRET_KEY`.

### 5. Run the app

```
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Project structure

```
recall-radar/
├── app.py             # Flask routes and the five SQL queries
├── schema.sql         # Tables and the topic_retention view
├── seed.sql           # Optional demo data
├── requirements.txt   # Python dependencies
├── .env.example       # Template for your local .env
└── templates/
    └── index.html     # Dashboard page
```

## SQL queries used (in `app.py`)

1. **Weakest memory first**: reads the view and orders by `retention`
2. **Fading now**: topics with retention below 60%
3. **Category health**: `GROUP BY` with average retention and a conditional `SUM`
4. **7-day study streak**: reviews bucketed by day
5. **Confidence trend**: correlated subqueries comparing first and latest review

## Notes

- `app.run(debug=True)` is meant for local use only. Do not run it on a public server.
- Never commit your `.env` file. It is listed in `.gitignore`.