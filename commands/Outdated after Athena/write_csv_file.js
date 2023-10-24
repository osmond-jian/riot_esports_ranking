const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const data = [
  { name: 'John', age: 30, city: 'New York' },
  { name: 'Jane', age: 28, city: 'Los Angeles' },
  { name: 'Bob', age: 35, city: 'Chicago' },
];

// Define the CSV writer
const csvWriter = createCsvWriter({
  path: 'output.csv', // Specify the output file name
  header: [
    { id: 'name', title: 'Name' }, // Define column headers
    { id: 'age', title: 'Age' },
    { id: 'city', title: 'City' },
  ],
});

// Write the data to the CSV file
csvWriter
  .writeRecords(data)
  .then(() => {
    console.log('CSV file has been written successfully');
  })
  .catch((error) => {
    console.error('Error writing CSV file:', error);
  });

  module.exports = { csvWriter };