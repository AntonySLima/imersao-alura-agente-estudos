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

import asyncio
import datetime

import pytest

from app.agent import (
    GCS_BUCKET_NAME,
    get_instruction,
    gcs_tool_settings,
    gcs_toolset,
    root_agent,
)
from google.adk.integrations.gcs.settings import Capabilities


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_root_agent_has_gcs_toolset():
    """O root_agent deve ter o GCSToolset entre suas ferramentas."""
    from google.adk.integrations.gcs.storage_toolset import GCSToolset

    toolset_types = [type(t) for t in root_agent.tools]
    assert GCSToolset in toolset_types, (
        f"GCSToolset não encontrado nas ferramentas do agente: {toolset_types}"
    )


def test_root_agent_does_not_have_environment_toolset():
    """O root_agent NÃO deve ter o EnvironmentToolset (substituído pelo GCS)."""
    toolset_names = [type(t).__name__ for t in root_agent.tools]
    assert "FerramentasDeArquivo" not in toolset_names
    assert "EnvironmentToolset" not in toolset_names


def test_gcs_tool_settings_has_read_write():
    """As configurações do GCS devem habilitar READ_WRITE."""
    assert Capabilities.READ_WRITE in gcs_tool_settings.capabilities


def test_gcs_toolset_exposes_only_create_and_get(event_loop):
    """O toolset filtrado deve expor apenas create_object e get_object_data."""
    tools = event_loop.run_until_complete(gcs_toolset.get_tools())
    tool_names = sorted([t.name for t in tools])
    assert tool_names == ["create_object", "get_object_data"], (
        f"Ferramentas inesperadas: {tool_names}"
    )


def test_gcs_toolset_does_not_expose_delete(event_loop):
    """delete_objects NÃO deve estar exposta ao agente."""
    tools = event_loop.run_until_complete(gcs_toolset.get_tools())
    tool_names = [t.name for t in tools]
    assert "delete_objects" not in tool_names


def test_instruction_contains_today_date():
    """A instrução do agente deve conter a data de hoje."""
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    instruction = get_instruction()
    assert hoje in instruction


def test_instruction_contains_bucket_name():
    """A instrução do agente deve mencionar o bucket GCS configurado."""
    instruction = get_instruction()
    assert GCS_BUCKET_NAME in instruction


def test_instruction_mentions_gcs_tools():
    """A instrução deve referenciar create_object e get_object_data."""
    instruction = get_instruction()
    assert "create_object" in instruction
    assert "get_object_data" in instruction
