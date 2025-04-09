# Custom dictionary for unit costs and event -> unit mapping
from sc2_data import costs, morph_to_unit, unit_list, relevant_events

# Helper Functions
def get_player_name(event):
    """Extract player name from an event, return None if not found."""
    if hasattr(event, 'player') and event.player and hasattr(event.player, 'name'):
        return str(event.player.name)
    elif hasattr(event, 'unit') and hasattr(event.unit, 'owner') and event.unit.owner and hasattr(event.unit.owner, 'name'):
        return str(event.unit.owner.name)
    return None


# initialization 
def initialize_data_structures(replay):
    """Initialize player data structures for tracking stats and investments."""
    player_data = {}
    for player in replay.players:
        player_data[player.name] = {
            # Economy stats from PlayerStatsEvent (time in game seconds)
            "times": [],
            "minerals_collection_rate": [],
            "minerals_current": [],
            "minerals_used_current_army": [],
            "minerals_used_current_economy": [],
            "minerals_used_current_technology": [],
            "vespene_collection_rate": [],
            "vespene_current": [],
            "vespene_used_current_army": [],
            "vespene_used_current_economy": [],
            "vespene_used_current_technology": [],
            "army_value": [],
            "workers_active_count": [],
            "food_made": [],
            "food_used": [],
            # Unit investment tracking (time, supply_count)
            "unit_investment": {unit: [(0, 0)] for unit in unit_list},
            # TODO: Placeholder for team affiliation (e.g., 1v1, 2v2)
            "team": None  # Will be set in future multi-player logic
        }
    # TODO: Placeholder for multi-player/team grouping logic
    # e.g., player_data["teams"] = {1: [player1, player2], 2: [player3, player4]}
    return player_data

# Handlers for different event types
def handle_player_stats(event, player_data):
    """Extract economy stats from PlayerStatsEvent."""
    player_name = get_player_name(event)
    data = player_data[player_name]
    time = event.second
    data["times"].append(time)
    data["minerals_collection_rate"].append(event.minerals_collection_rate)
    data["minerals_current"].append(event.minerals_current)
    data["minerals_used_current_army"].append(event.minerals_used_current_army)
    data["minerals_used_current_economy"].append(event.minerals_used_current_economy)
    data["minerals_used_current_technology"].append(event.minerals_used_current_technology)
    data["vespene_collection_rate"].append(event.vespene_collection_rate)
    data["vespene_current"].append(event.vespene_current)
    data["vespene_used_current_army"].append(event.vespene_used_current_army)
    data["vespene_used_current_economy"].append(event.vespene_used_current_economy)
    data["vespene_used_current_technology"].append(event.vespene_used_current_technology)
    data["army_value"].append(event.minerals_used_current_army + event.vespene_used_current_army)
    data["workers_active_count"].append(event.workers_active_count)
    data["food_made"].append(event.food_made)
    data["food_used"].append(event.food_used)


def update_unit_investment(player_data, player_name, unit_type, time, supply_change):
    """Update supply investment for a unit type."""
    if unit_type not in player_data[player_name]["unit_investment"]:
        player_data[player_name]["unit_investment"][unit_type] = [(0, 0)]
    investment = player_data[player_name]["unit_investment"][unit_type]
    last_count = investment[-1][1]
    new_count = max(0, last_count + supply_change)  # Ensure no negative supply
    investment.append((time, new_count))

def handle_basic_command(event, player_data, units_only):
    """Handle unit production start (birth trigger)."""
    player_name = get_player_name(event)
    if not player_name or player_name not in player_data:
        return
    ability = event.ability_name
    for morph, unit_type in morph_to_unit.items():
        if morph in ability and unit_type in units_only:
            supply = costs.get(unit_type, (0, 0, 0))[2]  # Get supply cost (3rd element)
            update_unit_investment(player_data, player_name, unit_type, event.second, supply)
            break

