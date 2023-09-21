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
// const { teamLookup } = require('./teamLookup.js');

function rawDataToCookedData(arrayOfObjects){
    // console.log(arrayOfObjects);
    const finalArray = [];
    for (i=0; i<arrayOfObjects.length; i++) {
        if (arrayOfObjects[i].leagueName) {
            finalArray.push(
                {
                    leagueName:arrayOfObjects[i].leagueName,
                    date: arrayOfObjects[i].date,
                });
        } else if (arrayOfObjects[i].stageName) {
            finalArray.push(
                {
                    stageName:arrayOfObjects[i].stageName,
                });
        } else if (arrayOfObjects[i].sectionName){
            finalArray.push(
                {
                    sectionName:arrayOfObjects[i].sectionName,
                });
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

// module.exports = { rawDataToCookedData, };


// teamLookup('106857739520697600');
// // teamLookup('99566406065437842');

module.exports = { rawDataToCookedData, teamLookup, };