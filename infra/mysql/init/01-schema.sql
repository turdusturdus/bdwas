
CREATE TABLE countries (
    country_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    flag_url VARCHAR(255)
);

CREATE TABLE stadiums (
    stadium_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    capacity INT
);

CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE coaches (
    coach_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nationality_id INT,
    CONSTRAINT fk_coach_nationality FOREIGN KEY (nationality_id) REFERENCES countries (country_id) ON DELETE SET NULL
);

CREATE TABLE referees (
    referee_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    nationality_id INT,
    CONSTRAINT fk_referee_nationality FOREIGN KEY (nationality_id) REFERENCES countries (country_id) ON DELETE SET NULL
);

CREATE TABLE leagues (
    league_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country_id INT,
    icon_url VARCHAR(255),
    cl_spot INT,
    uel_spot INT,
    relegation_spot INT,
    UNIQUE (name, country_id),
    CONSTRAINT fk_league_country FOREIGN KEY (country_id) REFERENCES countries (country_id) ON DELETE RESTRICT
);

CREATE TABLE seasons (
    season_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    league_id INT NOT NULL,
    `year` VARCHAR(9) NOT NULL,
    UNIQUE (league_id, `year`),
    CONSTRAINT fk_season_league FOREIGN KEY (league_id) REFERENCES leagues (league_id) ON DELETE CASCADE
);

CREATE TABLE teams (
    team_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    founded_year INT,
    stadium_id INT,
    coach_id INT,
    crest_url VARCHAR(255),
    CONSTRAINT fk_team_stadium FOREIGN KEY (stadium_id) REFERENCES stadiums (stadium_id) ON DELETE SET NULL,
    CONSTRAINT fk_team_coach FOREIGN KEY (coach_id) REFERENCES coaches (coach_id) ON DELETE SET NULL
);

CREATE TABLE players (
    player_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    team_id INT,
    name VARCHAR(255) NOT NULL,
    `position` VARCHAR(50),
    date_of_birth DATE,
    nationality_id INT,
    CONSTRAINT fk_player_team FOREIGN KEY (team_id) REFERENCES teams (team_id) ON DELETE SET NULL,
    CONSTRAINT fk_player_nationality FOREIGN KEY (nationality_id) REFERENCES countries (country_id) ON DELETE RESTRICT
);

CREATE TABLE matches (
    match_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    season_id INT NOT NULL,
    matchday INT,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    winner VARCHAR(50),
    `utc_date` DATE,
    CONSTRAINT check_teams_not_same CHECK (home_team_id <> away_team_id),
    CONSTRAINT fk_match_season FOREIGN KEY (season_id) REFERENCES seasons (season_id) ON DELETE CASCADE,
    CONSTRAINT fk_match_home FOREIGN KEY (home_team_id) REFERENCES teams (team_id) ON DELETE RESTRICT,
    CONSTRAINT fk_match_away FOREIGN KEY (away_team_id) REFERENCES teams (team_id) ON DELETE RESTRICT
);

CREATE TABLE match_statistics (
    stat_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    stat_key VARCHAR(50) NOT NULL,
    stat_value VARCHAR(255) NOT NULL,
    CONSTRAINT fk_stats_match FOREIGN KEY (match_id) REFERENCES matches (match_id) ON DELETE CASCADE
);

CREATE TABLE scores (
    score_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL UNIQUE,
    full_time_home INT,
    full_time_away INT,
    half_time_home INT,
    half_time_away INT,
    CONSTRAINT fk_score_match FOREIGN KEY (match_id) REFERENCES matches (match_id) ON DELETE CASCADE
);

CREATE TABLE match_referees (
    match_id INT NOT NULL,
    referee_id INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (match_id, referee_id),
    CONSTRAINT fk_mr_match FOREIGN KEY (match_id) REFERENCES matches (match_id) ON DELETE CASCADE,
    CONSTRAINT fk_mr_referee FOREIGN KEY (referee_id) REFERENCES referees (referee_id) ON DELETE RESTRICT
);

CREATE TABLE standings (
    standing_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    season_id INT NOT NULL,
    team_id INT NOT NULL,
    `position` INT NOT NULL,
    played_games INT NOT NULL,
    won INT NOT NULL,
    draw INT NOT NULL,
    lost INT NOT NULL,
    points INT NOT NULL,
    goals_for INT NOT NULL,
    goals_against INT NOT NULL,
    goal_difference INT NOT NULL,
    UNIQUE (season_id, team_id),
    CONSTRAINT fk_standing_season FOREIGN KEY (season_id) REFERENCES seasons (season_id) ON DELETE CASCADE,
    CONSTRAINT fk_standing_team FOREIGN KEY (team_id) REFERENCES teams (team_id) ON DELETE CASCADE
);

CREATE TABLE standings_form (
    form_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    standing_id INT NOT NULL,
    result CHAR(1) NOT NULL,
    sequence_order INT NOT NULL,
    CONSTRAINT fk_form_standing FOREIGN KEY (standing_id) REFERENCES standings (standing_id) ON DELETE CASCADE
);

CREATE TABLE scorers (
    scorer_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    season_id INT NOT NULL,
    goals INT,
    assists INT,
    penalties INT,
    UNIQUE (player_id, season_id),
    CONSTRAINT fk_scorer_player FOREIGN KEY (player_id) REFERENCES players (player_id) ON DELETE CASCADE,
    CONSTRAINT fk_scorer_season FOREIGN KEY (season_id) REFERENCES seasons (season_id) ON DELETE CASCADE
);