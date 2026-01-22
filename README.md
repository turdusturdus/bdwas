# BDWAS (Django + MongoDB)

## Start (Docker)
```bash
sudo docker-compose up --build
```

- App: http://localhost:8000
- Mongo: mongodb://localhost:27017
- DB: football_app

Mongo inicjalizuje się automatycznie przez:
- infra/mongo/init/01-schema.js
- infra/mongo/init/02-seed.js

## Backend danych
- mock: domyślnie (bez DB)
- mongo: w docker-compose.yml ustaw `DATA_BACKEND=mongo`

## Uwaga o ID
- URL-e używają 24-znakowego hex (Mongo ObjectId) np. `507f1f77bcf86cd799439011`

## Testy

### 1) Szybkie testy (mock / bez bazy)
```bash
sudo docker exec -it bdwas_web python manage.py test
```

### 2) Testy integracyjne na prawdziwym Mongo (tag=mongo)
```bash
sudo docker exec -it bdwas_web python manage.py test --tag=mongo -v 2
```

### 3) Oba zestawy po kolei
```bash
sudo docker exec -it bdwas_web python manage.py test_all -v 2
```

## Ważne: konflikt test discovery
Jeśli masz jednocześnie plik `core/tests.py` i katalog `core/tests/`, Django/unittest może rzucać ImportError.
Wtedy usuń/zmień nazwę pliku:
```bash
rm -f core/tests.py
```

## Uwaga: permission denied do docker.sock
Jeśli uruchamiasz `docker exec ...` bez `sudo` i masz błąd `permission denied`,
to używaj `sudo docker ...` albo dodaj usera do grupy `docker`.

## Benchmark wydajności baz danych

### Przygotowanie
1. Upewnij się, że kontenery baz danych są uruchomione w trybie odłączonym:
   ```bash
   docker compose up -d postgres mysql mongo
   ```

2. Sprawdź, czy bazy danych są gotowe do użycia:
   ```bash
   docker compose up -d postgres mysql mongo
   ```

### Uruchomienie benchmarku
Aby uruchomić benchmark porównujący wydajność baz danych, wykonaj poniższe polecenie:
```bash
docker compose exec web python bench.py > results.csv
```

Wyniki benchmarku zostaną wyświetlone w terminalu.
