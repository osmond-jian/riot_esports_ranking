
// Add an event listener to the form
const form = document.getElementById('regions');
form.addEventListener('submit', function(event) {
// Prevent the form from submitting
event.preventDefault();

// Get the selected option value
const selectedOption = document.getElementById('regionSelector').value;
// Determine the URL based on the selected option (replace with your logic)
let actionURL = '';
    switch (selectedOption) {
        case 'option1':
            actionURL = 'submit1.php';
            break;
        case 'option2':
            actionURL = 'submit2.php';
            break;
        case 'option3':
            actionURL = 'submit3.php';
            break;
        default:
         // Handle other cases or set a default URL
            actionURL = 'default.php';
    }

            // Set the form action attribute to the determined URL
    form.action = actionURL;

            // Now, the form will submit to the dynamically determined URL
            // You can add any additional logic here before submitting if needed

            // Submit the form
    form.submit();
      });

function populateDropdown(){
    const dropdown = document.getElementById('dropdown');

    dropdown.innerHTML = '';

    // Add a default "Select an option" option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.text = 'Select an option';
    dropdown.appendChild(defaultOption);
    
    const leagues = getAllLeagues();
    leagues.forEach((object) => {
        const option = document.createElement('option');
        option.text = object.name;
        option.value = object.leagueId;
        dropdown.appendChild(option);
        })
}

const dropdownArrow = document.getElementById('regionSelector').nextElementSibling;
dropdownArrow.addEventListener('click', populateDropdown);