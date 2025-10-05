import os, asyncio
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
# WAŻNE: MessagesPlaceholder z langchain_core
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools import (
    get_city_situation, get_line_situation, plan_trip,
    report_issue, vote_issue, verify_issue
)

SYSTEM_PROMPT = """Jesteś asystentem pasażera komunikacji miejskiej. Odpowiadasz po polsku, krótko i konkretnie.
Gdy pytanie dotyczy sytuacji w mieście/na linii – użyj odpowiednich narzędzi.
Gdy proszą o trasę – użyj plan_trip. Zawsze podawaj minuty i krótką radę (np. alternatywa).
Jeśli brak danych – powiedz to wprost i zasugeruj zgłoszenie problemu.
"""

# ✅ Dodajemy placeholder na scratchpad (i opcjonalnie na historię czatu)
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

tools = [get_city_situation, get_line_situation, plan_trip, report_issue, vote_issue, verify_issue]

def build_agent() -> AgentExecutor:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)

agent_executor = build_agent()

async def ask_agent(message: str) -> str:
    res = await agent_executor.ainvoke({"input": message, "chat_history": []})
    return res["output"]