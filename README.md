# Zumud

<div align="center">

![Zumud Logo](/frontend/public/logos/zumud/combined.svg)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js_16-000000.svg?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)

</div>

**Zumud** is an open-source platform that tailors your resume and cover letter to a specific job description using AI — with polished PDF output, an application dashboard, and interview-question prep.

## Features

- **Resume tailoring** — customize your resume for each job description.
- **Cover letters & Q&A** — generate cover letters and answers to application questions.
- **PDF upload & parsing** — drop in a PDF; AI extracts and structures the text.
- **PDF / LaTeX output** — download a professional PDF or the LaTeX source.
- **Dashboard** — manage resumes, applications, and settings behind secure auth.

## Tech stack

FastAPI · Next.js 16 · Supabase (Postgres + Auth) · self-hosted LaTeX compiler · Caddy.

## Quickstart

The only secret you need to run everything locally is an **OpenAI API key**. The local database, auth, storage, and test email come from the Supabase CLI stack; PDFs from a local LaTeX container.

**Prerequisites:** Docker, [Supabase CLI](https://supabase.com/docs/guides/cli), Node 20+, Python 3.12, Git.

```bash
git clone https://github.com/Zumud/Zumud.git && cd Zumud

# Dependencies
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd frontend && npm install && cd ..

# The one required key
echo "OPEN_AI_KEY=sk-your-key" > .env
```

Then start the stack and apps (Docker must be running):

```bash
make up            # local Supabase (Postgres, Auth, Storage, Mailpit)
make latex-up      # local LaTeX -> PDF service (first build downloads a few GB)
make dev-backend   # FastAPI  -> http://localhost:8000   (one terminal)
make dev-frontend  # Next.js  -> http://localhost:3000   (another terminal)
```

Open **http://localhost:3000**. The `make dev-*` targets wire themselves to the local stack automatically — no other config needed. Run `make help` for all commands.

> Everything except `OPEN_AI_KEY` is optional and degrades gracefully: email (Resend), billing (Stripe), and Google sign-in stay off until you add their keys, and the core product works without them.

For specifics — test emails (Mailpit), Google sign-in, LaTeX alternatives, WSL notes — see **[docs/local-dev.md](docs/local-dev.md)**. Deeper guides live in **[docs/](docs/)**.

## API docs

With the backend running: Swagger at `/docs`, ReDoc at `/redoc` (e.g. http://localhost:8000/docs).

## Contributing

Contributions are welcome. Branch off `main`, keep commits small and single-purpose, and open a PR. Never commit secrets or `.env*` files.

## Community

- Main group: [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/+GN3-DufToPU4OTA0)
- Dev chat: [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/+a8Cz2QqZWRdkMzI0)

## License

**AGPL-3.0** — see [LICENSE](LICENSE). You may use, modify, and self-host Zumud; if you run a modified version as a network service, you must offer its users your modified source under the same license.

## Security

Found a vulnerability? Report it privately — see [SECURITY.md](SECURITY.md). Please don't open a public issue for security reports.

---

<div align="center">
  <sub>Built with ❤️ by the Zumud Team</sub>
</div>
