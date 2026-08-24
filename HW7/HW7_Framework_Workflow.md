# Домашнє завдання №7 — Перенесення workflow на framework

## 1. Опис завдання

Перенести custom agent workflow з попереднього завдання на один із framework-ів.  
Завдання передбачає:
- реалізацію того самого workflow на обраному framework;
- визначення State, Nodes і Edges;
- тестування на 3 прикладах;
- порівняння custom implementation vs framework implementation.

**Рекомендований framework: LangGraph** — він добре відображає state, nodes, edges і conditional routing, які ми вже реалізовували вручну.  
Альтернативи: LlamaIndex Workflow, CrewAI Flow, smolagents.

---

## 2. Вимоги до виконання

### Framework
- Обрати один framework.
- Пояснити, чому обрано саме його.

### State
Визначити State як TypedDict або dataclass:
```python
class AgentState(TypedDict):
    user_question: str
    selected_route: str
    tool_result: dict
    final_answer: str
```

### Nodes
Реалізувати мінімум **2–4 nodes**:
- `classify_request` — визначає route
- `run_policy_rag` — виконує retrieval
- `run_employee_lookup` — викликає tool
- `build_answer` — формує фінальну відповідь

### Edges
- Звичайні edges між nodes
- Мінімум **один conditional edge** (наприклад: після classify_request → різні nodes залежно від route)

### Тестування
Підготувати **3 test questions** і показати для кожного:
- input question
- selected route
- executed nodes
- final state
- final answer

### Порівняння
Написати коротке порівняння custom flow vs framework:
- Що стало краще?
- Що стало складніше?
- Чи допоміг framework або додав зайву складність для цього розміру задачі?

---

## 3. Формат здачі

| Що | Де |
|---|---|
| LangGraph workflow script | `scripts/langgraph_flow.py` або `notebooks/` |
| State definition | у коді або README |
| Приклади 3 test questions | `outputs/langgraph_examples.md` |
| Порівняння custom vs framework | у README |

---

## 4. Критерії оцінювання

| Критерій | Бали | Опис |
|---|---|---|
| Framework workflow запускається локально | 15 | Script або notebook виконується без помилок |
| State визначено і використовується | 10 | TypedDict або аналог присутній |
| Мінімум 2 nodes і 1 conditional edge | 10 | Граф має розгалуження |
| 3 test examples з трасуванням | 10 | Видно route → nodes → final state |
| Порівняння custom vs framework | 5 | Є аналіз trade-offs |
| **Разом** | **50** | |

---

## 5. Приклад LangGraph workflow

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    user_question: str
    selected_route: str
    tool_result: dict
    final_answer: str

def classify_request(state: AgentState) -> AgentState:
    q = state["user_question"].lower()
    if any(w in q for w in ["vacation", "leave", "policy", "expense", "remote"]):
        state["selected_route"] = "policy_rag"
    elif any(w in q for w in ["employee", "emp_", "status"]):
        state["selected_route"] = "employee_lookup"
    else:
        state["selected_route"] = "clarification"
    return state

def run_policy_rag(state: AgentState) -> AgentState:
    state["tool_result"] = {"content": "Unused vacation days may be carried over until March 31."}
    state["final_answer"] = f"According to the HR policy: {state['tool_result']['content']}"
    return state

def run_employee_lookup(state: AgentState) -> AgentState:
    state["tool_result"] = {"status": "active", "department": "Engineering"}
    state["final_answer"] = f"Employee status: {state['tool_result']}"
    return state

def ask_clarification(state: AgentState) -> AgentState:
    state["final_answer"] = "Could you clarify: are you asking about a policy or an employee?"
    return state

def route_decision(state: AgentState) -> str:
    return state["selected_route"]

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("classify_request", classify_request)
workflow.add_node("policy_rag", run_policy_rag)
workflow.add_node("employee_lookup", run_employee_lookup)
workflow.add_node("clarification", ask_clarification)

workflow.set_entry_point("classify_request")
workflow.add_conditional_edges("classify_request", route_decision, {
    "policy_rag": "policy_rag",
    "employee_lookup": "employee_lookup",
    "clarification": "clarification",
})
workflow.add_edge("policy_rag", END)
workflow.add_edge("employee_lookup", END)
workflow.add_edge("clarification", END)

app = workflow.compile()
```

---

## 6. Приклад виведення

```
Input: Can I carry over unused vacation days?
Route: policy_rag
Nodes executed: classify_request → policy_rag
Final state: {
  user_question: "Can I carry over unused vacation days?",
  selected_route: "policy_rag",
  tool_result: { content: "Unused vacation days may be carried over until March 31." },
  final_answer: "According to the HR policy: Unused vacation days may be carried over until March 31."
}
```

---

## 7. Порівняння: custom flow vs LangGraph

| Аспект | Custom flow | LangGraph |
|---|---|---|
| Складність коду | Простіше для малих задач | Більше boilerplate |
| Видимість workflow | Не явна, треба читати код | Граф добре описує структуру |
| Робота зі state | Вручну передається dict | TypedDict забезпечує структуру |
| Conditional routing | if/else у коді | Explicit conditional edges |
| Debug | print statements | Вбудований трасування graph |
| Висновок | Ок для 2–3 steps | Виграє при 4+ steps або паралельних routes |
