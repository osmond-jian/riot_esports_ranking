const fs = require('fs');

//takes in an array with tournament IDs, and returns the game metadata for the tournaments.

//NOTE: This function currently uses the node.fs package to directly access the files synchronously
function getTournamentsFromLeagueId(id) {
    const data = fs.readFileSync('esports-data/leagues.json', {encoding:'utf8', flag: 'r'})
      const leagueArray = JSON.parse(data).filter((obj) => obj.id === id);
    //   console.log(leagueArray[0].tournaments);
      return leagueArray[0].tournaments;
  }
  

// getTournamentsFromLeagueId("98767975604431411"); //worlds
// getTournamentsFromLeagueId("98767991299243165"); //test

module.exports = { getTournamentsFromLeagueId }