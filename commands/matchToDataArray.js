const fs = require('fs');
//this function takes in the raw data (as you can see in test array above) and prepares it for csv maker
function rawDataToCookedData(arrayOfArrays){

    const arrayOfObjects = arrayOfArrays[0];
    const arrayOfErrors = arrayOfArrays[1];
    // console.log(arrayOfObjects);
    const finalArray = [];
    let currentLeagueName;
    let currentStageName;
    let currentSectionName;
    let leagueStartDate;

    let unneededCounter = 0;
    let unstartedCounter = 0;
    let inProgressCounter = 0;

    for (i=0; i<arrayOfObjects.length-1; i++) {
        // console.log(arrayOfObjects);
        // let ranking = [];
        //The first entry from tournamentLookup should include an object with just League name and date. This checks if the object is the entry that just contains the league metadata
        if (arrayOfObjects[i] === undefined){
            console.log('undefined');
        } else if (arrayOfObjects[i] && arrayOfObjects[i].leagueName) {
            currentLeagueName = arrayOfObjects[i].leagueName;
            // leagueStartDate = arrayOfObjects[i].date;
            // finalArray.push(
            //     {
            //         leagueName:arrayOfObjects[i].leagueName,
            //         date: arrayOfObjects[i].date,
            //     });
        //every time the "stage" section is segmented, a different object is pushed in and will be captured here. This is the single column with the name of the Stage (e.g. groups, playoffs)
        } else if (arrayOfObjects[i].stageName) {
            currentStageName = arrayOfObjects[i].stageName;

        //new Ranking feature
        // } else if (Array.isArray(arrayOfObjects[i]) && arrayOfObjects[i][0]?.ordinal === 1) {
        //     // console.log (arrayOfObjects[i][0]);
        //     for (j=0; j < arrayOfObjects[i].length-1; j++){
        //         ranking.push(arrayOfObjects[i][j].teams[0].id);
        //     }
        
        //same thing but for section (e.g. group A, semifinals)
        } else if (arrayOfObjects[i].sectionName){
            currentSectionName = arrayOfObjects[i].sectionName;

        } else if (arrayOfObjects[i].state === "completed"){
            //gets the date information from the game file
            const platformId = getPlatformGameId(arrayOfObjects[i].id);
            leagueStartDate = getDateFromGameData(platformId);

            let newObject = {
                leagueName: currentLeagueName,
                date: leagueStartDate,
                stageName: currentStageName,
                sectionName: currentSectionName,
                esportsGameId: arrayOfObjects[i].id,
                platformGameId: platformId,
                gameOrder: arrayOfObjects[i].number,
                blueSideTeam: teamLookup(arrayOfObjects[i].teams[0].id),
                blueSideWin: arrayOfObjects[i].teams[0].result.outcome,
                // blueSideTeamRanking: rankingDataSort(ranking, arrayOfObjects[i].teams[0].id),
                redSideTeam: teamLookup(arrayOfObjects[i].teams[1].id),
                redSideWin: arrayOfObjects[i].teams[1].result.outcome,
                // redSIdeTeamRanking: rankingDataSort(ranking, arrayOfObjects[i].teams[1].id),
            };
            finalArray.push(newObject);

        } else if (arrayOfObjects[i].state === "unneeded" || arrayOfObjects[i].state === "inProgress" || arrayOfObjects[i].state === "unstarted") {
            //need to figure out what inProgress means exactly
            if (arrayOfObjects[i].state === "unneeded") unneededCounter++
            if (arrayOfObjects[i].state === "inProgress" ) inProgressCounter++
            if (arrayOfObjects[i].state === "unstarted" ) unstartedCounter++
            updateConsoleMessage('The game state is ' + arrayOfObjects[i].state +`! Total so far:${unneededCounter} uneeded; ${inProgressCounter} in Progress, ${unstartedCounter} unstarted`);

            arrayOfErrors.push({
                gameId: arrayOfObjects[i].id,
                state: arrayOfObjects[i].state,
            });
        } else {
            //is it because it isnt competitive? or some other error?
            console.log('Null game that needs investigation');
            console.error(`Invalid data at index ${i}`, arrayOfObjects[i]);
            arrayOfErrors.push(arrayOfObjects[i]);
        }
    }
    // console.log(finalArray);
    arrayOfErrors.push({
        unneeded: unneededCounter,
        inProgress: inProgressCounter,
        unstarted: unstartedCounter,
    })
    updateConsoleMessage(`Cleaned ${i+1} rows for the dataframe`);
    console.log();
    return [finalArray, arrayOfErrors];
}

