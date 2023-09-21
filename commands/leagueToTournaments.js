const fs = require('fs');

// async function getTournamentsFromLeagueId (id) {
//     try {
//         const data = await fs.readFile('esports-data/leagues.json', function(error,data){
//             if (error) throw error;
//             const league = JSON.parse(data).filter((obj) => obj.id === id);
//             // console.log(league[0].tournaments);
//             return league[0].tournaments;
//         })
//     } catch (error) {
//         console.error("Error!", error);
//         throw error;
//     }
// }

//takes in an array with tournament IDs, and returns the game metadata for the tournaments.
function getTournamentsFromLeagueId(id) {
    const data = fs.readFileSync('esports-data/leagues.json', {encoding:'utf8', flag: 'r'})
      const leagueArray = JSON.parse(data).filter((obj) => obj.id === id);
    //   console.log(leagueArray[0].tournaments);
      return leagueArray[0].tournaments;
  }
  

// getTournamentsFromLeagueId("98767975604431411"); //worlds
// getTournamentsFromLeagueId("98767991299243165"); //test

module.exports = {getTournamentsFromLeagueId}