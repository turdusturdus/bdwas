db = db.getSiblingDB("football_app");
print("Using DB:", db.getName());

// Stałe ObjectId (zgodne z mock_repo i testami)
const PL = ObjectId("507f1f77bcf86cd799439001");
const GB = ObjectId("507f1f77bcf86cd799439002");

const leaguePL = ObjectId("507f1f77bcf86cd799439011");

const teamA = ObjectId("507f1f77bcf86cd799439101");
const teamB = ObjectId("507f1f77bcf86cd799439102");

const p1 = ObjectId("507f1f77bcf86cd799439201");
const p2 = ObjectId("507f1f77bcf86cd799439202");

const season = ObjectId("507f1f77bcf86cd799439401");
const referee = ObjectId("507f1f77bcf86cd799439501");

const match1 = ObjectId("507f1f77bcf86cd799439301");

// Czyścimy, żeby seed był idempotentny (do testów)
db.countries.deleteMany({});
db.leagues.deleteMany({});
db.teams.deleteMany({});
db.players.deleteMany({});
db.seasons.deleteMany({});
db.referees.deleteMany({});
db.matches.deleteMany({});

db.countries.insertMany([
  { _id: PL, name: "Polska", flagUrl: "https://example.com/pl.png" },
  { _id: GB, name: "Anglia", flagUrl: "https://example.com/gb.png" },
]);

db.leagues.insertOne({
  _id: leaguePL,
  name: "Ekstraklasa",
  countryId: PL,
  iconUrl: "https://example.com/ekstraklasa.png",
  europeanSpots: { championsLeague: 1, europaLeague: 2, relegation: 3 }
});

db.teams.insertMany([
  {
    _id: teamA,
    name: "Legia Warszawa",
    foundedYear: 1916,
    crestUrl: "https://example.com/legia.png",
    countryId: PL,
    leagueId: leaguePL,
    stadium: { name: "Stadion A", location: "Warszawa", capacity: 30000 },
    coach: { name: "Trener A", nationalityId: PL }
  },
  {
    _id: teamB,
    name: "Lech Poznań",
    foundedYear: 1922,
    crestUrl: "https://example.com/lech.png",
    countryId: PL,
    leagueId: leaguePL,
    stadium: { name: "Stadion B", location: "Poznań", capacity: 40000 },
    coach: { name: "Trener B", nationalityId: PL }
  }
]);

db.players.insertMany([
  { _id: p1, name: "Jan Kowalski", position: "FW", dateOfBirth: ISODate("1999-01-01"), nationalityId: PL, currentTeamId: teamA },
  { _id: p2, name: "Piotr Nowak", position: "MF", dateOfBirth: ISODate("2000-02-02"), nationalityId: PL, currentTeamId: teamB },
]);

db.seasons.insertOne({
  _id: season,
  leagueId: leaguePL,
  year: "2024/2025",
  standings: [
    { teamId: teamA, position: 1, playedGames: 12, won: 8, draw: 2, lost: 2, points: 26, goalsFor: 22, goalsAgainst: 10, goalDifference: 12, form: ["W","W","D","L","W"] },
    { teamId: teamB, position: 2, playedGames: 12, won: 7, draw: 2, lost: 3, points: 23, goalsFor: 18, goalsAgainst: 12, goalDifference: 6, form: ["W","D","W","W","L"] }
  ],
  topScorers: [
    { playerId: p1, teamId: teamA, goals: 10, assists: 2, penalties: 1 }
  ]
});

db.referees.insertOne({ _id: referee, name: "Sędzia X", nationalityId: PL });

db.matches.insertOne({
  _id: match1,
  utcDate: ISODate("2025-01-10T18:00:00Z"),
  matchday: 12,
  seasonId: season,
  homeTeamId: teamA,
  awayTeamId: teamB,
  score: {
    halfTime: { home: 1, away: 0 },
    fullTime: { home: 2, away: 1 },
    winner: "HOME_TEAM"
  },
  statistics: { possession: { home: 55, away: 45 } },
  referees: [{ role: "MAIN", refereeId: referee }]
});
