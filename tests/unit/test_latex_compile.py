"""The contract with the LaTeX compiler service.

Compiling is about to start running LaTeX that users wrote rather than only LaTeX
we wrote, which turns compile failure from a rare event into a routine one. These
cover what the client does with a response that is not a PDF, and what it puts in
the archive it uploads.
"""

import io
import os
import tarfile

import pytest
import requests

from backend.utils import file_ops


class FakeResponse:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code


@pytest.fixture()
def capture_post(monkeypatch):
    """Stand in for the compiler, recording what was uploaded."""
    sent = {}

    def fake_post(url, files, timeout, **kwargs):
        sent["url"] = url
        sent["timeout"] = timeout
        sent["tar_bytes"] = files["file"][1].read()
        return sent.get("response", FakeResponse(b"%PDF-1.5\nfake pdf"))

    monkeypatch.setattr(file_ops.requests, "post", fake_post)
    return sent


def test_only_the_tex_file_is_uploaded(tmp_path, capture_post):
    """The archive used to be the whole application folder, which swept up the
    previous run's resume.json, PDF and tar."""
    (tmp_path / "resume.json").write_text('{"stale": true}')
    (tmp_path / "leftover_resume.pdf").write_bytes(b"%PDF-old")

    file_ops.generate_pdf_from_latex(
        str(tmp_path), "\\documentclass{article}", "pdflatex"
    )

    with tarfile.open(fileobj=io.BytesIO(capture_post["tar_bytes"])) as tar:
        assert tar.getnames() == ["resume/resume.tex"]


def test_upload_targets_the_tex_inside_the_archive(tmp_path, capture_post):
    file_ops.generate_pdf_from_latex(
        str(tmp_path), "\\documentclass{article}", "xelatex"
    )

    assert "target=resume/resume.tex" in capture_post["url"]
    assert "command=xelatex" in capture_post["url"]


def test_a_read_timeout_is_always_set(tmp_path, capture_post):
    """Without one, a template that loops in TeX pins a worker forever."""
    file_ops.generate_pdf_from_latex(
        str(tmp_path), "\\documentclass{article}", "pdflatex"
    )

    connect, read = capture_post["timeout"]
    assert connect > 0 and read > 0


def test_pdf_response_is_returned(tmp_path, capture_post):
    response = file_ops.generate_pdf_from_latex(
        str(tmp_path), "\\documentclass{article}", "pdflatex"
    )

    assert response.content.startswith(b"%PDF")


def test_compiler_log_instead_of_pdf_raises(tmp_path, capture_post):
    capture_post["response"] = FakeResponse(b"error: Undefined control sequence \\foo")

    with pytest.raises(ValueError, match="Failed to compile"):
        file_ops.generate_pdf_from_latex(str(tmp_path), "\\bogus", "pdflatex")


def test_non_200_raises_even_when_the_body_looks_fine(tmp_path, capture_post):
    capture_post["response"] = FakeResponse(b"gateway trouble", status_code=502)

    with pytest.raises(ValueError, match="Failed to compile"):
        file_ops.generate_pdf_from_latex(
            str(tmp_path), "\\documentclass{article}", "pdflatex"
        )


def test_a_pdf_whose_bytes_contain_the_old_error_marker_is_accepted(
    tmp_path, capture_post
):
    """The previous check searched the whole body for b'error: ', which a valid
    PDF's compressed streams can contain by chance."""
    capture_post["response"] = FakeResponse(b"%PDF-1.5\n<stream>error: </stream>")

    response = file_ops.generate_pdf_from_latex(
        str(tmp_path), "\\documentclass{article}", "pdflatex"
    )

    assert response.content.startswith(b"%PDF")


def test_timeout_is_reported_as_a_compile_failure(tmp_path, monkeypatch):
    def timeout_post(*args, **kwargs):
        raise requests.Timeout("read timed out")

    monkeypatch.setattr(file_ops.requests, "post", timeout_post)

    with pytest.raises(ValueError, match="timed out"):
        file_ops.generate_pdf_from_latex(
            str(tmp_path), "\\documentclass{article}", "pdflatex"
        )


REAL_FAILURE_LOG = """\
/var/www/shells/../latexrun/latexrun:1215: SyntaxWarning: invalid escape sequence '\\w'
  if lookingatre('(Package |Class |LaTeX |pdfTeX )?(\\w+ )?warning:
/var/www/shells/../latexrun/latexrun:1836: SyntaxWarning: invalid escape sequence '\\d'
pdflatex -interaction nonstopmode -recorder -output-directory latex.out /tmp/x/resume.tex
/tmp/x/resume.tex:100: error: There's no line here to end
      at \\\\[-3pt]
           ^
/tmp/x/resume.tex: warning: [fancyhdr] \\footskip is too small (0.0pt)
There were errors; /tmp/storage/compilation_19/output.pdf not updated
"""


def test_the_documents_error_is_reported_not_the_compilers_warnings():
    """The log opens with latexrun's own Python warnings, so quoting the head of it
    describes a problem in the compiler rather than in the user's document."""
    summary = file_ops.summarise_latex_errors(REAL_FAILURE_LOG)

    assert "There's no line here to end" in summary
    assert "\\\\[-3pt]" in summary  # the offending source line
    assert "SyntaxWarning" not in summary
    assert "lookingatre" not in summary


def test_a_log_without_a_recognisable_error_still_says_something():
    summary = file_ops.summarise_latex_errors("something went wrong\nno idea what")

    assert "no idea what" in summary


def test_the_raised_message_carries_the_summary(tmp_path, capture_post):
    capture_post["response"] = FakeResponse(REAL_FAILURE_LOG.encode(), status_code=400)

    with pytest.raises(ValueError, match="no line here to end"):
        file_ops.generate_pdf_from_latex(str(tmp_path), "\\bogus", "pdflatex")


def test_write_failures_are_not_swallowed(tmp_path):
    """generate_tex_and_tar used to log at debug level and return None, so the
    caller failed later with a TypeError on open(None) instead of the real cause."""
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("")

    with pytest.raises(OSError):
        file_ops.generate_tex_and_tar(str(blocked / "sub"), "\\documentclass{article}")


def test_control_characters_are_stripped_before_writing(tmp_path, capture_post):
    file_ops.generate_pdf_from_latex(
        str(tmp_path), "clean\x16text \\documentclass{article}", "pdflatex"
    )

    written = (tmp_path / "resume.tex").read_text(encoding="utf-8")
    assert "\x16" not in written
    assert "cleantext" in written
    assert os.path.exists(tmp_path / "resume.tar")
