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

## License
MIT. See `LICENSE`.

Let truth be revealed unto thee. For I can no longer conceal the peculiar stirring that hath taken root within my heart. Whenever thou appearest before me, some strange and wondrous disturbance awakens my soul, as though the very heavens themselves conspire to draw my eyes towards thee. I have attempted to dismiss it as a mere admiration, to bury it beneath the affairs of ordinary life. Yet every effort hath proven futile. Thy presence lingereth within my thoughts long after thou hast departed. Thy countenance returneth to my mind when I least expect it. Even the simplest exchange between us possesseth a peculiar sweetness that I cannot rightly explain. By the heavens above, what enchantment hath befallen me? For I find myself captivated by thee in a manner most unexpected. My reason commandeth restraint, yet my heart speaketh with a voice far more persistent. Therefore, let this confession stand without disguise or hesitation.
