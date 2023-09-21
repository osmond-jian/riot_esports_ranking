const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const { getTournamentsFromLeagueId } = require('./commands/leagueToTournaments');
const { tournamentLookup } = require('./commands/tournamentLookup');
const { rawDataToCookedData } = require('./commands/matchToDataArray');
// const { teamLookup } = require('./commands/teamLookup'); //may not need until it is called in future iterations



// Define the CSV writer and header names for the csv file
const csvWriter = createCsvWriter({
    path: 'output.csv', // Specify the output file name, should be in the same folder as index.js
    header: [
      { id: 'leagueName', title: 'League Name' },
      { id: 'date', title: 'Date' }, 
      { id: 'stageName', title: 'Stage' },
      { id: 'sectionName', title: 'Section' },     
      { id: 'gameOrder', title: 'Game Number' },
      { id: 'esportsGameId', title: 'Game Id' },
      { id: 'blueSideTeam', title: 'Blue Team' },
      { id: 'blueSideWin', title: 'Outcome' },
      { id: 'redSideTeam', title: 'Red Team' },
      { id: 'redSideWin', title: 'Outcome' },
    ],
  });

function godFunction (leagueId) {
    //input league Id (e.g. LCS), and get an array of tournament Ids (regular season, playoffs)
    const tournamentIds = getTournamentsFromLeagueId(leagueId);
    //input array of tournament ids, iterate through array and return game data for each tournament Id
    const matchData = tournamentLookup(tournamentIds);
    //send raw data (array of objects) from the esports-data json and prepares it for the csv writer function
    const cookedData = rawDataToCookedData(matchData);
    //let the csv writer cook
    csvWriter
        .writeRecords(cookedData)
        .then(() => {
        console.log('CSV file has been written successfully');
        })
    .catch((error) => {
    console.error('Error writing CSV file:', error);
    });
}

// godFunction('108001239847565215');
godFunction('98767991299243165'); //this calls the function, the id is for LCS

//not used yet, but this function will return all the different leagues and their Ids to choose from when you run it, so you don't have to look up the id every time.
function getAllLeagues(){
    let leagueArray = [];
    const allLeagues = fs.readFile('esports-data/leagues.json', function(error, data){
        if (error) throw error;
        const leagues = JSON.parse(data);
        console.log(`There are currently ${leagues.length} leagues to choose from.`)
        leagues.forEach((obj) => leagueArray.push({name:obj.name, leagueId:obj.id}));
        console.log(leagueArray);
        return leagueArray;
    });
}

// getAllLeagues();
