# CalFit — Dynamic Calisthenics Circuit Generator

A Flask-based calisthenics web application with a 0/1 Knapsack workout generator, exercise library, exercise detail pages, workout timer, account system and workout history.

## Run locally
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Set a strong `SECRET_KEY` environment variable before deployment.
5. Run `python app.py` and open http://127.0.0.1:5000.

The SQLite database is created and seeded automatically on first run.

## Notes
- Exercise calorie values and durations are illustrative estimates, not measurements.
- Exercise demonstration links open YouTube search results for the named movement. Replace them with reviewed video URLs before production.
- This is an educational MVP, not medical advice or a substitute for individualized coaching.
- Set `debug=False` and use a production WSGI server (such as Gunicorn) for deployment.
- login - Create account using valid email id and use it to login

## License
MIT. See `LICENSE`.
