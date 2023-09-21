//ok function may not be needed anymore, just gonna use the csvwriter package


//data is an array of games taken from tournamentLookup
const csvmaker = function (data) {
    const header = Object.keys(data[0])
    const headerString = header.toString();
    const rowItems = data.map((object) =>{
        return Object.values(object).toString();
    });
    const merged = [headerString, ...rowItems];
    const csv = merged.join('\n');
    console.log(csv);

}

csvmaker([
    {
        dog: "red",
        cat: "sparkly",
        fish: "amnesia"
    },

    {
        dog:"green",
        cat:"Tom",
        fish:["test", "test1"]
    }
]);

module.exports = { csvmaker }