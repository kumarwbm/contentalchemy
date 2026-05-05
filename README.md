# ContentAlchemy — AI Content Marketing Assistant

A multi-agent AI system that generates research reports, SEO blog posts, LinkedIn posts, and images using LangGraph orchestration.

## Architecture

```
User Query
    │
    ▼
Query Handler Agent          ← classifies intent
    │
    ├──► Deep Research Agent  ← SERP API + GPT-4o synthesis
    │         │
    │         ▼
    │    Content Strategist   ← formats research into report
    │
    ├──► SEO Blog Writer      ← keyword optimisation, meta, headers
    │
    ├──► LinkedIn Post Writer ← 1300-1600 chars, hashtags, CTA
    │
    └──► Image Generation     ← DALL-E 3 with DALL-E 2 fallback
```

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph + MemorySaver) |
| LLM | OpenAI GPT-4o |
| Research | SERP API + GPT-4o synthesis |
| Image | DALL-E 3 (DALL-E 2 fallback) |
| UI | Streamlit |
| Deployment | AWS ECS Fargate / Elastic Beanstalk |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/contentalchemy.git
cd contentalchemy
After step 1 leverage Makefile which is present now.
make install
make run

Below are the individual steps if needed.

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 4. Run
streamlit run src/web_app/app.py


```

## Environment Variables

See `.env.example` for all required keys.

## Project Structure

```
contentalchemy/
├── src/
│   ├── agents/          # All 6 LangGraph agents
│   ├── core/            # Config, state schema, graph wiring
│   ├── integrations/    # Provider abstraction (LLM, research, image)
│   └── web_app/         # Streamlit UI
├── tests/
│   ├── unit/
│   └── integration/
├── docs/                # Architecture diagrams, API docs
├── .github/workflows/   # CI/CD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Agents

| Agent | Role |
|---|---|
| Query Handler | Routes queries to the correct agent(s) |
| Deep Research | Multi-source SERP research + GPT synthesis |
| Content Strategist | Formats research into structured reports |
| SEO Blog Writer | Long-form blog with SEO optimisation |
| LinkedIn Post Writer | Platform-optimised posts with hashtags |
| Image Generation | DALL-E 3 with automatic fallback |

## Demo

_Record and link your demo video here._

## License

MIT
