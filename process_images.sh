#!/bin/bash

LOCKFILE="/tmp/automated_b2b_api.lock"

if [ -f "$LOCKFILE" ]; then
    echo "Outro processo já está em execução. Encerrando process_images.sh..."
    exit 1
fi

trap "rm -f $LOCKFILE" EXIT
echo $$ > "$LOCKFILE"

echo "Iniciando processamento de imagens (sem bloqueados)..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST https://api.dominioexemplo.com/process-images/)
if [ "$response" -eq 200 ]; then
    echo "Processamento de imagens concluído com sucesso."
else
    echo "Erro ao processar imagens. Código HTTP: $response"
fi
