db = db.getSiblingDB("football_app");
print("Using DB:", db.getName());


// ---------- COUNTRIES ----------
db.createCollection("countries", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "flagUrl"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string", minLength: 1 },
        flagUrl: { bsonType: "string", minLength: 1 }
      }
    }
  }
});
db.countries.createIndex({ name: 1 }, { unique: true });

// ---------- USERS ----------
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "passwordHash", "email", "roles", "createdAt"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        username: { bsonType: "string", minLength: 3, maxLength: 32 },
        passwordHash: { bsonType: "string", minLength: 20 },
        email: { bsonType: "string", minLength: 5 },
        roles: { bsonType: "array", items: { bsonType: "string" }, minItems: 1 },
        createdAt: { bsonType: "date" },
        lastLoginAt: { bsonType: ["date", "null"] }
      }
    }
  }
});
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });

// ---------- LEAGUES ----------
db.createCollection("leagues", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "countryId", "iconUrl", "europeanSpots"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string", minLength: 1 },
        countryId: { bsonType: "objectId" },
        iconUrl: { bsonType: "string" },
        europeanSpots: {
          bsonType: "object",
          required: ["championsLeague", "europaLeague", "relegation"],
          additionalProperties: false,
          properties: {
            championsLeague: { bsonType: "int", minimum: 0 },
            europaLeague: { bsonType: "int", minimum: 0 },
            relegation: { bsonType: "int", minimum: 0 }
          }
        }
      }
    }
  }
});
db.leagues.createIndex({ name: 1, countryId: 1 }, { unique: true });
db.leagues.createIndex({ countryId: 1 });

// ---------- TEAMS ----------
// Dla Twojego UI potrzebne leagueId (filtr "drużyny w lidze")
db.createCollection("teams", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "foundedYear", "crestUrl", "countryId", "leagueId", "stadium", "coach"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string", minLength: 1 },
        foundedYear: { bsonType: "int", minimum: 1800, maximum: 2100 },
        crestUrl: { bsonType: "string" },
        countryId: { bsonType: "objectId" },
        leagueId: { bsonType: "objectId" },
        stadium: {
          bsonType: "object",
          required: ["name", "location", "capacity"],
          additionalProperties: false,
          properties: {
            name: { bsonType: "string", minLength: 1 },
            location: { bsonType: "string", minLength: 1 },
            capacity: { bsonType: "int", minimum: 0 }
          }
        },
        coach: {
          bsonType: "object",
          required: ["name", "nationalityId"],
          additionalProperties: false,
          properties: {
            name: { bsonType: "string", minLength: 1 },
            nationalityId: { bsonType: "objectId" }
          }
        }
      }
    }
  }
});
db.teams.createIndex({ leagueId: 1 });
db.teams.createIndex({ countryId: 1 });
db.teams.createIndex({ name: 1, countryId: 1 }, { unique: true });

// ---------- PLAYERS ----------
db.createCollection("players", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "position", "dateOfBirth", "nationalityId", "currentTeamId"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string", minLength: 1 },
        position: { bsonType: "string", minLength: 1 },
        dateOfBirth: { bsonType: "date" },
        nationalityId: { bsonType: "objectId" },
        currentTeamId: { bsonType: "objectId" }
      }
    }
  }
});
db.players.createIndex({ currentTeamId: 1 });
db.players.createIndex({ nationalityId: 1 });
db.players.createIndex({ name: 1 });

// ---------- SEASONS ----------
db.createCollection("seasons", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["leagueId", "year", "standings", "topScorers"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        leagueId: { bsonType: "objectId" },
        year: { bsonType: "string", minLength: 4, maxLength: 9 },
        standings: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["teamId", "position", "playedGames", "won", "draw", "lost", "points", "goalsFor", "goalsAgainst", "goalDifference", "form"],
            additionalProperties: false,
            properties: {
              teamId: { bsonType: "objectId" },
              position: { bsonType: "int", minimum: 1 },
              playedGames: { bsonType: "int", minimum: 0 },
              won: { bsonType: "int", minimum: 0 },
              draw: { bsonType: "int", minimum: 0 },
              lost: { bsonType: "int", minimum: 0 },
              points: { bsonType: "int", minimum: 0 },
              goalsFor: { bsonType: "int", minimum: 0 },
              goalsAgainst: { bsonType: "int", minimum: 0 },
              goalDifference: { bsonType: "int" },
              form: { bsonType: "array", items: { bsonType: "string" } }
            }
          }
        },
        topScorers: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["playerId", "teamId", "goals", "assists", "penalties"],
            additionalProperties: false,
            properties: {
              playerId: { bsonType: "objectId" },
              teamId: { bsonType: "objectId" },
              goals: { bsonType: "int", minimum: 0 },
              assists: { bsonType: "int", minimum: 0 },
              penalties: { bsonType: "int", minimum: 0 }
            }
          }
        }
      }
    }
  }
});
db.seasons.createIndex({ leagueId: 1, year: 1 }, { unique: true });

// ---------- REFEREES ----------
db.createCollection("referees", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "nationalityId"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string", minLength: 1 },
        nationalityId: { bsonType: "objectId" }
      }
    }
  }
});
db.referees.createIndex({ name: 1 });
db.referees.createIndex({ nationalityId: 1 });

// ---------- MATCHES ----------
db.createCollection("matches", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["seasonId", "matchday", "utcDate", "homeTeamId", "awayTeamId", "score", "referees"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        seasonId: { bsonType: "objectId" },
        matchday: { bsonType: "int", minimum: 1 },
        utcDate: { bsonType: "date" },
        homeTeamId: { bsonType: "objectId" },
        awayTeamId: { bsonType: "objectId" },
        score: {
          bsonType: "object",
          required: ["fullTime", "halfTime", "winner"],
          additionalProperties: false,
          properties: {
            fullTime: {
              bsonType: "object",
              required: ["home", "away"],
              additionalProperties: false,
              properties: {
                home: { bsonType: ["int", "null"], minimum: 0 },
                away: { bsonType: ["int", "null"], minimum: 0 }
              }
            },
            halfTime: {
              bsonType: "object",
              required: ["home", "away"],
              additionalProperties: false,
              properties: {
                home: { bsonType: ["int", "null"], minimum: 0 },
                away: { bsonType: ["int", "null"], minimum: 0 }
              }
            },
            winner: { bsonType: ["string", "null"] }
          }
        },
        statistics: { bsonType: ["object", "null"] },
        referees: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["role", "refereeId"],
            additionalProperties: false,
            properties: {
              role: { bsonType: "string" },
              refereeId: { bsonType: "objectId" }
            }
          }
        }
      }
    }
  }
});
db.matches.createIndex({ seasonId: 1, matchday: 1 });
db.matches.createIndex({ utcDate: 1 });
db.matches.createIndex({ homeTeamId: 1, utcDate: 1 });
db.matches.createIndex({ awayTeamId: 1, utcDate: 1 });
db.matches.createIndex({ seasonId: 1, homeTeamId: 1, awayTeamId: 1, utcDate: 1 }, { unique: true });
