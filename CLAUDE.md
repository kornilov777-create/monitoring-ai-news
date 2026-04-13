# AI DEVELOPMENT CONSTITUTION — MONITORING-AI-NEWS
**Iterative • Immutable • Versioned • Safe • Auditable Engineering**

## 0. PROJECT SPECIFICATION — SOURCE OF TRUTH

**Obsidian AI_BRAIN** — единственный мастер-источник правды по проекту.

| Источник | Путь | Назначение |
|----------|------|------------|
| **Master Dashboard** | `AI_BRAIN/01_Projects/Monitoring-AI-News.md` | Архитектура, метрики, здоровье, roadmap |
| **Конституция** | `CLAUDE.md` (этот файл) | Правила разработки |

**Rule:** Obsidian > CLAUDE.md. При конфликте — верь Obsidian.

## I. ROLE AND ENGINEERING IDENTITY

AI operates as a collective senior engineering authority, simultaneously fulfilling the roles of Principal Software Engineer, System Architect, Security Engineer, Code Reviewer, Release Manager, and Documentation Owner.

## II. ABSOLUTE PROHIBITIONS — IMMUTABILITY LAW

The AI is strictly forbidden from deleting code, files, functions, classes, modules, comments, or historical implementations. Permitted actions: adding new implementations, isolating legacy logic, marking deprecated components. Deletion only upon explicit user command.

## III. ITERATIVE DEVELOPMENT LAW

All development must proceed strictly through incremental iterations. Semantic Versioning (MAJOR.MINOR.PATCH) is mandatory.

## IV. PROJECT CONTEXT

**Проект:** Мониторинг новостей AI — автоматический сбор, анализ и доставка новостей из мира ИИ
**Владелец:** Станислав
**Язык интерфейса:** Русский

### Стек
| Компонент | Технология | Входная точка |
|-----------|------------|---------------|
| **Backend** | Python 3.12, FastAPI | `backend/main.py` |
| **Bot** | aiogram 3.15+ | `backend/app/bot/` |
| **DB** | SQLAlchemy + SQLite | `data/ai_news.db` |
| **Scraping** | BeautifulSoup, aiohttp, lxml, feedparser | `backend/app/services/` |
| **Scheduler** | APScheduler | `backend/app/tasks/` |
| **CI/CD** | GitHub Actions | `.github/workflows/collect.yml` |
| **Frontend** | Static HTML/JS | `index.html`, `products.html` |

### Архитектура
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  GitHub      │────▶│  Collector   │────▶│  SQLite DB   │
│  Actions     │     │  (cron 4h)   │     │  ai_news.db  │
│  (schedule)  │     │  8+ parsers  │     │  ~1000 статей│
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
┌──────────────┐     ┌──────────────┐     ┌──────▼───────┐
│  Telegram    │────▶│  Bot         │────▶│  FastAPI     │
│  (aiogram)   │     │  дайджесты   │     │  REST API    │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
┌──────────────┐                          ┌──────▼───────┐
│  Browser     │◀─────────────────────────│  Dashboard   │
│  (user)      │                          │  index.html  │
└──────────────┘                          │  products    │
                                          └──────────────┘
```

### Источники новостей
| Источник | Тип |
|----------|-----|
| OpenAI Blog | Custom parser |
| Google AI Blog | Custom parser |
| MIT News AI | Custom parser |
| MIT Technology Review | Custom parser |
| TechCrunch AI | Custom parser |
| The Verge AI | Custom parser |
| VentureBeat AI | Custom parser |
| AI News | Custom parser |

### Критические правила
1. **GitHub Actions** — автосбор каждые 4 часа + auto-commit
2. **Парсеры** — каждый источник имеет свой парсер в `backend/app/services/`
3. **Данные** — JSON файлы коммитятся в репо (data/)
4. **Bot** — дайджесты и уведомления через Telegram
5. **CORS** — настроить для продакшена (не wildcard)

### Данные
| Файл | Назначение |
|------|------------|
| `data/news.json` | Собранные статьи (~1800 записей) |
| `data/sources.json` | Конфигурация источников |
| `data/ai_products.json` | Каталог AI-продуктов (900+ записей) |
| `data/ai_news.db` | SQLite база данных |

### Переменные окружения
- Шаблон: `backend/.env.example`
- Telegram bot token + owner ID
- Интервал сбора (COLLECT_INTERVAL_HOURS=4)
- **НИКОГДА** не коммитить `.env` с реальными токенами

## V. SECURITY — ALWAYS ENABLED

For every iteration, perform threat-oriented reasoning. Validate all scraped content before storage. No user credentials in logs or git.

## VI. DOCUMENTATION AS A FIRST-CLASS ARTIFACT

Documentation is part of the product. Each version must be understandable without chat history.

## VII. CONFLICT RESOLUTION

**Tier 0 (Inviolable):** Security, Data protection, Backward compatibility
**Tier 1 (Critical):** Correctness, Immutability, Audit trail
**Tier 2 (Operational):** Performance, Maintainability, Documentation

## VIII. OBSIDIAN INTEGRATION

**Dashboard:** `AI_BRAIN/01_Projects/Monitoring-AI-News/Dashboard.md`

Events this project MUST emit to AI_BRAIN via `obsidian_event_client`:

| When | event_type | Emitter |
|---|---|---|
| GitHub Actions `collect.yml` finishes successfully | `metric` (article counts) | `.github/workflows/collect.yml` post-step |
| A parser fails (8 parsers total) | `incident` | same workflow, on failure |
| New version tag | `deploy` | release workflow |

### Wiring (не ломает текущий сбор)

Добавляется в `.github/workflows/collect.yml` **в самом конце** как
отдельный step с `if: always()`. Ничего существующего не трогается.

```yaml
- name: Report to AI_BRAIN
  if: always()
  env:
    OBSIDIAN_GATEWAY_URL: http://10.10.20.192:7010  # or via Cloudflare Tunnel once published
  run: |
    pip install -q 'obsidian-event-client @ git+ssh://git@github.com/kornilov777-create/sprut.git#subdirectory=libs/obsidian_event_client'
    python - <<'PY'
    import asyncio, os
    from obsidian_event_client import ObsidianClient, EventType
    async def main():
        c = ObsidianClient(source_project="monitoring-ai-news", machine="github-actions")
        status = "${{ job.status }}"
        if status == "success":
            await c.write_event(EventType.METRIC, f"collect.yml ok — run {os.environ['GITHUB_RUN_ID']}",
                                content="8 parsers, see run logs for article counts.",
                                tags=["collect", "github-actions"])
        else:
            await c.write_event(EventType.INCIDENT, f"collect.yml FAILED — run {os.environ['GITHUB_RUN_ID']}",
                                content=f"Status: {status}",
                                tags=["collect", "failure"])
    asyncio.run(main())
    PY
```

GitHub Actions runner НЕ имеет прямого сетевого доступа к
`10.10.20.192` (это home LAN). Чтобы step реально работал, gateway
должен быть опубликован через Cloudflare Tunnel
(`gateway.stk777-infra.<domain>`). До настройки туннеля step остаётся
задизейбленным через `if: false && always()` — и автоматически
заработает как только `OBSIDIAN_GATEWAY_URL` станет внешне доступным.
**Ни один существующий step не изменяется и не ломается.**

## IX. FINAL PRINCIPLE

**Code is not merely an output. It is frozen engineering reasoning over time. History outweighs cleanliness. Explainability outweighs speed.**

**Current Version:** 1.0.1
**Last Updated:** 2026-04-14
