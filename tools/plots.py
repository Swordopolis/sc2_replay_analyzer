import plotly.graph_objects as go

def game_to_real_minutes(game_seconds):
    """Convert game seconds to real minutes using SC2's Faster speed factor."""
    game_to_real_time = 0.714  # 1 game second = 0.714 real seconds
    return [t * game_to_real_time / 60 for t in game_seconds]


# Plotting Functions
def plot_collection_rates(player_data):
    """Plot resource collection rates over time per player."""
    fig = go.Figure()
    for player_name in player_data:
        times = game_to_real_minutes(player_data[player_name]["times"])
        minerals = player_data[player_name]["minerals_collection_rate"]
        vespene = player_data[player_name]["vespene_collection_rate"]
        total = [m + v for m, v in zip(minerals, vespene)]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=total,
                name=f"{player_name} - Total",
                mode="lines",
                hovertemplate="Total Rate: %{y} per min",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=minerals,
                name=f"{player_name} - Minerals",
                mode="lines",
                line=dict(dash="dash"),
                hovertemplate="Rate: %{y} per min",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=vespene,
                name=f"{player_name} - Vespene",
                mode="lines",
                line=dict(dash="dash"),
                hovertemplate="Rate: %{y} per min",
            )
        )

    fig.update_layout(
        title="Resource Collection Rates Over Time",
        xaxis_title="Time (Real Minutes)",
        yaxis_title="Resources per Minute",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220),
    )
    return fig


def plot_workers_active(player_data):
    """Plot workers active over time per player."""
    fig = go.Figure()
    for player_name in player_data:
        times = game_to_real_minutes(player_data[player_name]["times"])
        workers = player_data[player_name]["workers_active_count"]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=workers,
                name=f"{player_name}",
                mode="lines",
                hovertemplate="Workers: %{y}",
            )
        )

    fig.update_layout(
        title="Workers Active Over Time",
        xaxis_title="Time (Real Minutes)",
        yaxis_title="Number of Workers",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220),
    )
    return fig


def plot_income_advantage(player_data):
    """Plot income advantage (total collection rate difference) between first two players."""
    if len(player_data) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Not enough players for income advantage", showarrow=False)
        fig.update_layout(title="Income Advantage", height=400)
        return fig
    
    player1, player2 = list(player_data.keys())[:2]
    
    # Find the longest times list across all players
    all_times = []
    for player_name in player_data:
        all_times.extend(player_data[player_name]["times"])
    times = sorted(set(all_times))  # Unique, sorted times
    real_times = game_to_real_minutes(times)
    
    # Interpolate collection rates for both players at all times
    p1_total = []
    p2_total = []
    for player, p_total in [(player1, p1_total), (player2, p2_total)]:
        player_times = player_data[player]["times"]
        minerals = player_data[player]["minerals_collection_rate"]
        vespene = player_data[player]["vespene_collection_rate"]
        total = [m + v for m, v in zip(minerals, vespene)]
        idx = 0
        last_value = 0
        for t in times:
            while idx < len(player_times) - 1 and t >= player_times[idx + 1]:
                idx += 1
            if idx < len(player_times):
                last_value = total[idx]
            p_total.append(last_value)
    
    # Calculate advantage
    advantage = [p1 - p2 for p1, p2 in zip(p1_total, p2_total)]
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=real_times,
            y=advantage,
            name=f"{player1} vs {player2}",
            mode="lines",
            hovertemplate="Time: %{x:.2f} min<br>Advantage: %{y} per min"
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title=f"Income Advantage ({player1} - {player2})",
        xaxis_title="Time (Real Minutes)",
        yaxis_title=f"{player2}     {player1}",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220)
    )
    return fig


def plot_resources_available(player_data):
    """Plot resources available over time per player."""
    fig = go.Figure()
    for player_name in player_data:
        times = game_to_real_minutes(player_data[player_name]["times"])
        minerals = player_data[player_name]["minerals_current"]
        vespene = player_data[player_name]["vespene_current"]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=minerals,
                name=f"{player_name} - Minerals",
                mode="lines",
                hovertemplate="Minerals: %{y}",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=vespene,
                name=f"{player_name} - Vespene",
                mode="lines",
                hovertemplate="Vespene: %{y}",
            )
        )

    fig.update_layout(
        title="Resources Available Over Time",
        xaxis_title="Time (Real Minutes)",
        yaxis_title="Resources",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220),
    )
    return fig


