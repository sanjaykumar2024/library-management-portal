#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "📦 Installing project dependencies..."
pip install -r requirements.txt

echo "🎨 Collecting static assets with WhiteNoise..."
python manage.py collectstatic --noinput

echo "🗄️ Applying database migrations..."
python manage.py migrate

echo "📚 Populating complete library catalog (173 books, 378 copies, covers & e-books)..."
python populate_expanded_library.py || python manage.py loaddata data/complete_library_fixture.json

echo "🎨 Generating book covers for all 173 books..."
python manage.py regenerate_book_covers

echo "✅ Build completed successfully!"
