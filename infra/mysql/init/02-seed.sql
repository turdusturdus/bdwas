
SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO countries (country_id, name, flag_url) VALUES
(1, 'England', 'https://example.com/flags/england.png'),
(2, 'Spain', 'https://example.com/flags/spain.png'),
(3, 'Norway', 'https://example.com/flags/norway.png'),
(4, 'Egypt', 'https://example.com/flags/egypt.png'),
(5, 'Portugal', 'https://example.com/flags/portugal.png'),
(6, 'Brazil', 'https://example.com/flags/brazil.png');

INSERT INTO stadiums (stadium_id, name, location, capacity) VALUES
(1, 'Etihad Stadium', 'Manchester', 53400),
(2, 'Anfield', 'Liverpool', 61276),
(3, 'Old Trafford', 'Manchester', 74310),
(4, 'Emirates Stadium', 'London', 60704);

INSERT INTO users (username, password, email, is_admin) VALUES
('admin_user', '$2b$12$EixZaYVK1fs6NpE.PmsZDO...hashed_password...', 'admin@system.com', TRUE),
('john_doe', '$2b$12$R9h/cIPz0gi.URNNXGd6CP...hashed_password...', 'john@example.com', FALSE);

INSERT INTO coaches (coach_id, name, nationality_id) VALUES
(1, 'Pep Guardiola', 2),
(2, 'Jurgen Klopp', 1),
(3, 'Erik ten Hag', 1),
(4, 'Mikel Arteta', 2);

INSERT INTO referees (referee_id, name, nationality_id) VALUES
(1, 'Michael Oliver', 1),
(2, 'Anthony Taylor', 1);

INSERT INTO leagues (league_id, name, country_id, icon_url, cl_spot, uel_spot, relegation_spot) VALUES
(1, 'Premier League', 1, 'https://example.com/leagues/pl.png', 4, 2, 3);

INSERT INTO seasons (season_id, league_id, `year`) VALUES
(1, 1, '2023-2024');

INSERT INTO teams (team_id, name, founded_year, stadium_id, coach_id, crest_url) VALUES
(1, 'Manchester City', 1880, 1, 1, 'https://example.com/crests/mancity.png'),
(2, 'Liverpool FC', 1892, 2, 2, 'https://example.com/crests/liverpool.png'),
(3, 'Manchester United', 1878, 3, 3, 'https://example.com/crests/manutd.png'),
(4, 'Arsenal FC', 1886, 4, 4, 'https://example.com/crests/arsenal.png');

INSERT INTO players (player_id, team_id, name, `position`, date_of_birth, nationality_id) VALUES
(1, 1, 'Erling Haaland', 'Forward', '2000-07-21', 3),
(2, 1, 'Kevin De Bruyne', 'Midfielder', '1991-06-28', 1),
(3, 2, 'Mohamed Salah', 'Forward', '1992-06-15', 4),
(4, 2, 'Virgil van Dijk', 'Defender', '1991-07-08', 1),
(5, 3, 'Bruno Fernandes', 'Midfielder', '1994-09-08', 5),
(6, 3, 'Marcus Rashford', 'Forward', '1997-10-31', 1),
(7, 4, 'Bukayo Saka', 'Forward', '2001-09-05', 1),
(8, 4, 'Martin Odegaard', 'Midfielder', '1998-12-17', 3);

INSERT INTO matches (match_id, season_id, matchday, home_team_id, away_team_id, winner, `utc_date`) VALUES
(1, 1, 13, 1, 2, 'DRAW', '2023-11-25'),
(2, 1, 4, 4, 3, 'HOME_TEAM', '2023-09-03'),
(3, 1, 10, 3, 1, 'AWAY_TEAM', '2023-10-29');

INSERT INTO scores (match_id, full_time_home, full_time_away, half_time_home, half_time_away) VALUES
(1, 1, 1, 1, 0),
(2, 3, 1, 1, 1),
(3, 0, 3, 0, 1);

INSERT INTO match_statistics (match_id, stat_key, stat_value) VALUES
(1, 'possession_home', '60%'),
(1, 'possession_away', '40%'),
(1, 'shots_on_target_home', '5'),
(1, 'shots_on_target_away', '3'),
(2, 'possession_home', '55%'),
(2, 'possession_away', '45%');

INSERT INTO match_referees (match_id, referee_id, role) VALUES
(1, 1, 'HEAD_REFEREE'),
(2, 2, 'HEAD_REFEREE'),
(3, 1, 'HEAD_REFEREE');

INSERT INTO scorers (player_id, season_id, goals, assists, penalties) VALUES
(1, 1, 27, 5, 7),
(3, 1, 18, 10, 4),
(5, 1, 10, 8, 3),
(7, 1, 16, 9, 2);

INSERT INTO standings (season_id, team_id, `position`, played_games, won, draw, lost, points, goals_for, goals_against, goal_difference) VALUES
(1, 1, 1, 2, 1, 1, 0, 4, 4, 1, 3),
(1, 4, 2, 1, 1, 0, 0, 3, 3, 1, 2),
(1, 2, 3, 1, 0, 1, 0, 1, 1, 1, 0),
(1, 3, 4, 2, 0, 0, 2, 0, 1, 6, -5);

INSERT INTO standings_form (standing_id, result, sequence_order) VALUES
(1, 'D', 1),
(1, 'W', 2),
(2, 'W', 1),
(3, 'D', 1),
(4, 'L', 1),
(4, 'L', 2);

SET FOREIGN_KEY_CHECKS = 1;