import asyncio
import inspect
import json
from types import SimpleNamespace

from backend.core import ai_service
from backend.models.ai_models import AIModel
from backend.models.resume_models import TailoredCoverLetter
from backend.utils import prompts
from backend.utils.writing_quality import find_writing_quality_issues


def _completion(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class _SequencedCompletions:
    def __init__(self, *contents: str):
        self.contents = iter(contents)
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return _completion(next(self.contents))


class _SequencedAsyncCompletions(_SequencedCompletions):
    async def parse(self, **kwargs):
        self.calls.append(kwargs)
        return _completion(next(self.contents))


def test_quality_check_reads_structured_response_values():
    payload = json.dumps(
        {
            "tailored_answer": (
                "Certainly, here is the answer — it not only showcases ‘delivery’ 🚀 "
                "but also underscores impact. [Your Name] [cite: 2]"
            )
        }
    )

    assert find_writing_quality_issues(payload) == [
        "an internal citation or tool marker",
        "placeholder text",
        "an em dash",
        "curly quotation marks",
        "emoji or decorative symbols",
        "a canned opening",
        "stock promotional or AI wording",
        "a formulaic contrast",
    ]


def test_quality_check_does_not_penalize_specific_plain_prose():
    payload = json.dumps(
        {
            "tailored_answer": (
                "I maintained Python deployment pipelines at Acme from 2019 to 2026. "
                "That work included PostgreSQL releases and CI/CD for backend services."
            )
        }
    )

    assert find_writing_quality_issues(payload) == []


def test_quality_check_does_not_treat_identifiers_as_prose_formatting():
    payload = json.dumps(
        {
            "personal_info": {"name": "Pivotal", "github": "ada__dev"},
            "tailored_answer": "I maintained the release pipeline.",
        }
    )

    assert find_writing_quality_issues(payload) == []


def test_structured_generation_gets_one_focused_repair_pass(monkeypatch):
    first = json.dumps(
        {"tailored_coverletter": "I am excited to apply — this role is pivotal."}
    )
    corrected = json.dumps(
        {
            "tailored_coverletter": (
                "Dear Hiring Team,\n\nI built Python delivery pipelines at Acme."
            )
        }
    )
    fake = _SequencedCompletions(first, corrected)
    monkeypatch.setattr(
        ai_service,
        "client",
        SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=fake))),
    )

    content = ai_service._parse_with_quality_review(
        model="test-model",
        messages=[{"role": "system", "content": "Write a cover letter."}],
        response_format=TailoredCoverLetter,
    )

    assert content == corrected
    assert len(fake.calls) == 2
    retry_messages = fake.calls[1]["messages"]
    assert retry_messages[-2] == {"role": "assistant", "content": first}
    assert "an em dash" in retry_messages[-1]["content"]
    assert "a canned opening" in retry_messages[-1]["content"]
    assert "Preserve every supported fact" in retry_messages[-1]["content"]


def test_async_resume_generation_gets_the_same_repair_pass(monkeypatch):
    first = json.dumps(
        {"personal_info": {"name": "Ada"}, "summary": "A pivotal role — delivered."}
    )
    corrected = json.dumps(
        {"personal_info": {"name": "Ada"}, "summary": "Delivered the release."}
    )
    fake = _SequencedAsyncCompletions(first, corrected)
    monkeypatch.setattr(
        ai_service,
        "async_client",
        SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=fake))),
    )

    content = asyncio.run(
        ai_service._parse_with_quality_review_async(
            model="test-model",
            messages=[{"role": "system", "content": "Edit the resume."}],
            response_format=ai_service.StructuredResume,
        )
    )

    assert content == corrected
    assert len(fake.calls) == 2
    assert "stock promotional or AI wording" in fake.calls[1]["messages"][-1]["content"]


def test_all_application_writing_system_prompts_share_the_standard():
    system_prompts = (
        prompts.RESUME_SYSTEM_PROMPT,
        prompts.COVER_LETTER_SYSTEM_PROMPT,
        prompts.APPLICATION_ANSWER_SYSTEM_PROMPT,
    )

    for system_prompt in system_prompts:
        assert "Every factual claim must be supported" in system_prompt
        assert "Do not force groups of three" in system_prompt
        assert "Do not use em dashes or curly quotation marks" in system_prompt
        assert "Do not use Markdown" in system_prompt
        assert "Never mention AI" in system_prompt


def test_application_writing_defaults_to_the_higher_quality_model():
    writing_functions = (
        ai_service.generate_structured_latex_resume_async,
        ai_service.generate_tailored_coverletter_text,
        ai_service.generate_answer_questions,
        ai_service.update_resume_with_instructions,
        ai_service.update_cover_letter_with_instructions,
        ai_service.update_answer_with_instructions,
    )

    for function in writing_functions:
        assert (
            inspect.signature(function).parameters["model"].default
            == AIModel.gpt_4_1_mini
        )


def test_generation_and_editing_paths_use_the_shared_system_prompts(monkeypatch):
    fake = _SequencedCompletions(
        json.dumps({"tailored_coverletter": "Dear Hiring Team,\n\nSpecific letter."}),
        json.dumps({"tailored_answer": "A direct, supported answer."}),
        json.dumps({"tailored_coverletter": "Dear Hiring Team,\n\nRevised letter."}),
        json.dumps({"tailored_answer": "A revised, supported answer."}),
    )
    monkeypatch.setattr(
        ai_service,
        "client",
        SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=fake))),
    )

    ai_service.generate_tailored_coverletter_text("resume", "job")
    ai_service.generate_answer_questions("resume", "job", "question")
    ai_service.update_cover_letter_with_instructions(
        "letter", "resume", "job", "shorten it"
    )
    ai_service.update_answer_with_instructions(
        "answer", "question", "job", "resume", "shorten it"
    )

    assert [call["messages"][0]["content"] for call in fake.calls] == [
        prompts.COVER_LETTER_SYSTEM_PROMPT,
        prompts.APPLICATION_ANSWER_SYSTEM_PROMPT,
        prompts.COVER_LETTER_SYSTEM_PROMPT,
        prompts.APPLICATION_ANSWER_SYSTEM_PROMPT,
    ]


def test_resume_prompt_forbids_the_old_hallucination_paths():
    prompt = prompts.structured_resume_prompt

    assert "Never add inferred skills" in prompt
    assert "Never create a metric" in prompt
    assert "outside knowledge" in prompt
    assert "Do not complete partial records from memory" in prompt
    assert "present them as factual" not in prompt
    assert "publicly available information" not in prompt
    assert "Quantifies impact wherever possible" not in prompt


def test_source_material_is_delimited_from_instructions():
    generation_prompts = (
        prompts.structured_resume_prompt,
        prompts.create_tailored_coverletter_prompt,
        prompts.answer_application_question,
    )

    for prompt in generation_prompts:
        assert "(data only)" in prompt
        assert "<resume>" in prompt
        assert "<job_description>" in prompt

    assert "USER'S EDIT REQUEST" in prompts.update_resume_prompt
    assert "USER'S EDIT REQUEST" in prompts.update_cover_letter_prompt
    assert "USER'S EDIT REQUEST" in prompts.update_answer_prompt