def plot_army_value(player_data):
    """Plot army value over time per player."""
    fig = go.Figure()
    for player_name in player_data:
        times = game_to_real_minutes(player_data[player_name]["times"])
        army_value = player_data[player_name]["army_value"]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=army_value,
                name=f"{player_name}",
                mode="lines",
                hovertemplate="Army Value: %{y}",
            )
        )

    fig.update_layout(
        title="Army Value Over Time",
        xaxis_title="Time (Real Minutes)",
        yaxis_title="Value (Minerals + Vespene)",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220),
    )
    return fig


def plot_tech_value(player_data):
    """Plot tech value over time per player."""
    fig = go.Figure()
    for player_name in player_data:
        times = game_to_real_minutes(player_data[player_name]["times"])
        tech_value = [
            m + v
            for m, v in zip(
                player_data[player_name]["minerals_used_current_technology"],
                player_data[player_name]["vespene_used_current_technology"],
            )
        ]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=tech_value,
                name=f"{player_name}",
                mode="lines",
                hovertemplate="Tech Value: %{y}",
            )
        )

    fig.update_layout(
        title="Upgrade Value Over Time",
        xaxis_title="Time (Real Minutes)",
        yaxis_title="Upgrade Value (Minerals + Vespene)",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220),
    )
    return fig

def plot_supply(player_data):
    """Plot tech value over time per player."""
    fig = go.Figure()
    for player_name in player_data:
        times = game_to_real_minutes(player_data[player_name]["times"])
        supply_used = player_data[player_name]["food_used"]
        supply_available = player_data[player_name]["food_made"]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=supply_used,
                name=f"{player_name}",
                mode="lines",
                hovertemplate="Supply: %{y}",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=times,
                y=supply_available,
                name=f"{player_name}",
                mode="lines",
                line=dict(dash="dash"),
                hovertemplate="Supply Available: %{y}",
            )
        )

    fig.update_layout(
        title="Supply Over Time",
        xaxis_title="Time (Real Minutes)",
        yaxis_title="Supply (Used / Available)",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220),
    )
    return fig


def plot_unit_supply(player_data, player_name):
    """Plot stacked supply per unit type for a single player."""
    from tools.sc2_data import unit_list  # Updated import

    if player_name not in player_data:
        fig = go.Figure()
        fig.add_annotation(text=f"No data for {player_name}", showarrow=False)
        fig.update_layout(title=f"Unit Supply - {player_name}", height=400)
        return fig

    fig = go.Figure()

    # Get all unique times across all players
    all_times = set()
    for p_name in player_data:
        for unit_type, history in player_data[p_name]["unit_investment"].items():
            all_times.update(t for t, _ in history)
    times = sorted(all_times)
    real_times = game_to_real_minutes(times)

    # Get the last timestamp for this player
    player_times = set()
    for unit_type, history in player_data[player_name]["unit_investment"].items():
        player_times.update(t for t, _ in history)
    if player_times:
        last_player_time = max(player_times)
    else:
        last_player_time = 0

    # Plot each unit type for the specified player
    for unit_type in player_data[player_name]["unit_investment"]:
        if unit_type not in unit_list:
            continue
        history = player_data[player_name]["unit_investment"][unit_type]
        supply_values = []
        last_count = 0
        history_idx = 0
        for t in times:
            if t > last_player_time:
                supply_values.append(0)
                continue
            while history_idx < len(history) - 1 and t >= history[history_idx + 1][0]:
                history_idx += 1
            last_count = history[history_idx][1]
            supply_values.append(last_count)

        fig.add_trace(
            go.Scatter(
                x=real_times,
                y=supply_values,
                name=f"{unit_type}",
                mode="lines",
                stackgroup="supply",
                line=dict(color=unit_list.get(unit_type, "gray"), width=0),  # Use unit_list directly
                hovertemplate=f"{unit_type}: %{{y}} supply<br>Time: %{{x:.2f}} min"
            )
        )

    fig.update_layout(
        title=f"Unit Supply - {player_name}",
        xaxis_title="Time (Real Minutes)",
        yaxis_title="Supply Count",
        height=400,
        showlegend=True,
        hovermode="x unified",
        legend=dict(x=1, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=220)
    )
    return fig