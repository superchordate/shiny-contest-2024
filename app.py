import yaml, os
import faicons as fa
import plotly.express as px
from shinywidgets import render_plotly
from shiny import reactive, render
from shiny.ui import output_text_verbatim
from shiny.express import input, ui
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

# automatic tool bind:
from langchain import hub
from langchain_anthropic import ChatAnthropic
#from langchain_anthropic  import AnthropicLLM


# manual tool bind:
from langchain.tools.render import render_text_description
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from operator import itemgetter

# load secrets.
if os.path.exists("secrets"):
    with open("secrets") as stream:
        ANTHROPIC_API_KEY = yaml.safe_load(stream)["ANTHROPIC_API_KEY"]
else:
    ANTHROPIC_API_KEY = ''

# initial tool.
@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int

@tool
def add(first_int: int, second_int: int) -> int:
    "Add two integers."
    return first_int + second_int

@tool
def exponentiate(base: int, exponent: int) -> int:
    "Exponentiate the base to the exponent power."
    return base**exponent

# Add page title and sidebar
ui.page_opts(title="AI Agent Sandbox", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_text(
        "ANTHROPIC_API_KEY",
        "OpenAI API Key",
        value=ANTHROPIC_API_KEY
    )

# Add main content
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(col_widths=[12]):

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Chat with Your Agent"
        ui.input_text_area(
            "userinput",
            "",
            width = "100%",
            value = "Take 3 to the fifth power and multiply that by the sum of twelve and three, then square the whole result"
        )
        with ui.layout_columns(col_widths=[2]):
            ui.input_action_button(
                "submit",
                "Submit"
            )

        @render.text
        @reactive.event(input.submit)
        def chatresults():
            
            # automatic tool bind:
            prompt = hub.pull("hwchase17/openai-tools-agent")
            tools = [multiply, add, exponentiate]
            agent = create_tool_calling_agent(get_llm(), tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            with reactive.isolate():
                return agent_executor.invoke({"input": input.userinput()})
            
            # manual tool bind:
            # tools = [multiply, add, exponentiate]            

            # def tool_chain(model_output):
            #     tool_map = {tool.name: tool for tool in tools}
            #     chosen_tool = tool_map[model_output["name"]]
            #     return itemgetter("arguments") | chosen_tool
            
            # rendered_tools = render_text_description(tools)

            # system_prompt = f"""You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:
            #     {rendered_tools}
            #     Given the user input, return the name and input of the tool to use. Return your response as a JSON blob with 'name' and 'arguments' keys."""
            # prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", "{input}")])

            # chain = prompt | get_llm() | JsonOutputParser() | tool_chain

            # with reactive.isolate():                
            #     result = chain.invoke({"input": input.userinput(), "verbose": True})

            # print(result)
            # return result

ui.include_css("./styles.css")

@reactive.calc
def get_llm():
  os.environ["ANTHROPIC_API_KEY"] = input.ANTHROPIC_API_KEY()
  return ChatAnthropic(model="claude-3-sonnet-20240229")