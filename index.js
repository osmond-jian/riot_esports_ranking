//this lets nodejs work with files
const fs = require('fs');
let targetYear = '2023';

// list of functions, written in javascript for now



//this function takes a gameID (specifically platformGameId) and returns some stats on the game
async function gameLookup (gameID){
  const gameFileName = gameID.replace(/:/g, '_');

  fs.readFile(`games/${gameFileName}.json`, function(error, data){
    if (error) throw error;
    const game = JSON.parse(data);
    console.log(game[0].participants);
  });
}

// async function tournamentLookup (leagueID){
//   //get tournament, and all the teams, and the records after putting in League ID(e.g. lcs)
//   let finalDataArray = [];
//   let finalData = {};

//   await fs.readFile('esports-data/tournaments.json', function(error, data){
//     if (error) throw error;
//     const tournamentLists = JSON.parse(data);
//     const year = tournamentLists.filter((obj)=> obj.startDate.includes(targetYear))
//     const finalFilterList = year.includes((obj) => obj.leagueId = leagueID);

//     if (finalFilterList) {
//       //check this, can probably refactor ):
//       finalFilterList.stages.forEach((object)=>{
//         object.sections.forEach((element)=>{
//           finalData.team1Id = element.matches[1].id
//           finalData.team1Record = element.matches[1].record
//           finalData.team2Id = element.matches[3].id
//           finalData.team2Record = element.matches[3].record
//           finalDataArray.push(finalData);
//         })
//         console.log(finalDataArray);
//         return(finalDataArray);
//       });
//     }
//   })
// }


//chatgpt was cooking here

async function tournamentLookup(leagueID) {
  return new Promise((resolve, reject) => {
    fs.readFile('esports-data/tournaments.json', function (error, data) {
      if (error) {
        reject(error);
      } else {
        const tournamentLists = JSON.parse(data);
        const year = tournamentLists.filter((obj) => obj.startDate.includes(targetYear));
        const finalFilterList = year.filter((obj) => obj.leagueId === leagueID);
        // console.log (JSON.stringify(finalFilterList));

        if (finalFilterList.length > 0) {
          const finalDataArray = [];
          finalFilterList.forEach((object) => {
            const name = object.slug;
            object.stages.forEach((stage) => {
              stage.sections.forEach((element) => {
                element.matches.forEach((element) => {
                // console.log(JSON.stringify(element.matches[1]));
                  finalDataArray.push({
                    name: name,
                    team1Id: element.teams[1].id,
                    team1Record: element.teams[1].record,
                  });
                })
              });
            });
          });
          console.log(finalDataArray);
          resolve(finalDataArray);
        } else {
          console.log('No matching tournaments found.');
          resolve([]);
        }
      }
    });
  });
}

async function teamsLookup (tournamentID) {

  fs.readFile('esports-data/teams.json', function(error, data){
    if(error) throw error;
    const teamLists = JSON.parse(data);
    return(teamLists)
  })
}

// gameLookup('ESPORTSTMNT01_3294091');
// tournamentLookup('98767991299243165');



// Call the function and handle the promises
tournamentLookup('98767991299243165')
  .then((data) => {
    // Do something with the data if needed
    console.log('Tournament Data:', data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });