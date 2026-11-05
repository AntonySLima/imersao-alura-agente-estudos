# AGENTS.md: Agente de Estudos

## Goal

Construir o **`agente-estudos`**: um agente **Google ADK** (Python) movido a skills, que monta planos de estudo personalizados a partir da skill `skills/plano-de-estudos/`. O plano inclui revisão espaçada, checkpoints de autoavaliação e uma agenda em CSV que pode ser importada no Google Agenda. O agente salva essa agenda diretamente em um bucket do **Google Cloud Storage (GCS)** com o **GCSToolset** do ADK e roda localmente no **ADK Web**.

## Context

* **Quem é você:** um engenheiro de software especialista em IA, fazendo pair programming com quem está desenvolvendo o agente. Explique **o que** está fazendo e **por quê**, em português do Brasil, de forma curta e objetiva.
* **Ambiente:** Google Cloud Shell. O `agy` roda na raiz do repositório, e o projeto do agente fica em `./agente-estudos/`, criado com as convenções do **agents-cli**.
* **Skills do ADK** ([adk.dev/skills](https://adk.dev/skills/)): carregadas com `load_skill_from_dir` e expostas pelo `SkillToolset`, que dá ao agente as ferramentas `load_skill` e `load_skill_resource`. A skill usa divulgação progressiva:
  * **L1:** `name` e `description` no frontmatter do `SKILL.md`.
  * **L2:** o corpo do `SKILL.md`, com a regra de gating.
  * **L3:** `references/workflow.md`, `references/tecnicas.md`, `references/salvar_agenda.md`, `assets/plano_template.md` e `assets/exemplo_plano.md`.
* **GCSToolset** ([adk.dev/integrations/gcs](https://adk.dev/integrations/gcs/)): dá ao agente ferramentas de Cloud Storage (`create_object`, `get_object_data`) configurado com `Capabilities.READ_WRITE`. O agente usa `create_object` para gravar `plano-de-estudos.csv` no bucket configurado (`GCS_BUCKET_NAME`) e `get_object_data` para conferir o arquivo antes de reescrever no replanejamento.
* **Regra de gating da skill:** sem **objetivo**, **prazo**, **disponibilidade** e **nível atual**, o agente pergunta só o que falta e não carrega nenhum recurso L3. Com tudo em mãos, ele segue o `workflow.md` até entregar o plano no formato do `plano_template.md` e salvar o CSV com `create_object`.
* **Autenticação local:** API Key do Google AI Studio no arquivo `agente-estudos/.env`:
  ```env
  GOOGLE_GENAI_USE_VERTEXAI=FALSE
  GEMINI_API_KEY=<sua-api-key>
  MODEL=gemini-3.8-flash
  GCS_BUCKET_NAME=antony-agente-estudos
  ```
* **Execução local:**
  ```bash
  cd agente-estudos
  uv run adk web --allow_origins="*"   # libera o proxy do Web Preview do Cloud Shell
  ```

## Constraints

* **Framework:** use só o **Google ADK** em Python, seguindo a especificação de ADK Skills (`load_skill_from_dir` + `SkillToolset`).
* **Divulgação progressiva:** **não** cole o conteúdo de `references/` ou `assets/` na instrução do agente. O conteúdo deve ser carregado sob demanda pelas ferramentas da skill.
* **Empacotamento da skill:** copie `skills/plano-de-estudos/` para `agente-estudos/app/skills/plano-de-estudos/`, porque o ADK resolve o caminho a partir do `agent.py`. A pasta precisa ter **exatamente** o nome do campo `name` do frontmatter. Ao alterar uma skill, mantenha as duas cópias sincronizadas.
* **Ferramentas de armazenamento:** use `GCSToolset(tool_filter=["create_object", "get_object_data"], gcs_tool_settings=GCSToolSettings(capabilities=[Capabilities.READ_WRITE]))`.
* **Modelo e Bucket:** leia o modelo da variável de ambiente `MODEL` (padrão `gemini-3.8-flash`) e o bucket de `GCS_BUCKET_NAME`. Não deixe esses valores fixos no código.
* **Data atual:** injete a data de hoje na instrução do agente, via *instruction provider* do ADK, para que ele entenda expressões como "segunda que vem".
* **Segredos:** **nunca** versione o `.env` nem a pasta `planos/` nem escreva a API Key em código, README, testes ou logs.
* **Dependências:** gerencie com `uv` dentro de `agente-estudos/` (`uv sync`).
* **Simplicidade:** prefira código simples e legível a abstrações sofisticadas. Confirme o entendimento do pedido antes de gerar muito código.
* **Fora de escopo:** deploy no Agent Runtime, Gemini Enterprise e infraestrutura (Terraform, CI/CD). Não gere esses artefatos, a menos que isso seja pedido explicitamente.

## Done-when

- [x] `agente-estudos/app/agent.py` define um `root_agent` com o `SkillToolset` carregando `app/skills/plano-de-estudos` e o `GCSToolset` expondo só `create_object` e `get_object_data`.
- [x] O modelo vem da variável `MODEL`, o bucket de `GCS_BUCKET_NAME`, e a instrução do agente contém a data de hoje e as orientações para o GCS.
- [x] `uv sync` e `uv run adk web --allow_origins="*"` rodam sem erros, e o agente `app` aparece no ADK Web.
- [x] **Gating:** com a mensagem "Quero organizar meus estudos de JavaScript.", o agente pede só as informações que faltam e **não** chama `load_skill_resource`.
- [x] **Plano completo:** com todas as informações, o agente carrega `workflow.md`, `tecnicas.md`, `plano_template.md` e `salvar_agenda.md`, entrega módulos, cronograma e checkpoints e chama `create_object`, criando `plano-de-estudos.csv` no bucket do Google Cloud Storage com um CSV válido para importação no Google Agenda.
- [x] **Replanejamento:** quando o usuário informa sessões perdidas, o agente lê o plano com `get_object_data`, devolve a tabela atualizada e sobrescreve o `plano-de-estudos.csv` no bucket com `create_object`, sem empilhar o conteúdo atrasado em um único dia.
- [x] Nenhum `.env`, API Key ou arquivo de `planos/` aparece em `git status` nem em arquivos versionados.