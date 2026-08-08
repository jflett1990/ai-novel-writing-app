"""End-to-end API pipeline tests using a deterministic AI provider."""

from typing import AsyncGenerator, Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import services.enhanced_generation_service as enhanced_generation_module
import services.generation_service as generation_module
from app import app
from db.database import Base, get_db
from models.chapter import ChapterRevision
from services.ai_providers.base import AIProvider, GenerationParams, GenerationResult


class DeterministicProvider(AIProvider):
    """Small fake that emits valid fixtures based on the prompt contract."""

    def __init__(self):
        super().__init__({})
        self.prompts: list[str] = []

    async def generate_text(
        self,
        prompt: str,
        params: Optional[GenerationParams] = None,
    ) -> GenerationResult:
        del params
        self.prompts.append(prompt)

        if "FORMAT YOUR RESPONSE EXACTLY AS:" in prompt and "ACT I:" in prompt:
            text = """ACT I: The Broken Map
The siblings discover that the city's official maps have been quietly altered.

Chapter 1: The Missing Street
Mara follows a delivery address into a district absent from every current map and meets Ivo there.

Chapter 2: Ink Under Glass
Mara and Ivo compare the old map with city records and realize someone is erasing routes on purpose.
"""
        elif "fully developed characters" in prompt:
            text = """1. Mara Vale
Role: protagonist
Age: 29
Appearance: ink-stained fingers and a silver tooth
Personality: skeptical, loyal, impatient
Background: municipal archivist from the river ward
Motivation: protect her brother and expose the altered maps
Conflict: distrusts anyone who offers easy certainty
Skills/Talents: archival research and lock repair
Relationships: older sister of Ivo
Unique Element: memorizes street grids as music
Character Arc: learns to share incomplete truths instead of carrying them alone

2. Ivo Vale
Role: supporting character
Age: 24
Appearance: red scarf and a permanent squint
Personality: curious, funny, stubborn
Background: bicycle courier
Motivation: prove the vanished district still exists
Conflict: turns danger into a joke until it becomes unavoidable
Skills/Talents: navigation and improvisation
Relationships: younger brother of Mara
Unique Element: keeps discarded address labels
Character Arc: becomes deliberate without losing his curiosity
"""
        elif "world building elements" in prompt and "*Type:" in prompt:
            text = """1. Glass District
*Type: location
*Description: A riverfront neighborhood whose street signs are replaced each dawn.
*Significance: It is the physical evidence that the city archive has been falsified.
*Details: Mirrored awnings make old building numbers visible from oblique angles.
*Story Impact: Mara must enter it to recover the original survey ledger.

2. Registry Office
*Type: organization
*Description: A municipal bureau that certifies every legal address in the city.
*Significance: Its records decide which homes officially exist.
*Details: Corrections require three independent paper ledgers.
*Story Impact: Ivo discovers one ledger has been replaced.
"""
        elif "EXPANSION TYPE:" in prompt:
            text = (
                "Rain pressed a silver grid against the archive windows. "
                "Mara unfolded the copied survey twice, then once more. "
                "\"The street is here,\" Ivo said. \"They just taught the city not to see it.\"\n\n"
                "She traced the old route with an ink-stained finger and heard the tram turn outside. "
                "The rails made the same three-note pattern she remembered from childhood."
            )
        elif "ADVANCED CHAPTER COMPOSITION DIRECTIVE:" in prompt:
            text = (
                "Mara set the old map beneath the registry lamp. CONTINUITY-MARKER-GLASS-DISTRICT "
                "appeared in the margin where no modern survey admitted a street.\n\n"
                "\"Read it again,\" Ivo said. \"Slowly this time.\"\n\n"
                "She did, and the erased route became a choice instead of a rumor."
            )
        elif "CURRENT CHAPTER TO WRITE:" in prompt:
            text = (
                "Mara found the vanished street just after dusk. CONTINUITY-MARKER-GLASS-DISTRICT "
                "glimmered on an old enamel sign above the rain.\n\n"
                "\"You took your time,\" Ivo said from beneath a mirrored awning.\n\n"
                "She looked back at the blank space on her new map and stepped across it anyway."
            )
        elif "CHAPTER STRUCTURE GENERATION - PASS 1" in prompt:
            text = "Scene 1: archive discovery. Scene 2: confrontation at the registry."
        elif "CHARACTER DEVELOPMENT ENHANCEMENT - PASS 2" in prompt:
            text = "Mara and Ivo argue over whether exposing the ledger will put their neighbors at risk."
        elif "PROSE REFINEMENT AND EXPANSION - PASS 3" in prompt:
            text = "Mara closed the ledger. \"We copy it first,\" she said. Ivo finally stopped smiling."
        else:
            text = "Deterministic generated text."

        return GenerationResult(
            text=text,
            tokens_used=42,
            model_used="deterministic-test-model",
            finish_reason="stop",
            metadata={},
        )

    async def generate_text_stream(
        self,
        prompt: str,
        params: Optional[GenerationParams] = None,
    ) -> AsyncGenerator[str, None]:
        del params
        self.prompts.append(prompt)
        yield "Streamed prose begins. "
        yield "The map still remembers the missing street."

    async def is_available(self) -> bool:
        return True

    def get_model_info(self):
        return {"name": "deterministic-test-model", "provider": "test"}


