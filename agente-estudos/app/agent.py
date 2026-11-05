# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from pathlib import Path
from typing import Optional

from google.adk.agents import Agent
from google.adk.agents.context import ReadonlyContext
from google.adk.apps import App
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import Capabilities, GCSToolSettings
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

MODEL = os.getenv("MODEL", "gemini-3.8-flash")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "plano-estudos-bucket")

BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
plano_skill = load_skill_from_dir(SKILLS_DIR / "plano-de-estudos")

gcs_tool_settings = GCSToolSettings(capabilities=[Capabilities.READ_WRITE])
gcs_toolset = GCSToolset(
    tool_filter=["create_object", "get_object_data"],
    gcs_tool_settings=gcs_tool_settings,
)


def get_instruction(ctx: Optional[ReadonlyContext] = None) -> str:
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    dias_semana = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]
    dia_nome = dias_semana[datetime.date.today().weekday()]
    return (
        f"Você é um mentor de estudos especialista. "
        f"A data de hoje é {hoje} ({dia_nome}). "
        f"Use sempre esta data como referência para planejar prazos e cronogramas. "
        f"Siga a skill plano-de-estudos para criar planos personalizados, "
        f"aplicar revisão espaçada, checkpoints e gerar a agenda em arquivo CSV. "
        f"Para salvar e consultar a agenda em formato CSV, utilize o bucket do Google Cloud Storage: '{GCS_BUCKET_NAME}' "
        f"e o arquivo 'plano-de-estudos.csv'. Use a ferramenta create_object para salvar ou atualizar o arquivo no bucket, "
        f"e get_object_data para ler o arquivo existente caso precise replanejar."
    )


root_agent = Agent(
    name="agente_estudos",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=get_instruction,
    tools=[
        SkillToolset(skills=[plano_skill]),
        gcs_toolset,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
