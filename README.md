# Sistema Libreria Escolar

Base API construida con FastAPI, SQLAlchemy y PostgreSQL para administrar usuarios, grados, secciones, cursos, libros y matriculas de estudiantes.

## Requisitos
- Python 3.10 o superior
- PostgreSQL disponible en `localhost`
- Cliente HTTP (curl, HTTPie, Postman, Bruno, etc.)

## Preparacion del entorno
1. Clonar el repositorio y ubicarse en la raiz del proyecto.
2. Crear y activar un entorno virtual (ejemplos):
   - PowerShell
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Bash
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configurar el archivo `.env` en la raiz:
   ```dotenv
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASS=root
   DB_NAME=school_db
   ```

## Provision automatica de la base de datos
Los scripts crean la base de datos si no existe y, opcionalmente, generan las tablas a partir de los modelos SQLAlchemy.

- PowerShell:
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/setup_db.ps1 -CreateTables -PythonExecutable .\.venv\Scripts\python.exe
  ```
- Bash:
  ```bash
  bash scripts/setup_db.sh --create-tables --python ./.venv/bin/python
  ```

Si no deseas crear las tablas en este paso, omite `-CreateTables` o `--create-tables`.

## Ejecucion del servidor
1. Asegurate de estar en el directorio `project/`.
2. Inicia FastAPI:
   ```bash
   uvicorn app.main:app --reload
   ```
3. La API quedara disponible en `http://127.0.0.1:8000`.
4. Documentacion interactiva: `http://127.0.0.1:8000/docs` (Swagger UI) y `http://127.0.0.1:8000/redoc`.

## Resumen de endpoints
| Recurso           | Metodo | Ruta                                    | Descripcion                               |
|-------------------|--------|-----------------------------------------|-------------------------------------------|
| Salud             | GET    | `/health`                               | Verifica que la aplicacion este activa    |
| Autenticacion     | POST   | `/auth/login`                           | Valida credenciales y retorna el usuario  |
| Usuarios          | GET    | `/users`                                | Lista usuarios                            |
|                   | GET    | `/users/{id}`                           | Obtiene un usuario                        |
|                   | POST   | `/users`                                | Crea usuario                              |
|                   | PATCH  | `/users/{id}`                           | Actualiza usuario                         |
|                   | DELETE | `/users/{id}`                           | Elimina usuario                           |
| Grados            | GET    | `/grades`                               | Lista grados                              |
|                   | GET    | `/grades/{id}`                          | Obtiene un grado                          |
|                   | POST   | `/grades`                               | Crea grado                                |
|                   | PATCH  | `/grades/{id}`                          | Actualiza grado                           |
|                   | DELETE | `/grades/{id}`                          | Elimina grado                             |
| Secciones         | GET    | `/grades/{grade_id}/sections`           | Lista secciones por grado                 |
|                   | POST   | `/grades/{grade_id}/sections`           | Crea seccion en un grado                  |
|                   | PATCH  | `/grades/{grade_id}/sections/{section_id}` | Actualiza una seccion                  |
|                   | DELETE | `/grades/{grade_id}/sections/{section_id}` | Elimina una seccion                    |
| Cursos            | GET    | `/sections/{section_id}/courses`        | Lista cursos por seccion                  |
|                   | POST   | `/sections/{section_id}/courses`        | Crea curso en una seccion                 |
|                   | PATCH  | `/sections/{section_id}/courses/{course_id}` | Actualiza un curso                    |
|                   | DELETE | `/sections/{section_id}/courses/{course_id}` | Elimina un curso                      |
| Libros            | GET    | `/courses/{course_id}/books`            | Lista libros por curso                    |
|                   | POST   | `/courses/{course_id}/books`            | Crea libro asociado a un curso            |
|                   | PATCH  | `/courses/{course_id}/books/{book_id}`  | Actualiza un libro                        |
|                   | DELETE | `/courses/{course_id}/books/{book_id}`  | Elimina un libro                          |
| Matriculas        | POST   | `/sections/{section_id}/enroll`         | Matricula a un estudiante en la seccion   |
|                   | GET    | `/sections/{section_id}/students`       | Lista estudiantes de la seccion           |
|                   | PATCH  | `/sections/{section_id}/enroll/{enrollment_id}` | Actualiza una matricula            |
|                   | DELETE | `/sections/{section_id}/enroll/{enrollment_id}` | Elimina una matricula              |

## Ejemplos de pruebas HTTP
Las siguientes muestras usan `http://127.0.0.1:8000` como base. Puedes copiarlas a Postman, Bruno u otro cliente para repetir el flujo tipico.

### 1. Crear usuario docente
- Metodo: `POST`
- Ruta: `/users`
- Request body:
  ```json
  {
    "full_name": "Ana Docente",
    "email": "ana.docente@example.com",
    "role": "teacher",
    "password": "secreto123"
  }
  ```
