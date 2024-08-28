import yaml, os
import faicons as fa
import plotly.express as px

# Load data and compute static values
from shared import app_dir, tips
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui

if os.path.exists("secrets"):
    with open("secrets") as stream:
        try:
            OPENAI_API_KEY = yaml.safe_load(stream)["OPENAI_API_KEY"]
        except yaml.YAMLError as exc:
            print(exc)

# Add page title and sidebar
ui.page_opts(title="AI Agent Sandbox", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_text(
        "OPENAI_API_KEY",
        "OpenAI API Key",
        value=OPENAI_API_KEY
    )

# Add main content
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(col_widths=[6, 6, 12]):

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Chat with Your Agent"            
            # ui.input_text(
            #     "OPENAI_API_KEY",
            #     "OpenAI API Key",
            #     value=OPENAI_API_KEY
            # )

        


ui.include_css(app_dir / "styles.css")

