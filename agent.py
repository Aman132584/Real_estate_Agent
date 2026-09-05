from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from config import settings


@tool
def sea_listings(query: str) -> str:
    """Search available property listings. Pass a natural description of what the client wants,
    e.g. '3 marla plot', 'plot near Ferozpur Road under 2 million', 'corner plot with park facing'."""
    from rag import retrieve_listings
    results = retrieve_listings(query)
    if not results:
        return "No matching listings found."
    return "\n\n".join(
        f"{r.title} - {r.location} - PKR {r.price:,}\n{r.description}"
        for r in results
    )


@tool
def book_viewing(lead_phone: str, listing_title: str) -> str:
    """Book a property viewing for a lead."""
    return f"Viewing booked for {listing_title}, we'll confirm the time shortly."


tools = [sea_listings, book_viewing]

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=settings.google_api_key)
# llm = ChatAnthropic(model="claude-sonnet-4-6", api_key=settings.anthropic_api_key)  # switch back to this once billing is sorted
llm_with_tools = llm.bind_tools(tools)


def call_model(state: MessagesState):
    is_first_message = len(state["messages"]) == 1

    system_text = (
        f"You work at {settings.business_name}, a real estate business, and you're chatting with a "
        f"potential client on WhatsApp. Speak as a real person on the team - use \"we\" and \"our\" "
        f"(never \"they\", never say you're an AI or an assistant). Keep replies short, warm, and "
        f"conversational, like a real person texting - not a formal listing sheet, not heavy bullet "
        f"points or bold formatting for every detail. "
        + (
            "This is the client's first message to you. Start with a brief, warm greeting "
            "introducing yourself as part of the team, then naturally answer their question in "
            "the same message - don't send the greeting and the answer separately."
            if is_first_message else
            "This is a continuing conversation - don't re-introduce yourself or repeat greetings, "
            "just continue naturally."
        )
    )

    messages = [{"role": "system", "content": system_text}] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def conti(state: MessagesState):
    last_mess = state["messages"][-1]
    if last_mess.tool_calls:
        return "tools"
    return END


graph = StateGraph(MessagesState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", conti)
graph.add_edge("tools", "agent")

app = graph.compile()


if __name__ == "__main__":
    result = app.invoke({"messages": [{"role": "user", "content": "Hi, do you have any 3 bed places in DHA under 4 crore?"}]})
    print(result["messages"][-1].content)