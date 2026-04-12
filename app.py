# Shiny for Python Core
from shiny import App, reactive, render, ui
import plotly.express as px
from shinywidgets import output_widget, render_widget
from icons import question_circle_fill
from itables.shiny import DT
import pandas as pd
import itables.options as opt
# increase sizing to prevent downsampling
opt.maxBytes = "1MB"

df = pd.read_parquet("data.parquet")

color_map = {
    "Steam Deck Verified": "#2ecc71",
    "Steam Deck Playable": "#f1c40f",
    "Steam Deck Unsupported": "#e74c3c",
    "No Steam Deck Information": "#95a5a6",
}

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Filters"),
            ui.input_selectize(  
                "wishlist_owned_filter",
                "Wishlist/Owned:",
                choices={
                    "Yes": "Wishlist",
                    "No": "Owned"
                },
                selected=["Yes", "No"],
                multiple=True,  
            ),
            ui.tooltip(
                ui.span("", question_circle_fill),
                ui.tags.ul(
                    ui.tags.li("Verified - The game works great on Steam Deck, right out of the box."),
                    ui.tags.li("Playable - The game may require some manual tweaking by the user."),
                    ui.tags.li("Unsupported - The game is currently not functional on Steam Deck."),
                    ui.tags.li("Unknown - This game hasn't been checked yet."),
                ),
                placement="right",
                id="steamdeck_supported_tooltip",
            ),
            ui.input_selectize(  
                "steamdecksupport_filter",  
                "Steam Deck Supported:",  
                {"No Steam Deck Information": "No Steam Deck Information",
                  "Steam Deck Playable": "Steam Deck Playable",
                  "Steam Deck Verified": "Steam Deck Verified",
                  "Steam Deck Unsupported": "Steam Deck Unsupported"},  
                selected=["No Steam Deck Information", "Steam Deck Playable",
                          "Steam Deck Verified", "Steam Deck Unsupported"],
                multiple=True,  
            ),
            ui.input_slider(
                "slider_max_playtime", "Game Playtime (minutes)", min=0, max=max(df['playtime_forever']), value=(0, max(df['playtime_forever']))
            ),
            ui.input_slider(
                "slider_protondb_submissions", "Total ProtonDB Submissions", min=0, max=max(df['total_protondb_submissions']), value=(0, max(df['total_protondb_submissions']))
            ),
            ui.input_slider(
                "slider_protondb_supported_percentage", "ProtonDB Supported Percentage", min=0, max=max(df['protondb_supported_percentage']), value=(0, max(df['protondb_supported_percentage']))
            ),
            ui.input_slider(
                "slider_metacritic", "Metacritic Score", min=0, max=max(df['metacritic']), value=(0, max(df['metacritic']))
            ),
        ),
        ui.h1("Shiny Steam Linux Game Support"),
        ui.card("Presets",
            ui.layout_columns(
                ui.input_action_button("reset_filters", "Reset Filters"),
                ui.input_action_button("next_purchase", "Next Game Purchase"),
                ui.input_action_button("problem_owned_games", "Potential Issues With Owned Games"),
                ui.input_action_button("problem_wishlist_games", "Potential Issues With Wishlisted Games"),
            )
        ),
        ui.layout_columns(
            ui.card("Wishlist",
                output_widget("wishlist_category_plot"),
                output_widget("wishlist_protondb_percentage_histogram"),
                output_widget("wishlist_protondb_numreviews_histogram"),
            ),
            ui.card("Owned Games",
                output_widget("owned_category_plot"),
                output_widget("owned_protondb_percentage_histogram"),
                output_widget("owned_protondb_numreviews_histogram"),
            )
        ),
        ui.card("Games Table", ui.output_ui("renderTable")),
    )
)