- Response body (201 Created):
  ```json
  {
    "full_name": "Ana Docente",
    "email": "ana.docente@example.com",
    "role": "teacher",
    "id": 1,
    "created_at": "2025-01-01T15:30:00+00:00"
  }
  ```

### 2. Crear usuario estudiante
- Metodo: `POST`
- Ruta: `/users`
- Request body:
  ```json
  {
    "full_name": "Juan Estudiante",
    "email": "juan.estudiante@example.com",
    "role": "student",
    "password": "secreto123"
  }
  ```
- Response body:
  ```json
  {
    "full_name": "Juan Estudiante",
    "email": "juan.estudiante@example.com",
    "role": "student",
    "id": 2,
    "created_at": "2025-01-01T15:31:00+00:00"
  }
  ```

### 3. Iniciar sesion
- Metodo: `POST`
- Ruta: `/auth/login`
- Request body:
  ```json
  {
    "email": "ana.docente@example.com",
    "password": "secreto123"
  }
  ```
- Response body:
  ```json
  {
    "message": "Login successful",
    "user": {
      "full_name": "Ana Docente",
      "email": "ana.docente@example.com",
      "role": "teacher",
      "id": 1,
      "created_at": "2025-01-01T15:30:00+00:00"
    }
  }
  ```

### 4. Crear grado
- Metodo: `POST`
- Ruta: `/grades`
- Request body:
  ```json
  {
    "name": "Primero de Secundaria"
  }
  ```
- Response body:
  ```json
  {
    "name": "Primero de Secundaria",
    "id": 1
  }
  ```

### 5. Crear seccion para el grado
- Metodo: `POST`
- Ruta: `/grades/1/sections`
- Request body:
  ```json
  {
    "name": "Seccion A"
  }
  ```
- Response body:
  ```json
  {
    "name": "Seccion A",
    "id": 1,
    "grade_id": 1
  }
  ```

### 6. Crear curso para la seccion
- Metodo: `POST`
- Ruta: `/sections/1/courses`
- Request body:
  ```json
  {
    "name": "Matematica I",
    "teacher_id": 1
  }
  ```
- Response body:
  ```json
  {
    "name": "Matematica I",
    "teacher_id": 1,
    "id": 1,
    "section_id": 1
  }
  ```

### 7. Registrar un libro para el curso
- Metodo: `POST`
- Ruta: `/courses/1/books`
- Request body:
  ```json
  {
    "title": "Algebra Basica",
    "author": "Maria Campos",
    "description": "Material introductorio de algebra.",
    "file_url": "https://example.com/libros/algebra.pdf",
    "category": "Matematica",
    "created_by": 1
  }
  ```
- Response body:
  ```json
  {
    "title": "Algebra Basica",
    "author": "Maria Campos",
    "description": "Material introductorio de algebra.",
    "file_url": "https://example.com/libros/algebra.pdf",
    "category": "Matematica",
    "course_id": 1,
    "id": 1,
    "created_by": 1,
    "created_at": "2025-01-01T15:35:00+00:00"
  }
  ```

### 8. Matricular estudiante en la seccion
- Metodo: `POST`
- Ruta: `/sections/1/enroll`
- Request body:
  ```json
  {
    "student_id": 2
  }
  ```
- Response body:
  ```json
  {
    "id": 1,
    "student_id": 2,
    "section_id": 1
  }
  ```

### 9. Consultar estudiantes de la seccion
- Metodo: `GET`
- Ruta: `/sections/1/students`
- Response body:
  ```json
  [
    {
      "full_name": "Juan Estudiante",
      "email": "juan.estudiante@example.com",
      "role": "student",
      "id": 2,
      "created_at": "2025-01-01T15:31:00+00:00"
    }
  ]
  ```

### 10. Consultar libros del curso
- Metodo: `GET`
- Ruta: `/courses/1/books`
- Response body:
  ```json
  [
    {
      "title": "Algebra Basica",
      "author": "Maria Campos",
      "description": "Material introductorio de algebra.",
      "file_url": "https://example.com/libros/algebra.pdf",
      "category": "Matematica",
      "course_id": 1,
      "id": 1,
      "created_by": 1,
      "created_at": "2025-01-01T15:35:00+00:00"
    }
  ]
  ```

Adapta los identificadores (`1`, `2`, etc.) y las fechas a los valores reales devueltos por tu base de datos.

## Notas adicionales
- Al registrar o actualizar usuarios envia el campo `password`; la API lo encripta y almacena en `password_hash` internamente (longitud maxima 72 bytes UTF-8).
- Los endpoints de actualizacion y eliminacion validan que los IDs de la ruta coincidan con los datos enviados y devuelven errores 400 si existen violaciones de integridad (claves foraneas, valores nulos o restricciones de unicidad) en lugar de errores 500.
- Para ejecutar pruebas repetidas, limpia las tablas manualmente o crea una base de datos temporal.
- Asegura que el usuario configurado en `.env` tenga permisos de creacion de base de datos y tablas.
