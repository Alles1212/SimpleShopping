function postForm() {
    // Get the form object
    let form = document.getElementById('myForm');

    // Use form content to create a FormData object
    let mydata = new FormData(form);
    console.log(mydata);

    let url = "/insert";  // Assuming your Flask route is '/insert'

    // Check if any of the required fields is empty
    if (mydata.get('name').trim().length === 0 || mydata.get('price').trim().length === 0 || mydata.get('stock').trim().length === 0) {
        alert('請輸入正確值');
    } else {
        // Perform the fetch only if all required fields are filled
        fetch(url, {
            method: 'POST',
            body: mydata  // Put the FormData object in the fetch body
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            alert('新增成功');
            location.reload();
            return response.json();
        })
        .then(data => {
            console.log(data);
            // Handle the response data if needed
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle the error, e.g., display an error message to the user
        });
    }
}



function editForm() {
    // Get the form object
    let form = document.getElementById('myForm');

    // Use form content to create a FormData object
    let mydata = new FormData(form);
    console.log(mydata);

    let url = "/update";  // Assuming your Flask route is '/insert'

    // Check if any of the required fields is empty
    if (mydata.get('name').trim().length === 0 || mydata.get('price').trim().length === 0 || mydata.get('stock').trim().length === 0) {
        alert('請輸入正確值');
    } else {
        // Perform the fetch only if all required fields are filled
        fetch(url, {
            method: 'POST',
            body: mydata  // Put the FormData object in the fetch body
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            alert('修改成功');
            location.replace('/shop');
            return response.json();
        })
        .then(data => {
            console.log(data);
            // Handle the response data if needed
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle the error, e.g., display an error message to the user
        });
    }
}