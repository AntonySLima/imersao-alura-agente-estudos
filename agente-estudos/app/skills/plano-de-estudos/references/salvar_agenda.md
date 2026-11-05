# Salvar a Agenda no Google Cloud Storage (GCSToolset)

O agente salva a agenda num arquivo CSV diretamente em um bucket do **Google Cloud Storage (GCS)** usando as ferramentas do **GCSToolset** do ADK ([adk.dev/integrations/gcs](https://adk.dev/integrations/gcs/)). A pessoa pode baixar o arquivo do bucket para importar no Google Agenda.

---

## Ferramentas disponíveis

| Ferramenta | Para que serve | Argumentos |
|---|---|---|
| `create_object` | Cria o objeto no bucket ou **sobrescreve** o objeto inteiro | `bucket_name` (texto), `object_name` (texto), `data` (texto) |
| `get_object_data` | Lê o conteúdo do objeto no bucket | `bucket_name` (texto), `object_name` (texto) |

Use **só** essas duas ferramentas para interações com o GCS. O CSV é sempre gravado ou sobrescrito inteiro, de uma vez, através do parâmetro `data`.

## Regras de bucket e objeto

* O nome do bucket padrão é informado na sua instrução inicial (ou fornecido pelo usuário).
* Use sempre o nome de objeto fixo `plano-de-estudos.csv`.
* No replanejamento, a versão nova substitui a anterior no mesmo bucket e com o mesmo nome de objeto.

## Como gravar a agenda

1. Monte o CSV completo seguindo as regras de `assets/plano_template.md`.
2. Antes de chamar a ferramenta, confira o checklist:
   - [ ] A primeira linha é exatamente `Subject,Start Date,Start Time,End Date,End Time,Description`.
   - [ ] Há uma linha por sessão, sem linhas em branco, e nenhuma sessão cai em dia que a pessoa não informou.
   - [ ] Datas em `MM/DD/YYYY` e horários em `HH:MM AM/PM`.
   - [ ] Toda `Description` está entre aspas duplas.
   - [ ] O conteúdo do parâmetro `data` **não** tem a cerca ```` ```csv ```` nem texto explicativo, só o CSV puro terminando com quebra de linha.
3. Chame `create_object` com `bucket_name` igual ao bucket configurado, `object_name` igual a `plano-de-estudos.csv` e `data` contendo a string CSV.

Exemplo de chamada:

```json
{
  "bucket_name": "plano-estudos-bucket",
  "object_name": "plano-de-estudos.csv",
  "data": "Subject,Start Date,Start Time,End Date,End Time,Description\n📚 Python: variáveis e entrada/saída,11/02/2026,08:00 PM,11/02/2026,09:00 PM,\"Revisão: — | Técnica: Aprender fazendo | Entregável: script de nome e idade\"\n"
}
```

## Como interpretar a resposta

| Resposta da ferramenta | O que fazer |
|---|---|
| `{"status": "SUCCESS", ...}` | Sucesso. Informe na seção 5 do template a URI `gs://<bucket_name>/plano-de-estudos.csv` e o número de sessões. |
| `{"status": "ERROR", "error_details": "..."}` | Ocorreu um erro (por exemplo, bucket não existe ou erro de permissão). Não insista. Explique resumidamente o motivo na seção 5 e mostre o CSV completo num bloco ```` ```csv ```` como fallback para o usuário. |

Nunca diga que salvou o arquivo no GCS sem ter recebido `"status": "SUCCESS"`.

## Replanejamento

1. Se precisar lembrar do plano atual gravado no GCS, chame `get_object_data` com `bucket_name` e `object_name` igual a `plano-de-estudos.csv`.
2. A resposta vem como `{"status": "SUCCESS", "data": "..."}` com o conteúdo em texto puro do CSV.
3. Se a resposta for erro (ex.: objeto não encontrado), monte o CSV a partir da tabela de sessões da conversa.
4. Monte o CSV novo **inteiro**, já com os ajustes, e grave chamando `create_object` no mesmo bucket e com o mesmo `object_name`. A versão anterior é substituída.
5. Na resposta, diga o que mudou e confirme que o arquivo no bucket foi atualizado.
