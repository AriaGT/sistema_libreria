Param(
    [string]$EnvPath,
    [switch]$CreateTables = $false,
    [string]$PythonExecutable = "python"
)

function Read-EnvFile {
    Param([string]$Path)

    if (-not (Test-Path -Path $Path)) {
        throw "El archivo .env no existe en la ruta: $Path"
    }

    $variables = @{}

    foreach ($line in Get-Content -Path $Path) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
        if ($trimmed.StartsWith("#")) { continue }

        $parts = $trimmed -split "=", 2
        if ($parts.Length -ne 2) { continue }

        $key = $parts[0].Trim()
        $value = $parts[1].Trim().Trim("'`"")
        $variables[$key] = $value
    }

    return $variables
}

function Ensure-CommandExists {
    Param([string]$CommandName)

    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        throw "No se encontro el comando requerido '$CommandName' en el PATH."
    }
}

$scriptPath = $PSCommandPath
if (-not $scriptPath) {
    $scriptPath = $MyInvocation.MyCommand.Path
}
if (-not $scriptPath) {
    throw "No se pudo determinar la ruta del script."
}
$scriptDir = Split-Path -Parent $scriptPath
$projectRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
if (-not $EnvPath) {
    $EnvPath = Join-Path $projectRoot ".env"
}

$envVars = Read-EnvFile -Path $EnvPath
$requiredKeys = @("DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME")

foreach ($key in $requiredKeys) {
    if (-not $envVars.ContainsKey($key) -or [string]::IsNullOrWhiteSpace($envVars[$key])) {
        throw "La variable $key es requerida en el archivo .env"
    }
}

$dbHost = $envVars["DB_HOST"]
$dbPort = $envVars["DB_PORT"]
$dbUser = $envVars["DB_USER"]
$dbPass = $envVars["DB_PASS"]
$dbName = $envVars["DB_NAME"]

Ensure-CommandExists -CommandName "psql"

Write-Host ("Validando conexion a PostgreSQL en {0}:{1} ..." -f $dbHost, $dbPort)

$env:PGPASSWORD = $dbPass

try {
    $psqlBaseArgs = @("-h", $dbHost, "-p", $dbPort, "-U", $dbUser, "-d", "postgres", "-v", "ON_ERROR_STOP=1")

    & psql @psqlBaseArgs "-tAc" "SELECT 1;" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "No fue posible conectar con PostgreSQL usando las credenciales proporcionadas."
    }

    Write-Host "Conexion exitosa. Verificando existencia de la base de datos '$dbName' ..."

    $dbExists = & psql @psqlBaseArgs "-tAc" "SELECT 1 FROM pg_database WHERE datname = '$dbName';"

    if ([string]::IsNullOrWhiteSpace($dbExists)) {
        Write-Host "La base de datos no existe. Creandola..."
        & psql @psqlBaseArgs "-c" "CREATE DATABASE $dbName;"
        if ($LASTEXITCODE -ne 0) {
            throw "No fue posible crear la base de datos '$dbName'."
        }
        Write-Host ("Base de datos '{0}' creada correctamente." -f $dbName)
    }
    else {
        Write-Host ("La base de datos '{0}' ya existe." -f $dbName)
    }

    if ($CreateTables) {
        Write-Host "Creando tablas a partir de los modelos SQLAlchemy..."
        Push-Location $projectRoot
        try {
            & $PythonExecutable "-c" "from app.database.connection import engine; from app.database.base import Base; import app.models  # noqa: F401; Base.metadata.create_all(bind=engine)"
            if ($LASTEXITCODE -ne 0) {
                throw "No fue posible crear las tablas mediante SQLAlchemy."
            }
        }
        finally {
            Pop-Location
        }
        Write-Host "Tablas creadas o actualizadas correctamente."
    }

    Write-Host "Configuracion de la base de datos completada."
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue | Out-Null
}
