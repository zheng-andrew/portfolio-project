"""FastAPI program - Chapter 4"""
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

import crud, schemas
from database import SessionLocal

api_description = """ 
This API provides read-only access to info from the SportsWorldCentral
(SWC) Fantasy Football API.
The endpoints are grouped into the following categories:

## Analytics
Get information about the health of the API and counts of leagues, teams,
and players.

## Player
You can get a list of NFL players, or search for an individual player by
player_id.

## Scoring
You can get a list of NFL player performances, including the fantasy points
they scored using SWC league scoring.

## Membership
Get information about all the SWC fantasy football leagues and the teams in them.
"""

#FastAPI constructor with additional details added for OpenAPI Specification
app = FastAPI(
    description=api_description, 
    title="Sports World Central (SWC) Fantasy Football API", 
    version="0.1" 
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", 
        summary="Test the root of the API",
        description="""You can call this API to check its health""", 
        response_description="A successful API health check", 
        operation_id="v0_root",
        tags = ["analytics"])
async def root():
    return {"message": "API health check successful"}


@app.get("/v0/players/",
        summary="Get a list of players",
        description="""This performs a query on the players,
        displaying players matching the criteria""", 
        response_description="A list of players", 
        operation_id="v0_get_players",
        response_model=list[schemas.Player], tags = ["player"])
def read_players(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
                limit: int = Query(100, description="The number of records to return after the skipped records."),
                minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
                first_name: str = Query(None, description="The first name of the players to return"),
                last_name: str = Query(None, description="The last name of the players to return"),
                db: Session = Depends(get_db)):
    players = crud.get_players(db, 
                skip=skip, 
                limit=limit, 
                min_last_changed_date=minimum_last_changed_date, 
                first_name=first_name, 
                last_name=last_name)
    return players


@app.get("/v0/players/{player_id}",
        summary="Get one player using the Player ID, which is internal to SWC",
        description="""If you have an SWC Player ID of a player from another API
        call such as v0_get_players, you can call this API
        using the player ID""", 
        response_description="One NFL player", 
        operation_id="v0_get_players_by_player_id",
        response_model=schemas.Player, tags = ["player"])
def read_player(player_id: int, 
                db: Session = Depends(get_db)):
    player = crud.get_player(db, 
                             player_id=player_id)
    if player is None:
        raise HTTPException(status_code=404, 
                            detail="Player not found")
    return player

@app.get("/v0/performances/",
        summary="Get a list of one player's performances",
        description="""This API call provides information on past performances including
        the week number and how many fantasy points were scored on that week.
        This can be displayed by another API call such as v0_get_players_by_player_id""", 
        response_description="A list of performances", 
        operation_id="v0_get_performances",
        response_model=list[schemas.Performance], tags = ["scoring"])
def read_performances(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
                limit: int = Query(100, description="The number of records to return after the skipped records."),
                minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
                db: Session = Depends(get_db)):
    performances = crud.get_performances(db, 
                skip=skip, 
                limit=limit, 
                min_last_changed_date=minimum_last_changed_date)
    return performances

@app.get("/v0/leagues/{league_id}",
        summary="Get details of one league",
        description="""This API call provides information on one league.
        It includes the league name, scoring type, and teams participating in the league""", 
        response_description="One league's details", 
        operation_id="v0_get_leagues_by_league_id",
        response_model=schemas.League, tags = ["membership"])
def read_league(league_id: int, 
                db: Session = Depends(get_db)):
    league = crud.get_league(db, league_id = league_id)
    if league is None:
        raise HTTPException(status_code=404, detail="League not found")
    return league


@app.get("/v0/leagues/",
        summary="Get a list of leagues",
        description="""This performs a query on the database,
        displaying leagues matching the criteria""", 
        response_description="A list of leagues", 
        operation_id="v0_get_leagues",
        response_model=list[schemas.League], tags = ["membership"])
def read_leagues(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
                limit: int = Query(100, description="The number of records to return after the skipped records."),
                minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
                league_name: str = Query(None, description = "The name of the leagues to return"),
                db: Session = Depends(get_db)):
    leagues = crud.get_leagues(db, 
                skip=skip, 
                limit=limit, 
                min_last_changed_date=minimum_last_changed_date, 
                league_name=league_name)
    return leagues

@app.get("/v0/teams/",
        summary="Get a list of temas",
        description="""This performs a query on the teams,
        displaying teams matching the criteria""", 
        response_description="A list of teams", 
        operation_id="v0_get_teams",
        response_model=list[schemas.Team], tags = ["membership"])
def read_teams(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
               limit: int = Query(100, description="The number of records to return after the skipped records."),
               minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
               team_name: str = Query(None, description = "The name of the teams to return"), 
               league_id: int = Query(None, description = "The id of the leagues to return"),
               db: Session = Depends(get_db)):
    teams = crud.get_teams(db, 
                skip=skip, 
                limit=limit, 
                min_last_changed_date=minimum_last_changed_date, 
                team_name=team_name,
                league_id=league_id)
    return teams


@app.get("/v0/counts/",
        summary="Get a series of counts",
        description="""This counts the number of players, teams, and leagues in the database""", 
        response_description="A series of counts", 
        operation_id="v0_get_counts",
        response_model=schemas.Counts, tags = ["analytics"])
def get_count(db: Session = Depends(get_db)):
    counts = schemas.Counts(
        league_count = crud.get_league_count(db),
        team_count = crud.get_team_count(db),
        player_count = crud.get_player_count(db))
    return counts

