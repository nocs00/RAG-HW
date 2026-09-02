# Домашнє завдання №8 — Evaluation + Observability layer

## 1. Опис завдання

Додати до свого chatbot-а мінімальний шар спостереження й оцінювання якості.  
Завдання передбачає:
- підготовку eval set із 8–12 test questions;
- запуск chatbot на цих питаннях і збір результатів у структуровану таблицю;
- розрахунок мінімальних observability metrics;
- написання короткого quality report із 3 головними проблемами.

**Мета** — не просто запустити систему, а зафіксувати traces, метрики і зрозуміти, де система працює добре, а де ні.

---

## 2. Вимоги до виконання

### Eval set
Підготувати **8–12 test questions**, що покривають:
- просте питання з knowledge base;
- питання, де потрібен retrieval;
- питання, де retrieval може помилитися;
- питання, де chatbot має сказати "не знаю";
- питання, де потрібен tool;
- одне складне або неоднозначне питання.

### Eval table
Для кожного питання зафіксувати:

| Колонка | Тип | Опис |
|---|---|---|
| `id` | int | Номер кейсу |
| `question` | string | Питання користувача |
| `expected_behavior` | string | Що система мала зробити |
| `answer` | string | Фактична відповідь |
| `retrieved_chunks` | string | Які chunks або sources використано |
| `route_or_mode` | string | RAG / tool / fallback / clarification |
| `tools_used` | string | Назви викликаних tools |
| `task_success` | yes/partial/no | Чи задача виконана |
| `groundedness` | good/partial/bad | Чи відповідь підтримана context |
| `answer_quality` | good/partial/bad | Загальна якість |
| `latency_ms` | int | Час виконання |
| `errors` | string | none / wrong_retrieval / hallucination / тощо |
| `notes` | string | Короткий коментар |

### Observability metrics
Розрахувати (вручну або скриптом):
- `total_cases`
- `success_rate` (task_success = yes / total)
- `groundedness_good_rate`
- `average_latency_ms`
- `top_error_types`

### Quality report
Написати звіт 0.5–1 сторінки:
- що тестувалося
- результати
- де система добре / погано
- **3 головні проблеми**
- що покращити наступним кроком

---

## 3. Формат здачі

| Що | Де |
|---|---|
| Eval table (CSV або Markdown) | `outputs/eval_results.csv` або `outputs/eval_results.md` |
| Observability metrics summary | `outputs/eval_summary.md` або у README |
| Quality report | `outputs/quality_report.md` або у README |

---

## 4. Критерії оцінювання

| Критерій | Бали | Опис |
|---|---|---|
| Eval set із 8–12 питань різних типів | 10 | Є coverage різних сценаріїв |
| Повна eval table з усіма колонками | 15 | Усі обов'язкові поля заповнені |
| Observability metrics розраховано | 10 | success_rate, groundedness, latency, errors |
| Quality report написано | 10 | Є аналіз, а не просто таблиця |
| 3 головні проблеми чітко сформульовано | 5 | Проблеми конкретні, не розмиті |
| **Разом** | **50** | |

---

## 5. Приклад eval table

| id | question | expected_behavior | route_or_mode | task_success | groundedness | answer_quality | latency_ms | errors | notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | How many vacation days do I get? | Answer from KB | RAG | yes | good | good | 1650 | none | Correct policy retrieved |
| 2 | Can I carry over vacation days? | Answer from KB with date | RAG | yes | good | good | 1720 | none | March 31 rule correctly cited |
| 3 | What is the CEO's salary? | Say not enough information | RAG | yes | bad | good | 1800 | wrong_retrieval | Fallback triggered correctly |
| 4 | What is status of emp_001? | Use employee tool | tool | yes | not_applicable | good | 2100 | none | Tool returned correct data |
| 5 | Can I use my personal laptop? | Answer from remote work policy | RAG | partial | partial | partial | 1900 | missing_context | Answer correct but no citation |
| 6 | How do I submit expenses? | Step-by-step from expense policy | RAG | yes | good | good | 1750 | none | Good result |
| 7 | Tell me about everything | Clarification | clarification | yes | not_applicable | good | 950 | none | Correctly asked to clarify |
| 8 | When is my next performance review? | Say not enough info (no date in KB) | RAG | no | bad | bad | 1800 | hallucination | Model invented a date |

---

## 6. Приклад observability metrics

```
Total cases: 10
Success rate: 7/10 = 70%
Partial success: 2/10 = 20%
Failure rate: 1/10 = 10%

Groundedness good: 6/10 = 60%
Groundedness partial: 2/10 = 20%
Groundedness bad: 2/10 = 20%

Average latency: 1,742 ms
Max latency: 2,100 ms (tool call)

Error types:
  none: 7
  wrong_retrieval: 1
  missing_context: 1
  hallucination: 1
```

---

## 7. Приклад quality report

```
# Quality Report — HR Policy Assistant

## What was tested
10 questions covering: policy retrieval, employee tool, fallback, 
clarification, and out-of-scope queries.

## Results
- 70% success rate overall
- Retrieval works well for direct policy questions
- Employee tool integration works correctly
- Fallback behavior mostly correct

## Where the system works well
- Direct single-document questions (vacation, expense rules)
- Employee status lookups via tool
- Out-of-scope clarification routing

## Where the system fails
- Questions requiring multi-document reasoning return incomplete answers
- Model occasionally hallucinates dates not present in knowledge base
- Some answers lack citation even when retrieval found correct chunk

## 3 Main Problems
1. Hallucination on time-sensitive queries (dates, deadlines not in KB)
2. Missing citations in ~20% of answers despite prompt instruction
3. Retrieval returns irrelevant chunks for vague or broad queries

## Next Steps
- Add explicit fallback threshold on retrieval score
- Strengthen prompt to enforce citation on every RAG answer
- Add metadata filtering by document_type to reduce noise in retrieval
```
