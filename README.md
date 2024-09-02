# Unofficial Valorant Champions Tour REST API

![banner_picture](banner.jpg)


## Table of Contents

- [About](#about)
- [Endpoints](#endpoints)
- [To-Do List](#to_do_list)
- [Built With](#built_with)

## About <a name = "about"></a>
This README provides detailed information about the unofficial Valorant Champions Tour API, an API that provides general stats for agents, players, and maps.
## Endpoints <a name = "endpoints"></a>

### Tournaments

#### /tournaments

- Method: GET
- Description: Get all the tournaments and its IDs grouped by the year

#### /tournaments/{identifier}

- Method: GET
- Description: Get the tournament and its ID based on either the name or the ID
- Parameters:
    - identifier: The name or the ID (e.g., "Champions Tour Asia-Pacific: Last Chance Qualifier" or 560)

#### /tournaments/pool
- Method: GET
- Description: Get all the tournaments grouped by the year and the stages

### Maps

#### /maps

- Method: GET
- Description: Get all the maps and its IDs

#### /maps/{identifier}
- Method: GET
- Description: Get the map and its ID based on either the name or the ID
- Parameters:
    - identifier: The name or the ID (e.g., "Bind" or 381)

#### /maps/pool

- Method: GET
- Description: Get all the maps that were played grouped by the year and the stages

### Players

#### /players

- Method: GET
- Description: Get all the players and their IDs

#### /players/{identifier}
- Method: GET
- Description: Get the player and their ID based on either the name or the ID
- Parameters:
    - identifier: The name or the ID (e.g., "MaKo" or 4462)


#### /players/search?name={name}

- Method: GET
- Description: Get the players and their IDs that are similar match to the name provided
- Parameters:
    - identifier: The name or the ID (e.g., "Ma")

### Teams

#### /teams

- Method: GET
- Description: Get all the teams and their IDs

#### /teams/{identifier}

- Method: GET
- Description: Get the team and their ID based on either the name or the ID
- Parameters:
    - identifier: The name or the ID (e.g., "Cloud9" or 188)


#### /teams/search?name={name}

- Method: GET
- Description: Get the teams and their IDs that are similar match to the name provided
- Parameters:
    - identifier: The name (e.g., "Cloud9")

### Maps Stats

#### /maps-stats/wr

#### /maps-stats/wr/team/{team_id}

#### /maps-stats/trends/wr

#### /maps-stats/trends/wr/team/{team_id}

### Pick Bans (Maps)

#### /pick-bans

#### /pick-bans/team/{team_id}

#### /pick-bans/trends

#### /pick-bands/trends/{team_id}

### Team Composition

#### /team-comp

#### /team-comp/team/{team_id}

#### /team-comp/trends

#### /team-comp/trends/team/{team_id}


## Built With <a name="built_with"></a>
- [FastAPI](https://fastapi.tiangolo.com/)
