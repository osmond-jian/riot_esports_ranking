const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const { getTournamentsFromLeagueId } = require('./commands/leagueToTournaments');
const { tournamentLookup } = require('./commands/tournamentLookup');
const { rawDataToCookedData } = require('./commands/matchToDataArray');
// const { csvmaker } = require('commands/jsonToCSV.js'); //no longer needed with csvwriter package
// const { csvwriter } = require('./commands/write_csv_file');
const { teamLookup } = require('./commands/teamLookup');



// Define the CSV writer
const csvWriter = createCsvWriter({
    path: 'output.csv', // Specify the output file name
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
    const tournamentIds = getTournamentsFromLeagueId(leagueId);
    // console.log(tournamentIds);
    const matchData = tournamentLookup(tournamentIds);
    // console.log(matchData);
    // const csvString = await csvmaker(matchData);
    // await csvwriter.writeRecords(matchData);

    const cookedData = rawDataToCookedData(matchData);
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
godFunction('98767991299243165');

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