function teamLookup(teamId){
    // console.log(teamId);
    const teamNameDatabase = fs.readFileSync('esports-data/teams.json', {encoding:'utf8', flag: 'r'})
    const teamName = JSON.parse(teamNameDatabase).filter((obj) => obj.team_id === teamId);
    if (teamName.length ===0){
        console.log(`No Mapping data found for team Id:${teamId}`);
    } else {
        return teamName[0].name;
    }
}

//get gameId, return platformGameId (the file name)
function getPlatformGameId(gameId){
    const data = fs.readFileSync('esports-data/mapping_data.json', {encoding:'utf8', flag: 'r'});
    const mappingObject = JSON.parse(data).filter((obj) => obj.esportsGameId === gameId);
    if (!mappingObject) {
        console.log("No mappingObject for "+gameId);
        return(null);
    } else if (mappingObject.length === 0) {
        console.log("No platformGameId found for "+gameId); //maybe add a way to track all the missing data
        return(null);
    } else {
    //  console.log(mappingObject[0].platformGameId);
        // console.log(gameId, mappingObject);
        return(mappingObject[0].platformGameId);
    }
}

//using platformGameId, get date played from the game data
function getDateFromGameData(platformGameId) {
    if (platformGameId === null) return('No platformGameId');
    try {
      const fileName = platformGameId.replace(/:/g, '_');
      const filePath = `games/${fileName}.json`;
  
      if (fs.existsSync(filePath)) {
        const data = fs.readFileSync(filePath, 'utf8');
        const parseData = JSON.parse(data);
        if (parseData && parseData[0] && parseData[0].eventTime) {
        //   console.log(parseData[0].eventTime);
          return parseData[0].eventTime;
        } else {
          console.error('Invalid data format in the JSON file:', filePath);
          return('Invalid data format in JSON file'); // Or handle the error as needed
        }
      } else {
        console.error('File does not exist:', filePath);
        return('File does not exist'); // Or handle the error as needed
      }
    } catch (err) {
      console.error('Error reading or parsing file:', err);
      return ('Error reading or parsing file'); // Or handle the error as needed
    }
  }

function updateConsoleMessage(message) {
    process.stdout.clearLine();  // Clear the current line
    process.stdout.cursorTo(0); // Move the cursor to the beginning of the line
    process.stdout.write(message); // Write the updated message
 }

//temp disabled
// function rankingDataSort (rankingArray, teamId){
//     const rank = rankingArray.indexOf(teamId);
//     if (!rank) {
//         console.log(rank);
//     }
//     return (Number(rank)+1);
// }

// rawDataToCookedData(testArray);

// teamLookup('106857739520697600');
// teamLookup('99566406065437842');

module.exports = { rawDataToCookedData, teamLookup, getDateFromGameData, getPlatformGameId, updateConsoleMessage };


/////testing purposes below

// const testArray = [
//     {
//         id:'110767955468411237',
//         state:'completed',
//         number:3,
//         teams: [
//             {
//                 id: "106857739520697600",
//                 side: "blue",
//                 record: {
//                     wins: 2,
//                     losses: 0,
//                     ties: 0
//                   },
//                   result: {
//                     outcome: "win",
//                     gameWins: 2
//                   },
//             },
//             {
//                 id: "106857739520697600",
//                 side: "red",
//                 record: {
//                     wins: 2,
//                     losses: 0,
//                     ties: 0
//                   },
//                   result: {
//                     outcome: "loss",
//                     gameWins: 2
//                   },
//             }
//         ]
//     },

