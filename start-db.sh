docker run --name indexor-db --rm \
  -v ./postgres:/var/lib/postgresql/data \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -e POSTGRES_DB=indexor \
  -e POSTGRES_USER=indexor \
  -e POSTGRES_PASSWORD=indexor \
  -d \
  -p 5432:5432 \
  --shm-size=1g \
  postgres:15-alpine
