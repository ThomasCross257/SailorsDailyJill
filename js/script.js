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
function DB_EntrySwap(ID){
    var entry_id = ID;
    console.log(entry_id);
    if (entry_id == "Submit" || entry_id == "Return"){
        document.getElementById("new_Entry").style.display = "none"; 
        document.getElementById("db_Broad").style.display = "block";
        
    }
    else if (entry_id = "Enter"){
        document.getElementById("db_Broad").style.display = "none";
        document.getElementById("new_Entry").style.display = "block"; 
    }
}