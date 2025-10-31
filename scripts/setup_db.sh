#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${PROJECT_ROOT}/.env"
PYTHON_EXECUTABLE="${PYTHON_EXECUTABLE:-python}"
CREATE_TABLES="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file=*)
      ENV_FILE="${1#*=}"
      shift
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --python=*)
      PYTHON_EXECUTABLE="${1#*=}"
      shift
      ;;
    --python)
      PYTHON_EXECUTABLE="$2"
      shift 2
      ;;
    --create-tables)
      CREATE_TABLES="true"
      shift
      ;;
    *)
      ENV_FILE="$1"
      shift
      ;;
  esac
done

if [[ ! -f "$ENV_FILE" ]]; then
  echo "No se encontro el archivo .env en: $ENV_FILE" >&2
  exit 1
fi

declare -A env_vars
while IFS= read -r line || [[ -n "$line" ]]; do
  trimmed="$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  [[ -z "$trimmed" || "${trimmed:0:1}" == "#" ]] && continue
  IFS='=' read -r key value <<<"$trimmed"
  key="$(echo "$key" | xargs)"
  value="$(echo "$value" | xargs)"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  env_vars["$key"]="$value"
done < "$ENV_FILE"

required_vars=(DB_HOST DB_PORT DB_USER DB_PASS DB_NAME)
for key in "${required_vars[@]}"; do
  if [[ -z "${env_vars[$key]:-}" ]]; then
    echo "La variable $key es requerida en el archivo .env" >&2
    exit 1
  fi
done

DB_HOST="${env_vars[DB_HOST]}"
DB_PORT="${env_vars[DB_PORT]}"
DB_USER="${env_vars[DB_USER]}"
DB_PASS="${env_vars[DB_PASS]}"
DB_NAME="${env_vars[DB_NAME]}"

if ! command -v psql >/dev/null 2>&1; then
  echo "No se encontro el comando 'psql' en el PATH." >&2
  exit 1
fi

echo "Validando conexion a PostgreSQL en ${DB_HOST}:${DB_PORT} ..."
if ! PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -v "ON_ERROR_STOP=1" -tAc "SELECT 1;" >/dev/null; then
  echo "No fue posible conectar con PostgreSQL usando las credenciales proporcionadas." >&2
  exit 1
fi

echo "Conexion exitosa. Verificando existencia de la base de datos '${DB_NAME}' ..."
db_exists="$(PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -v "ON_ERROR_STOP=1" -tAc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}';" | tr -d '[:space:]')"

if [[ -z "$db_exists" ]]; then
  echo "La base de datos no existe. Creandola..."
  if ! PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -v "ON_ERROR_STOP=1" -c "CREATE DATABASE ${DB_NAME};"; then
    echo "No fue posible crear la base de datos '${DB_NAME}'." >&2
    exit 1
  fi
  echo "Base de datos '${DB_NAME}' creada correctamente."
else
  echo "La base de datos '${DB_NAME}' ya existe."
fi

if [[ "${CREATE_TABLES,,}" == "true" ]]; then
  echo "Creando tablas a partir de los modelos SQLAlchemy..."
  (
    cd "$PROJECT_ROOT"
    "$PYTHON_EXECUTABLE" -c "from app.database.connection import engine; from app.database.base import Base; import app.models  # noqa: F401; Base.metadata.create_all(bind=engine)"
  )
  echo "Tablas creadas o actualizadas correctamente."
fi

echo "Configuracion de la base de datos completada."
