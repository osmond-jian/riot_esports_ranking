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
// ]
const fs = require('fs');

//this function takes in the raw data (as you can see in test array above) and prepares it for csv maker
function rawDataToCookedData(arrayOfObjects){
    // console.log(arrayOfObjects);
    const finalArray = [];
    for (i=0; i<arrayOfObjects.length; i++) {
        //The first entry from tournamentLookup should include an object with just League name and date. This checks if the object is the entry that just contains the league metadata
        if (arrayOfObjects[i].leagueName) {
            finalArray.push(
                {
                    leagueName:arrayOfObjects[i].leagueName,
                    date: arrayOfObjects[i].date,
                });
        //every time the "stage" section is segmented, a different object is pushed in and will be captured here. This is the single column with the name of the Stage (e.g. groups, playoffs)
        } else if (arrayOfObjects[i].stageName) {
            finalArray.push(
                {
                    stageName:arrayOfObjects[i].stageName,
                });
        //same thing but for section (e.g. group A, semifinals)
        } else if (arrayOfObjects[i].sectionName){
            finalArray.push(
                {
                    sectionName:arrayOfObjects[i].sectionName,
                });
        //configuring the regular array into the final object
        } else if (arrayOfObjects[i].state === "completed"){
            let newObject = {
                esportsGameId: arrayOfObjects[i].id,
                gameOrder: arrayOfObjects[i].number,
                blueSideTeam: teamLookup(arrayOfObjects[i].teams[0].id),
                blueSideWin: arrayOfObjects[i].teams[0].result.outcome,
                redSideTeam: teamLookup(arrayOfObjects[i].teams[1].id),
                redSideWin: arrayOfObjects[i].teams[1].result.outcome,
            };
            finalArray.push(newObject);
        } else {
            //no game found with tournament data - maybe riot deemed it non-competitive (e.g. TFT game, rift rivals) or maybe there was no game (e.g. the 3rd game in a Bo3 that ended in 2-0 but still had a data entry)
            console.log('null game');
        }
    }
    // console.log(finalArray);
    return finalArray;
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


// rawDataToCookedData(testArray);

// teamLookup('106857739520697600');
// teamLookup('99566406065437842');

module.exports = { rawDataToCookedData, teamLookup, };