# Projeto: Persistência Poliglota (MongoDB + SQLite) com Geo-Processamento em Python e Streamlit

## Objetivo
Aplicação prática que combina SQLite e MongoDB para armazenar e consultar dados em diferentes contextos e implementa recursos de geoprocessamento com visualização em mapa.

## Arquitetura
- `SQLite` armazena estados e cidades.
- `MongoDB` armazena documentos JSON de locais com nome, cidade, coordenadas e descrição.
- Funções de geoprocessamento calculam distâncias e listam locais por raio.
- `Streamlit` fornece interface interativa para cadastro, consultas integradas e mapas.

## Estrutura
```
projeto_persistencia_poliglota/
├── app.py
├── db_sqlite.py
├── db_mongo.py
├── geoprocessamento.py
├── requirements.txt
└── README.md
```

## Requisitos
- Python 3.10+
- MongoDB local ou Atlas
- Pip

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

Caso tenha problemas use:
python -m pip install -r requirements.txt
```

## Execução
```bash
streamlit run app.py

Caso tenha problemas:
python -m streamlit run app.py
```
Ajuste as conexões na barra lateral:
- Caminho do arquivo SQLite (padrão: `data.sqlite3`)
- URI do MongoDB (padrão: `mongodb://localhost:27017`)
- Nome do banco no MongoDB (padrão: `poliglota`)

## Uso
1. Aba **Cidades e Estados**: cadastre estados e cidades; visualize as tabelas.
2. Aba **Locais**: cadastre locais no MongoDB escolhendo uma cidade do SQLite; visualize todos os locais.
3. Aba **Consulta Integrada**: selecione Estado e Cidade do SQLite e visualize os locais do MongoDB relacionados.
4. Aba **Proximidade**: informe uma coordenada e um raio em km para listar locais próximos e visualizar no mapa.
5. Aba **Mapa**: veja todos os locais plotados em um mapa interativo.

## Modelo de Documento no MongoDB
```json
{
  "nome_local": "Praça da Independência",
  "cidade": "João Pessoa",
  "coordenadas": {
    "latitude": -7.11532,
    "longitude": -34.861
  },
  "descricao": "Ponto turístico central da cidade."
}
```

## Exemplos
- Cadastrar estado `PB` e cidade `João Pessoa` no SQLite.
- Cadastrar local no MongoDB com as coordenadas da cidade.
- Usar **Consulta Integrada** para listar os locais da cidade.
- Usar **Proximidade** com raio de 10 km a partir de uma coordenada para ver locais próximos.

## Dicas
- Certifique-se de que o MongoDB está ativo. Para Atlas, copie a string de conexão como URI.
- Se desejar resetar os dados, apague o arquivo `data.sqlite3` e a coleção `locais` no MongoDB.

## Licença
MIT
