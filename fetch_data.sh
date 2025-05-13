#!/bin/bash

# Bloqueia execução simultânea para evitar bugs
LOCKFILE="/tmp/automated_b2b_api.lock"

if [ -f "$LOCKFILE" ]; then
    echo "Outro processo já está em execução. Encerrando fetch_data.sh..."
    exit 1
fi

# Lock file
trap "rm -f $LOCKFILE" EXIT
echo $$ > "$LOCKFILE"

# Lógica
echo "Iniciando fetch de dados do fornecedor principal..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8000/fetch-data/)
if [ "$response" -eq 200 ]; then
    echo "Fetch de dados do fornecedor principal concluído com sucesso."
else
    echo "Erro ao executar o fetch de dados. Código HTTP: $response"
fi