@pytest.fixture()
def pipeline_client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    provider = DeterministicProvider()
    monkeypatch.setattr(generation_module, "create_ai_provider", lambda: provider)
    monkeypatch.setattr(enhanced_generation_module, "create_ai_provider", lambda: provider)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client, TestingSession, provider
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_complete_novel_pipeline(pipeline_client):
    client, TestingSession, provider = pipeline_client

    assert client.get("/health").json() == {"status": "healthy"}
    features = client.get("/api/v1/features")
    assert features.status_code == 200
    assert features.json()["enhanced_generation"] is True

    world_types = client.get("/api/v1/world/types")
    assert world_types.status_code == 200
    assert "location" in world_types.json()["types"]

    created = client.post(
        "/api/v1/stories/",
        json={
            "title": "The Cartographer's Error",
            "description": "Two siblings uncover a city that edits itself out of public records.",
            "genre": "Mystery",
            "target_chapters": 2,
            "target_word_count": 3000,
        },
    )
    assert created.status_code == 200
    story_id = created.json()["story_id"]

    outline = client.post(
        f"/api/v1/generate/stories/{story_id}/outline",
        json={"target_chapters": 2},
    )
    assert outline.status_code == 200
    assert outline.json()["success"] is True
    assert len(outline.json()["outline"]["chapters"]) == 2

    characters = client.post(
        f"/api/v1/generate/stories/{story_id}/characters",
        json={"character_count": 2, "custom_prompt": "Make the siblings disagree about risk."},
    )
    assert characters.status_code == 200
    assert characters.json()["success"] is True
    assert len(characters.json()["characters"]) == 2

    world = client.post(f"/api/v1/generate/stories/{story_id}/world?element_count=2")
    assert world.status_code == 200
    assert world.json()["success"] is True
    persisted_world = client.get(f"/api/v1/world/story/{story_id}")
    assert persisted_world.status_code == 200
    assert {item["name"] for item in persisted_world.json()} == {"Glass District", "Registry Office"}
    assert persisted_world.json()[0]["meta"]["significance"]

    chapter_one = client.post(
        f"/api/v1/generate/stories/{story_id}/chapters/1",
        json={},
    )
    assert chapter_one.status_code == 200
    assert chapter_one.json()["success"] is True
    assert "CONTINUITY-MARKER-GLASS-DISTRICT" in chapter_one.json()["chapter_content"]

    prompts_before_blocked_outline = len(provider.prompts)
    blocked_outline = client.post(
        f"/api/v1/generate/stories/{story_id}/outline",
        json={"target_chapters": 2},
    )
    assert blocked_outline.status_code == 409
    assert len(provider.prompts) == prompts_before_blocked_outline

    enhanced = client.post(
        f"/api/v1/generate-enhanced/stories/{story_id}/chapters/2",
        json={"target_word_count": 1500, "quality_check": False},
    )
    assert enhanced.status_code == 200
    assert enhanced.json()["success"] is True
    assert any(
        "Closing prose excerpt:" in prompt and "CONTINUITY-MARKER-GLASS-DISTRICT" in prompt
        for prompt in provider.prompts
    )

    quality = client.post(
        f"/api/v1/generate-enhanced/stories/{story_id}/chapters/2/analyze-quality"
    )
    assert quality.status_code == 200
    assert 0.0 <= quality.json()["quality_score"] <= 1.0
    assert isinstance(quality.json()["suggestions"], list)

    expanded = client.post(
        f"/api/v1/generate/stories/{story_id}/chapters/2/expand",
        json={"expansion_type": "detail", "target_length": 1800},
    )
    assert expanded.status_code == 200
    assert expanded.json()["success"] is True
    assert expanded.json()["expanded_word_count"] > 0

    with TestingSession() as db:
        assert db.query(ChapterRevision).count() == 1

    story_list = client.get("/api/v1/stories/")
    assert story_list.status_code == 200
    summary = next(item for item in story_list.json() if item["story_id"] == story_id)
    assert len(summary["chapters"]) == 2
    assert summary["total_word_count"] > 0

    export_preview = client.get(
        f"/api/v1/export/stories/{story_id}/export/preview?format=markdown"
    )
    assert export_preview.status_code == 200
    assert "# The Cartographer's Error" in export_preview.json()["content"]
    assert "## Chapter 2: Ink Under Glass" in export_preview.json()["content"]


def test_streaming_and_full_draft_use_real_provider_and_fresh_session(pipeline_client):
    client, _, _ = pipeline_client

    created = client.post(
        "/api/v1/stories/",
        json={
            "title": "Streaming Test",
            "description": "A compact pipeline fixture.",
            "target_chapters": 2,
            "target_word_count": 3000,
        },
    )
    story_id = created.json()["story_id"]
    assert client.post(
        f"/api/v1/generate/stories/{story_id}/outline",
        json={"target_chapters": 2},
    ).status_code == 200

    with client.stream(
        "POST",
        f"/api/v1/generate/stories/{story_id}/chapters/1?stream=true",
        json={},
    ) as response:
        stream_text = "".join(response.iter_text())
    assert response.status_code == 200
    assert '"type": "content"' in stream_text
    assert "Streamed prose begins" in stream_text

    draft_story = client.post(
        "/api/v1/stories/",
        json={
            "title": "Background Draft Test",
            "description": "Verify the background task owns its DB session.",
            "target_chapters": 2,
            "target_word_count": 3000,
        },
    ).json()
    started = client.post(f"/api/v1/generate/stories/{draft_story['story_id']}/full-draft")
    assert started.status_code == 200

    detail = client.get(f"/api/v1/stories/{draft_story['story_id']}")
    assert detail.status_code == 200
    assert len(detail.json()["chapters"]) == 2
    assert all(chapter["is_generated"] for chapter in detail.json()["chapters"])
