function loginSwap(){
    var signIn = document.getElementById("signin");
    var signUp = document.getElementById("signup");
    if (signIn.style.display == "block"){
        signIn.style.display = "none";
        signUp.style.display = "block";
    }
    else{
        signIn.style.display = "block";
        signUp.style.display = "none";
    }
}