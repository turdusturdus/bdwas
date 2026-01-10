TRUNCATE TABLE
    public.scorers,
    public.standings,
    public.match_referees,
    public.scores,
    public.matches,
    public.players,
    public.teams,
    public.seasons,
    public.leagues,
    public.referees,
    public.coaches,
    public.users,
    public.stadiums,
    public.countries
RESTART IDENTITY CASCADE;

INSERT INTO public.countries (country_id, name, flag_url) VALUES
(1, 'England', 'https://flags.com/eng.png'),
(2, 'Spain', 'https://flags.com/esp.png'),
(3, 'Poland', 'https://flags.com/pol.png'),
(4, 'Germany', 'https://flags.com/ger.png'),
(5, 'France', 'https://flags.com/fra.png'),
(6, 'Italy', 'https://flags.com/ita.png'),
(7, 'Portugal', 'https://flags.com/por.png'),
(8, 'Brazil', 'https://flags.com/bra.png'),
(9, 'Argentina', 'https://flags.com/arg.png');

INSERT INTO public.stadiums (stadium_id, name, location, capacity) VALUES
(1, 'Old Trafford', 'Manchester', 74310),
(2, 'Etihad Stadium', 'Manchester', 53400),
(3, 'Camp Nou', 'Barcelona', 99354),
(4, 'Santiago Bernabéu', 'Madrid', 81044),
(5, 'Stadion Narodowy', 'Warsaw', 58580),
(6, 'Stadion Wojska Polskiego', 'Warsaw', 31103),
(7, 'Anfield', 'Liverpool', 61276),
(8, 'Emirates Stadium', 'London', 60704),
(9, 'Allianz Arena', 'Munich', 75024);

INSERT INTO public.coaches (coach_id, name, nationality_id) VALUES
(1, 'Pep Guardiola', 2),
(2, 'Erik ten Hag', 1),
(3, 'Xavi Hernandez', 2),
(4, 'Carlo Ancelotti', 6),
(5, 'Jurgen Klopp', 4),
(6, 'Mikel Arteta', 2),
(7, 'Kosta Runjaić', 4),
(8, 'Michał Probierz', 3);

INSERT INTO public.referees (referee_id, name, nationality_id) VALUES
(1, 'Szymon Marciniak', 3),
(2, 'Michael Oliver', 1),
(3, 'Anthony Taylor', 1),
(4, 'Antonio Mateu Lahoz', 2),
(5, 'Daniele Orsato', 6);

INSERT INTO public.leagues (league_id, name, country_id, icon_url, cl_spot, uel_spot, relegation_spot) VALUES
(1, 'Premier League', 1, 'pl_logo.png', 4, 2, 3),
(2, 'La Liga', 2, 'laliga_logo.png', 4, 2, 3),
(3, 'Ekstraklasa', 3, 'esa_logo.png', 1, 2, 3),
(4, 'Bundesliga', 4, 'bundes_logo.png', 4, 2, 2);

INSERT INTO public.seasons (season_id, league_id, year) VALUES
(100, 1, '2023/2024'),
(101, 2, '2023/2024'),
(102, 3, '2023/2024');

INSERT INTO public.teams (team_id, name, founded_year, stadium_id, coach_id, crest_url) VALUES
(10, 'Manchester United', 1878, 1, 2, 'manutd.png'),
(11, 'Manchester City', 1880, 2, 1, 'mancity.png'),
(12, 'Liverpool FC', 1892, 7, 5, 'lfc.png'),
(13, 'Arsenal FC', 1886, 8, 6, 'afc.png'),
(20, 'FC Barcelona', 1899, 3, 3, 'barca.png'),
(21, 'Real Madrid', 1902, 4, 4, 'real.png'),
(30, 'Legia Warszawa', 1916, 6, 7, 'legia.png'),
(31, 'Lech Poznań', 1922, null, null, 'lech.png');

INSERT INTO public.players (player_id, team_id, name, "position", date_of_birth, nationality_id) VALUES
(1001, 10, 'Bruno Fernandes', 'Midfielder', '1994-09-08', 7),
(1002, 10, 'Marcus Rashford', 'Forward', '1997-10-31', 1),
(1003, 11, 'Erling Haaland', 'Forward', '2000-07-21', 1),
(1004, 11, 'Kevin De Bruyne', 'Midfielder', '1991-06-28', 1),
(1005, 12, 'Mohamed Salah', 'Forward', '1992-06-15', 1),
(1006, 12, 'Virgil van Dijk', 'Defender', '1991-07-08', 1),
(1007, 13, 'Bukayo Saka', 'Forward', '2001-09-05', 1),
(1008, 13, 'Martin Odegaard', 'Midfielder', '1998-12-17', 1),
(2001, 20, 'Robert Lewandowski', 'Forward', '1988-08-21', 3),
(2002, 20, 'Pedri', 'Midfielder', '2002-11-25', 2),
(2003, 21, 'Vinicius Junior', 'Forward', '2000-07-12', 8),
(2004, 21, 'Jude Bellingham', 'Midfielder', '2003-06-29', 1),
(3001, 30, 'Josue', 'Midfielder', '1990-09-17', 7);

INSERT INTO public.matches (match_id, season_id, matchday, home_team_id, away_team_id, winner, utc_date, statistics) VALUES
(5001, 100, 1, 11, 12, 'HOME_TEAM', '2023-08-11', '{"possession_home": 60, "possession_away": 40, "xg_home": 2.5, "xg_away": 1.1}'),
(5002, 100, 1, 13, 10, 'DRAW', '2023-08-12', '{"possession_home": 55, "possession_away": 45, "xg_home": 1.2, "xg_away": 1.3}'),
(5003, 101, 1, 21, 20, 'AWAY_TEAM', '2023-08-12', '{"possession_home": 48, "possession_away": 52, "xg_home": 0.8, "xg_away": 2.1}');

INSERT INTO public.scores (score_id, match_id, full_time, half_time) VALUES
(1, 5001, (3, 1), (1, 0)),
(2, 5002, (2, 2), (0, 1)),
(3, 5003, (0, 2), (0, 1));

INSERT INTO public.match_referees (match_id, referee_id, role) VALUES
(5001, 2, 'MAIN_REFEREE'),
(5002, 3, 'MAIN_REFEREE'),
(5003, 4, 'MAIN_REFEREE');

INSERT INTO public.scorers (scorer_id, player_id, season_id, goals, assists, penalties) VALUES
(1, 1003, 100, 2, 0, 0),
(2, 1005, 100, 1, 0, 0),
(3, 1007, 100, 1, 1, 0),
(4, 2001, 101, 2, 0, 1);

INSERT INTO public.standings
(standing_id, season_id, team_id, "position", played_games, won, draw, lost, points, goals_for, goals_against, goal_difference, form)
VALUES
(1, 100, 11, 1, 1, 1, 0, 0, 3, 3, 1, 2, ARRAY['W']),
(2, 100, 13, 2, 1, 0, 1, 0, 1, 2, 2, 0, ARRAY['D']),
(3, 100, 10, 3, 1, 0, 1, 0, 1, 2, 2, 0, ARRAY['D']),
(4, 100, 12, 4, 1, 0, 0, 1, 0, 1, 3, -2, ARRAY['L']),
(5, 101, 20, 1, 1, 1, 0, 0, 3, 2, 0, 2, ARRAY['W']),
(6, 101, 21, 2, 1, 0, 0, 1, 0, 0, 2, -2, ARRAY['L']);