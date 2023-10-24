const fs = require('fs');

function teamLookup(teamId){
    console.log(teamId);
    const teamNameDatabase = fs.readFileSync('esports-data/teams.json', {encoding:'utf8', flag: 'r'})
    const teamName = JSON.parse(teamNameDatabase).filter((obj) => obj.team_id === teamId);
    if (teamName.length ===0){
        console.log(`No Mapping data found for team Id:${teamId}`);
    } else {
        return teamName[0].name;
    }
}

teamLookup('106857739520697600');
// teamLookup('99566406065437842');

module.exports = { teamLookup, };