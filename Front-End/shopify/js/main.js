function login() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var URL = this.responseText;
            var win = window.open(URL, "_self");
        } else if (this.readyState == 4 && this.status != 200) {
            alert(
                "The app is facing some technical difficulties and therefore cannot log you in right now. Please try again later.\nIf the issue persists, please contact me at anant.j2409@gmail.com"
            );
        }
    };
    xhttp.open("GET", "http://127.0.0.1:5000/login", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.withCredentials = true;
    // xhttp.timeout = 3000;
    // xhttp.ontimeout = errorAlert();
    xhttp.send();
}

function fetchUserData() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let jsonval = JSON.parse(this.responseText);
            loggedin(jsonval);
        }
        if (this.readyState == 4 && this.status != 200) {
            loggedout();
        }
    };
    xhttp.open("GET", "http://127.0.0.1:5000/userdata", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.withCredentials = true;
    // xhttp.timeout = 3000; // Set timeout to 4 seconds (4000 milliseconds)
    // xhttp.ontimeout = errorAlert();
    xhttp.send();
}

function logout() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            loggedout();
        }
    };
    xhttp.open("GET", "http://127.0.0.1:5000/logout", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.withCredentials = true;
    xhttp.send();
}

function displayResult(imgurl) {
    var firstRow = document.getElementById("myTable").rows[0];
    var x = firstRow.insertCell(-1);
    // x.innerHTML="New cell";
    var img = document.createElement("img");
    img.src = imgurl;
    x.appendChild(img);
    x.onclick = function () {
        document.getElementById("bigger_image").style.display = "block";
        document.getElementById("bigger_image_frame").src = imgurl;
        document.getElementById("myTable").style.display = "none";
    };
}

function close_iframe() {
    document.getElementById("bigger_image").style.display = "none";
    document.getElementById("myTable").style.display = "table";
}

function delete_image() {
    if (!confirm("Are you sure you want to delete this image?")) {
        alert("Your image was not deleted!");
        return;
    }
    url = document.getElementById("bigger_image_frame").src;
    var pathname = new URL(url).pathname;
    var paths = pathname.split("/");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            window.location.replace(this.responseText);
        }
        if (this.readyState == 4 && this.status != 200) {
            console.log("Could not delete image");
        }
    };
    xhttp.open("GET", "http://127.0.0.1:5000/delete?id=" + paths[2], true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.withCredentials = true;
    xhttp.send();
}
