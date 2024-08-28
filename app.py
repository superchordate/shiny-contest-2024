import yaml, os
import faicons as fa
import plotly.express as px
from shinywidgets import render_plotly
from shiny import reactive, render
from shiny.ui import output_text_verbatim
from shiny.express import input, ui
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import render_text_description

from langchain.agents import AgentType, initialize_agent

# automatic tool bind:
from langchain import hub
from langchain_anthropic import ChatAnthropic

# manual tool bind:
# from langchain.tools.render import render_text_description
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import JsonOutputParser
# from operator import itemgetter

# load secrets.
if os.path.exists("secrets"):
    with open("secrets") as stream:
        ANTHROPIC_API_KEY = yaml.safe_load(stream)["ANTHROPIC_API_KEY"]
else:
    ANTHROPIC_API_KEY = ''

# loop over the files in tools/ and run each file. 
# This will register the tools with the agent.
tool_files = [f for f in os.listdir("tools") if f.endswith(".py")]
toolkit_files = [f for f in os.listdir("toolkits") if f.endswith(".py")]

# Add page title and sidebar
ui.page_opts(title="AI Agent Sandbox", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_text(
        "ANTHROPIC_API_KEY",
        "Anthropic API Key",
        value=ANTHROPIC_API_KEY
    )
    ui.input_select(
        "tools",
        "Tools", # https://python.langchain.com/v0.2/docs/integrations/tools/
        tool_files,
        multiple=True,
        #selected = tool_files
    )
    ui.input_select(
        "toolkits",
        "Toolkits", # https://python.langchain.com/v0.2/docs/integrations/tools/
        toolkit_files,
        multiple=True,
        #selected = tool_files
    )

with ui.layout_columns(col_widths=[12]):

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Chat with Your Agent"
        ui.input_text_area(
            "userinput",
            "",
            width = "100%",
            value = "Can you find three pictures of the moon published between the years 2014 and 2020?"
        )        
        ui.input_action_button(
            "submit",
            "Submit",
            width = '200px'
        )

        @render.text
        @reactive.event(input.submit)
        @reactive.event(input.tools)
        def chatresults():
            
            # automatic tool bind:
            prompt = hub.pull("hwchase17/openai-tools-agent")
            with reactive.isolate():    

                # add tools. 
                tools = []
                for tool_file in input.tools():    
                    with open(f"tools/{tool_file}") as stream:
                        exec(stream.read())
                        exec(f"tools.append({tool_file.replace('.py', '')})")

                # add toolkits.
                toolkits = []
                for toolkit_file in input.toolkits():    
                    with open(f"toolkits/{toolkit_file}") as stream:
                        exec(stream.read())
                for toolkit in toolkits:
                    toolct = 0
                    for tool in toolkit.get_tools():
                        toolct+= 1
                        #print(render_text_description(tool))
                        #tools.append(tool.as_tool(name = 'fromtoolkits' + str(toolct)))
                        tools.append(tool)

                # create the agent and executor. 
                # agent = create_tool_calling_agent(get_llm(), tools, prompt)
                # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
                # return agent_executor.invoke({"input": input.userinput()})['text']
            
                agent = initialize_agent(tools, get_llm(), agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
                return agent.run(input.userinput())
            
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