

CREATE TYPE public.score_result AS (
    home integer,
    away integer
);

CREATE TABLE public.countries (
    country_id SERIAL PRIMARY KEY,
    name character varying(255) NOT NULL UNIQUE,
    flag_url character varying(255)
);

CREATE TABLE public.stadiums (
    stadium_id SERIAL PRIMARY KEY,
    name character varying(255) NOT NULL,
    location character varying(255) NOT NULL,
    capacity integer
);

CREATE TABLE public.users (
    user_id SERIAL PRIMARY KEY,
    username character varying(255) NOT NULL UNIQUE,
    password character varying(255) NOT NULL,
    email character varying(255) NOT NULL UNIQUE,
    is_admin boolean DEFAULT false
);

CREATE TABLE public.coaches (
    coach_id SERIAL PRIMARY KEY,
    name character varying(255) NOT NULL,
    nationality_id integer REFERENCES public.countries (country_id) ON DELETE SET NULL
);

CREATE TABLE public.referees (
    referee_id SERIAL PRIMARY KEY,
    name character varying(100),
    nationality_id integer REFERENCES public.countries (country_id) ON DELETE SET NULL
);

CREATE TABLE public.leagues (
    league_id SERIAL PRIMARY KEY,
    name character varying(255) NOT NULL,
    country_id integer REFERENCES public.countries (country_id) ON DELETE RESTRICT,
    icon_url character varying(255),
    cl_spot integer,
    uel_spot integer,
    relegation_spot integer,
    UNIQUE (name, country_id)
);

CREATE TABLE public.seasons (
    season_id SERIAL PRIMARY KEY,
    league_id integer NOT NULL REFERENCES public.leagues (league_id) ON DELETE CASCADE,
    year character varying(9) NOT NULL,
    UNIQUE (league_id, year)
);

CREATE TABLE public.teams (
    team_id SERIAL PRIMARY KEY,
    name character varying(255) NOT NULL UNIQUE,
    founded_year integer,
    stadium_id integer REFERENCES public.stadiums (stadium_id) ON DELETE SET NULL,
    coach_id integer REFERENCES public.coaches (coach_id) ON DELETE SET NULL,
    crest_url character varying(255)
);

CREATE TABLE public.players (
    player_id SERIAL PRIMARY KEY,
    team_id integer REFERENCES public.teams (team_id) ON DELETE SET NULL,
    name character varying(255) NOT NULL,
    "position" character varying(50),
    date_of_birth date,
    nationality_id integer REFERENCES public.countries (country_id) ON DELETE RESTRICT
);

CREATE TABLE public.matches (
    match_id SERIAL PRIMARY KEY,
    season_id integer NOT NULL REFERENCES public.seasons (season_id) ON DELETE CASCADE,
    matchday integer,
    home_team_id integer NOT NULL REFERENCES public.teams (team_id) ON DELETE RESTRICT,
    away_team_id integer NOT NULL REFERENCES public.teams (team_id) ON DELETE RESTRICT,
    winner character varying(50),
    utc_date date,
    statistics jsonb,
    CONSTRAINT check_teams_not_same CHECK (home_team_id <> away_team_id)
);

CREATE TABLE public.scores (
    score_id SERIAL PRIMARY KEY,
    match_id integer NOT NULL UNIQUE REFERENCES public.matches (match_id) ON DELETE CASCADE,
    full_time public.score_result,
    half_time public.score_result
);

CREATE TABLE public.match_referees (
    match_id integer NOT NULL REFERENCES public.matches (match_id) ON DELETE CASCADE,
    referee_id integer NOT NULL REFERENCES public.referees (referee_id) ON DELETE RESTRICT,
    role character varying(50) NOT NULL,
    PRIMARY KEY (match_id, referee_id)
);

CREATE TABLE public.standings (
    standing_id SERIAL PRIMARY KEY,
    season_id integer NOT NULL REFERENCES public.seasons (season_id) ON DELETE CASCADE,
    team_id integer NOT NULL REFERENCES public.teams (team_id) ON DELETE CASCADE,
    "position" integer NOT NULL,
    played_games integer NOT NULL,
    won integer NOT NULL,
    draw integer NOT NULL,
    lost integer NOT NULL,
    points integer NOT NULL,
    goals_for integer NOT NULL,
    goals_against integer NOT NULL,
    goal_difference integer NOT NULL,
    form character varying(1)[],
    UNIQUE (season_id, team_id)
);

CREATE TABLE public.scorers (
    scorer_id SERIAL PRIMARY KEY,
    player_id integer NOT NULL REFERENCES public.players (player_id) ON DELETE CASCADE,
    season_id integer NOT NULL REFERENCES public.seasons (season_id) ON DELETE CASCADE,
    goals integer,
    assists integer,
    penalties integer,
    UNIQUE (player_id, season_id)
);