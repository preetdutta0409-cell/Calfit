# CalFit: free deployment (Render + Neon)

## What this package changes
- Uses `DATABASE_URL` when supplied, while keeping SQLite for local development.
- Adds Gunicorn and the PostgreSQL Psycopg driver.
- Includes a Render Blueprint and Procfile.
- Does not include your local virtual environment or local SQLite database.

## Deployment overview
1. Create a free Neon PostgreSQL project and copy its pooled or direct connection string. Use the connection string shown by Neon; it should include SSL settings. Do not publish it.
2. Push this folder to a GitHub repository.
3. In Render, create a new Blueprint or Web Service connected to that repository.
4. Use Python runtime, build command `pip install -r requirements.txt`, and start command `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`.
5. Add `DATABASE_URL` using the Neon connection string. Add `SECRET_KEY` as a long random value. Set both as secret environment variables in Render.
6. Deploy and open the `onrender.com` URL.

## Important
- Render free web services sleep after 15 minutes without traffic and may take around a minute to wake.
- The Render filesystem is ephemeral. Do not use local SQLite for production on Render.
- Back up your Neon database periodically. Free-plan quotas and policies can change.
- This deploy creates a fresh database and seeds the built-in exercise catalogue. Existing users/workout history in a local `calfit.db` are not automatically migrated.
