const fs = require('fs');


//takes in an array with tournament IDs, and returns the game metadata for the tournaments.
function tournamentLookup(tournamentArray) {
  // console.log(tournamentArray[0].id);
  let output = [];
  const data = fs.readFileSync('esports-data/tournaments.json', {encoding:'utf8', flag: 'r'})
  for (let i=0; i<tournamentArray.length; i++){
    let tournamentData = JSON.parse(data).filter((obj) => obj.id === tournamentArray[i].id);
    if (tournamentData.length === 0) {
      console.log(`No mapping data found for tournament id:${tournamentArray[i].id}`);
    } else {
      // console.log(tournamentData[0].stages);
      output.push(
        {
          leagueName: tournamentData[0].slug, //e.g. LCS
          date:tournamentData[0].startDate,
        }
        );
      tournamentData[0].stages.forEach((obj) => {
        output.push({stageName:obj.slug}); //e.g groups
        obj.sections.forEach((obj) => {
          output.push({sectionName:obj.name}); //e.g. group A
          obj.matches.forEach((obj) => {
            // output.push(
            //   {
            //     matchId:obj.id,
            //     strategy:obj.strategy,
            //   });
            obj.games.forEach((obj) => output.push(obj))
          })})});
    }
  }
  // console.log(output.length, output);
  return output;
}


// tournamentLookup([{id:"110733838935136200"}]);//easy
// tournamentLookup([{id:"109428868589633757"}]); //hARD
// tournamentLookup([
//   { id: '110303581083678395' },
//   { id: '109517090066605615' },
//   { id: '108206581962155974' },
//   { id: '107458367237283414' },
//   { id: '107458335260330212' },
//   { id: '105658534671026792' },
//   { id: '105788932118361426' },
//   { id: '109428868589633757' },
//   { id: '105522217230238828' },
//   { id: '104174992692075107' },
//   { id: '103462439438682788' },
//   { id: '108300620375000370' },
//   { id: '108294935083112239' },
//   { id: '108288780705657082' },
//   { id: '108283378783680768' },
//   { id: '108007809203463350' },
//   { id: '107784927885285215' },
//   { id: '107744640257699883' },
//   { id: '106972812538132507' },
//   { id: '107741488941545959' },
//   { id: '107045060626269295' },
//   { id: '107719921883398026' },
//   { id: '107697401518332544' },
//   { id: '107656643139734824' },
//   { id: '107620592294752774' }
// ]);

module.exports = { tournamentLookup };