//     {
//         id:'110767955468411237',
//         state:'completed',
//         number:3,
//         teams: [
//             {
//                 id: "106857739520697600",
//                 side: "red",
//                 record: {
//                     wins: 2,
//                     losses: 0,
//                     ties: 0
//                   },
//                   result: {
//                     outcome: "loss",
//                     gameWins: 2
//                   },
//             },
//             {
//                 id: "106857739520697600",
//                 side: "red",
//                 record: {
//                     wins: 2,
//                     losses: 0,
//                     ties: 0
//                   },
//                   result: {
//                     outcome: "loss",
//                     gameWins: 2
//                   },
//             }
//         ]
//     },

//     [
//         {
//           ordinal: 1,
//           teams: [
//             {
//               id: "107603600826620492",
//               side: null,
//               record: {
//                 wins: 6,
//                 losses: 0,
//                 ties: 1
//               },
//               result: null,
//               players: [
//                 {
//                   id: "102179949566469236",
//                   role: "support"
//                 },
//                 {
//                   id: "107599451577178034",
//                   role: "top"
//                 },
//                 {
//                   id: "107599454467577313",
//                   role: "jungle"
//                 },
//                 {
//                   id: "108319314210826103",
//                   role: "mid"
//                 },
//                 {
//                   id: "99566405931955015",
//                   role: "bottom"
//                 },
//                 {
//                   id: "108319313376381387",
//                   role: "mid"
//                 },
//                 {
//                   id: "107599451053841884",
//                   role: "top"
//                 },
//                 {
//                   id: "107581943022339854",
//                   role: "support"
//                 }
//               ]
//             }
//           ]
//         },
//         {
//           ordinal: 2,
//           teams: [
//             {
//               id: "107581765633427097",
//               side: null,
//               record: {
//                 wins: 5,
//                 losses: 0,
//                 ties: 2
//               },
//               result: null,
//               players: [
//                 {
//                   id: "107581371163788732",
//                   role: "jungle"
//                 },
//                 {
//                   id: "107599454407284678",
//                   role: "top"
//                 },
//                 {
//                   id: "99566408548798069",
//                   role: "mid"
//                 },
//                 {
//                   id: "108588683461473411",
//                   role: "bottom"
//                 },
//                 {
//                   id: "107599454605465061",
//                   role: "support"
//                 },
//                 {
//                   id: "110383724057493681",
//                   role: "mid"
//                 }
//               ]
//             }
//           ]
//         },
//         {
//           ordinal: 3,
//           teams: [
//             {
//               id: "108121051709036068",
//               side: null,
//               record: {
//                 wins: 3,
//                 losses: 3,
//                 ties: 1
//               },
//               result: null,
//               players: [
//                 {
//                   id: "108121093742662993",
//                   role: "support"
//                 },
//                 {
//                   id: "108033845851746480",
//                   role: "mid"
//                 },
//                 {
//                   id: "108121093999548053",
//                   role: "none"
//                 },
//                 {
//                   id: "108018681174343034",
//                   role: "jungle"
//                 },
//                 {
//                   id: "109675271282589715",
//                   role: "mid"
//                 },
//                 {
//                   id: "108121093943907978",
//                   role: "bottom"
//                 },
//                 {
//                   id: "109675277775000118",
//                   role: "top"
//                 },
//                 {
//                   id: "109892678657940020",
//                   role: "bottom"
//                 },
//                 {
//                   id: "107581398133425627",
//                   role: "support"
//                 },
//                 {
//                   id: "107599452576308720",
//                   role: "top"
//                 },
//                 {
//                   id: "107576831502041293",
//                   role: "jungle"
//                 },
//                 {
//                   id: "107599451749930934",
//                   role: "mid"
//                 }
//               ]
//             }
//           ]
//         },
//     ]
// ];

//     rawDataToCookedData(testArray);