def server(input, output, session):

    @reactive.calc
    def reactiveDF():
        filtered = df

        # owned or wishlisted games (categorical)
        wishlist = input.wishlist_owned_filter()
        if not wishlist:
            return df.iloc[0:0]  # or empty dataframe
        else:
            filtered = filtered[filtered["on_wishlist"].isin(wishlist)]

        # Steam Deck filter (categorical)
        steamdeck = input.steamdecksupport_filter()
        if not steamdeck:
            return df.iloc[0:0]  # or empty dataframe
        else:
            filtered = filtered[filtered["resolved_category"].isin(steamdeck)]

        # Playtime range
        play_min, play_max = input.slider_max_playtime()
        filtered = filtered[
            filtered["playtime_forever"].between(play_min, play_max)
        ]

        # ProtonDB submissions
        sub_min, sub_max = input.slider_protondb_submissions()
        filtered = filtered[
            filtered["total_protondb_submissions"].between(sub_min, sub_max)
        ]

        # ProtonDB supported %
        pct_min, pct_max = input.slider_protondb_supported_percentage()
        filtered = filtered[
            filtered["protondb_supported_percentage"].between(pct_min, pct_max)
        ]

        # Metacritic score
        meta_min, meta_max = input.slider_metacritic()
        filtered = filtered[
            filtered["metacritic"].between(meta_min, meta_max)
        ]

        return filtered
    
    @reactive.calc
    def filteredWishlist():
        return reactiveDF()[reactiveDF()["on_wishlist"] == "Yes"]
    
    @reactive.calc
    def filteredOwnedGames():
        return reactiveDF()[reactiveDF()["on_wishlist"] == "No"]

    @output
    @render.ui
    def renderTable():
        df_table = reactiveDF()

        table = DT(
            df_table,
            search=True,
            pageLength=10,
        )

        return ui.HTML(table)
    
    @output
    @render_widget
    def wishlist_category_plot():
        data = filteredWishlist()

        counts = (
            data["resolved_category"]
            .value_counts()
            .reset_index()
        )

        counts.columns = ["resolved_category", "count"]

        fig = px.bar(
            counts,
            x="resolved_category",
            y="count",
            color="resolved_category",
            color_discrete_map=color_map,
            title="Wishlist Games by Steam Deck Support Category",
        )

        fig.update_layout(xaxis_title="", yaxis_title="Number of Games", showlegend=False)

        return fig
    
    @output
    @render_widget
    def owned_category_plot():
        data = filteredOwnedGames()

        counts = (
            data["resolved_category"]
            .value_counts()
            .reset_index()
        )

        counts.columns = ["resolved_category", "count"]

        fig = px.bar(
            counts,
            x="resolved_category",
            y="count",
            color="resolved_category",
            color_discrete_map=color_map,
            title="Owned Games by Steam Deck Support Category",
        )

        fig.update_layout(xaxis_title="", yaxis_title="Number of Games", showlegend=False)

        return fig
    
    @output
    @render_widget
    def wishlist_protondb_percentage_histogram():
        data = filteredWishlist()

        fig = px.histogram(
            data,
            x="protondb_supported_percentage",
            nbins=60,
            title="Distribution of ProtonDB Supported Percentage Wishlist Games",
        )

        fig.update_layout(
            xaxis_title="ProtonDB Supported %",
            yaxis_title="Number of Games",
        )

        return fig
    
    @output
    @render_widget
    def owned_protondb_percentage_histogram():
        data = filteredOwnedGames()

        fig = px.histogram(
            data,
            x="protondb_supported_percentage",
            nbins=60,
            title="Distribution of ProtonDB Supported Percentage Owned Games",
        )

        fig.update_layout(
            xaxis_title="ProtonDB Supported %",
            yaxis_title="Number of Games",
        )

        return fig
    
    @output
    @render_widget
    def wishlist_protondb_numreviews_histogram():
        data = filteredWishlist()

        fig = px.histogram(
            data,
            x="total_protondb_submissions",
            nbins=60,
            title="Distribution of ProtonDB Submissions For Wishlist Games",
        )

        fig.update_layout(
            xaxis_title="ProtonDB Submissions",
            yaxis_title="Number of Games",
        )

        return fig
    
    @output
    @render_widget
    def owned_protondb_numreviews_histogram():
        data = filteredOwnedGames()

        fig = px.histogram(
            data,
            x="total_protondb_submissions",
            nbins=60,
            title="Distribution of ProtonDB Submissions For Owned Games",
        )

        fig.update_layout(
            xaxis_title="ProtonDB Submissions",
            yaxis_title="Number of Games",
        )

        return fig
    
    @reactive.effect
    @reactive.event(input.reset_filters)
    def reset_filters():
        ui.update_selectize(
            "wishlist_owned_filter",
            selected=["Yes", "No"],
        )
        ui.update_selectize(
            "steamdecksupport_filter",
            selected=["No Steam Deck Information", "Steam Deck Playable",
                        "Steam Deck Verified", "Steam Deck Unsupported"],
        )
        ui.update_slider("slider_max_playtime", value=(0, max(df["playtime_forever"])))
        ui.update_slider("slider_protondb_submissions", value=(0, max(df["total_protondb_submissions"])))
        ui.update_slider("slider_protondb_supported_percentage", value=(0, max(df["protondb_supported_percentage"])))
        ui.update_slider("slider_metacritic", value=(0, max(df["metacritic"])))

    @reactive.effect
    @reactive.event(input.next_purchase)
    def next_purchase():
        ui.update_selectize(
            "wishlist_owned_filter",
            selected=["Yes"],
        )
        ui.update_selectize(
            "steamdecksupport_filter",
            selected=["Steam Deck Playable", "Steam Deck Verified"],
        )
        ui.update_slider("slider_max_playtime", value=(0, max(df["playtime_forever"])))
        ui.update_slider("slider_protondb_submissions", value=(20, max(df["total_protondb_submissions"])))
        ui.update_slider("slider_protondb_supported_percentage", value=(75, max(df["protondb_supported_percentage"])))
        ui.update_slider("slider_metacritic", value=(75, max(df["metacritic"])))

    @reactive.effect
    @reactive.event(input.problem_owned_games)
    def problem_owned_games():
        ui.update_selectize(
            "wishlist_owned_filter",
            selected=["No"],
        )
        ui.update_selectize(
            "steamdecksupport_filter",
            selected=["No Steam Deck Information", "Steam Deck Unsupported"],
        )
        ui.update_slider("slider_max_playtime", value=(0, max(df["playtime_forever"])))
        ui.update_slider("slider_protondb_submissions", value=(0, max(df["total_protondb_submissions"])))
        ui.update_slider("slider_protondb_supported_percentage", value=(0, 50))
        ui.update_slider("slider_metacritic", value=(0, max(df["metacritic"])))

    @reactive.effect
    @reactive.event(input.problem_wishlist_games)
    def problem_wishlist_games():
        ui.update_selectize(
            "wishlist_owned_filter",
            selected=["Yes"],
        )
        ui.update_selectize(
            "steamdecksupport_filter",
            selected=["No Steam Deck Information", "Steam Deck Unsupported"],
        )
        ui.update_slider("slider_max_playtime", value=(0, max(df["playtime_forever"])))
        ui.update_slider("slider_protondb_submissions", value=(0, max(df["total_protondb_submissions"])))
        ui.update_slider("slider_protondb_supported_percentage", value=(0, 50))
        ui.update_slider("slider_metacritic", value=(0, max(df["metacritic"])))


app = App(app_ui, server)
