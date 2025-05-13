   # Automated B2B API

   ## Descrição

   Este projeto é uma API modular e escalável desenvolvida com FastAPI e SQLAlchemy, projetada para automatizar a ingestão, normalização e gerenciamento de catálogos de produtos provenientes de múltiplas fontes. A solução suporta importações via APIs externas, arquivos CSV estruturados e integração com sistemas legados, aplicando enriquecimento de dados, classificação semântica baseada em embeddings, e processamento automatizado de imagens, com foco em aplicações B2B e e-commerce.

  A necessidade por essa arquitetura surgiu da limitação imposta pela plataforma B2B utilizada pelo cliente, que é operada por um terceiro e não oferece suporte nativo para gerenciamento eficiente de produtos ou customização de funcionalidades. Como alternativa, foi implementado um pipeline próprio de ingestão, com mapeamento de colunas adaptado às exigências da plataforma-alvo e comunicação direta via API, permitindo a sincronização centralizada e automática de produtos de diferentes fornecedores, mesmo sem acesso interno ao sistema principal.

   ### Melhorias e Alterações
   1. **Classificação de Família e Subfamília**:
      - Novo sistema de classificação automatizada baseado em palavras-chave nos títulos, marcas e categorias dos itens.
      - Suporte a várias famílias e subfamílias, incluindo acessórios, dispositivos móveis, computadores, entre outros.

   2. **Atributos de Produto**:
      - Introdução do campo `activated` com regras automáticas para ativação/desativação de itens:
      - Produtos sem estoque são automaticamente desativados.
      - Produtos com palavras-chave especificadas no código também são desativados (para preservar o segredo dos fornecedores).

   3. **Processamento de Imagens**:
      - Imagens são processadas com margens automáticas e convertidas para formato padronizado (JPG).
      - Melhor integração com sistemas FTP para upload de imagens processadas.

   4. **Melhorias no Banco de Dados**:
      - Otimizações nas tabelas e índices para suportar as novas funcionalidades.
      - Suporte a cálculos automáticos de preços B2C e B2B com margens configuráveis.

   5. **Endpoints Adicionados**:
      - `GET /dev/`: Retorna uma versão detalhada dos produtos, incluindo preços ajustados, família e subfamília.
      - `POST /process-images-ignore-conditions/`: Processa todas as imagens sem aplicar condições preexistentes.

   ### Correções de Bugs
   - Corrigido problema com classificação incorreta de itens.
   - Ajustado o processamento de imagens para lidar melhor com URLs inválidas.
   - Otimizações no upload FTP para lidar com conexões instáveis.

   ## Licença

   Este projeto está licenciado sob a MIT License.