def handle_unit_born(event, player_data, units_only):
    """Handle Zerg unit birth from eggs or natural spawns."""
    player_name = get_player_name(event)
    if not player_name or player_name not in player_data or not hasattr(event, 'unit_type_name'):
        return
    unit_type = event.unit_type_name
    if unit_type in units_only:
        supply = costs.get(unit_type, (0, 0, 0))[2]
        update_unit_investment(player_data, player_name, unit_type, event.second, supply)

def handle_unit_type_change(event, player_data, units_only):
    """Handle unit transformations (potential death/birth)."""
    player_name = get_player_name(event)
    if not player_name or player_name not in player_data or not hasattr(event, 'unit_type_name'):
        return
    old_unit = event.unit.name  # Original unit
    new_unit = event.unit_type_name  # New unit type after change
    if "Egg" in new_unit and old_unit in units_only:  # e.g., Larva -> Egg (death of Larva)
        supply = costs.get(old_unit, (0, 0, 0))[2]
        update_unit_investment(player_data, player_name, old_unit, event.second, -supply)
    elif old_unit in ["HighTemplar", "DarkTemplar"] and new_unit == "Archon":  # Merging into Archon
        supply = costs.get(old_unit, (0, 0, 0))[2]
        update_unit_investment(player_data, player_name, old_unit, event.second, -supply)
        # Archon birth handled separately if needed

def handle_unit_init(event, player_data, units_only):
    """Handle non-Zerg unit/building start (birth trigger)."""
    player_name = get_player_name(event)
    if not player_name or player_name not in player_data or not hasattr(event, 'unit'):
        return
    unit_type = event.unit.name
    if unit_type in units_only and event.unit.owner.play_race != "Zerg":  # Skip Zerg here
        supply = costs.get(unit_type, (0, 0, 0))[2]
        update_unit_investment(player_data, player_name, unit_type, event.second, supply)

def handle_unit_done(event, player_data, units_only):
    """Handle non-Zerg unit/building completion (optional confirmation)."""
    # Often redundant with BasicCommandEvent/UnitInitEvent, so we'll skip unless needed
    pass

def handle_unit_died(event, player_data, units_only):
    """Handle unit death."""
    player_name = get_player_name(event)
    if not player_name or player_name not in player_data or not hasattr(event, 'unit'):
        return
    unit_type = event.unit.name
    if unit_type in units_only:
        supply = costs.get(unit_type, (0, 0, 0))[2]
        update_unit_investment(player_data, player_name, unit_type, event.second, -supply)

def handle_upgrade_complete(event, player_data, units_only):
    """Handle upgrade completion (no supply impact, placeholder)."""
    pass  # Upgrades don’t affect unit supply, but we’ll keep it for future use

# Event parsing
def parse_events(replay, player_data):
    """Parse replay events and extract relevant data."""
    event_handlers = {
        "PlayerStatsEvent": handle_player_stats,
        "UpgradeCompleteEvent": handle_upgrade_complete,
        "UnitBornEvent": handle_unit_born,
        "UnitTypeChangeEvent": handle_unit_type_change,
        "BasicCommandEvent": handle_basic_command,
        "UnitInitEvent": handle_unit_init,
        "UnitDoneEvent": handle_unit_done,
        "UnitDiedEvent": handle_unit_died
    }
    
    
    for event in replay.events:
        if event.name in relevant_events.keys():
            handler = event_handlers[event.name]
            if event.name == "PlayerStatsEvent":
                handler(event, player_data)
            else:  # PlayerStatsEvent, UpgradeCompleteEvent
                handler(event, player_data, unit_list)
    
    # Clean up unit_investment: remove units with no investment
    for player_name in player_data:
        investment = player_data[player_name]["unit_investment"]
        # Keep only units where supply count ever exceeds 0
        player_data[player_name]["unit_investment"] = {
            unit_type: history for unit_type, history in investment.items()
            if any(count > 0 for _, count in history)
        }
    return player_data
