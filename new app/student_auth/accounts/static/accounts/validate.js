function validateForm() {
    let mobile = document.getElementsByName("mobile")[0].value;
    let passout = document.getElementsByName("passout_year")[0].value;

    if (mobile.length !== 10 || isNaN(mobile)) {
        alert("Enter a valid 10-digit mobile number!");
        return false;
    }

    if (passout < 2000 || passout > 2028) {
        alert("Enter a valid passout year between 2000 and 2028!");
        return false;
    }
    return true;
}
