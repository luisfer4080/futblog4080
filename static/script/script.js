var arr = new Array();
let team_disp = $("#team_disp");
var hide = false
 
// create and update players divs
$("#team_disp").hide();
$("#team_label").hide();

// player view menu divs
$("#show-player-pro").show();
$("#show-author-pro").hide();
$("#show-palmares-pro").hide();
$("#show-history-pro").hide();

// admin view filters divs
$("users").show();
$("posts").show();
$("teams").show();
$("players").show();

// button actions player view menu divs
$("#player-pro").click(function(){
    $("#show-player-pro").show();
    $("#show-author-pro").hide();
    $("#show-palmares-pro").hide();
    $("#show-history-pro").hide();
})

$("#author-pro").click(function(){
    $("#show-player-pro").hide();
    $("#show-author-pro").show();
    $("#show-palmares-pro").hide();
    $("#show-history-pro").hide();
})

$("#palmares-pro").click(function(){
    $("#show-player-pro").hide();
    $("#show-author-pro").hide();
    $("#show-palmares-pro").show();
    $("#show-history-pro").hide();
})


$("#history-pro").click(function(){
    $("#show-player-pro").hide();
    $("#show-author-pro").hide();
    $("#show-palmares-pro").hide();
    $("#show-history-pro").show();
})

// filter when you click in the admin buttons
$("#all").click(function(){
    $("#users").show();
    $("#posts").show();
    $("#teams").show();
    $("#players").show();
})

$("#users_button").click(function(){
    $("#users").show();
    $("#posts").hide();
    $("#teams").hide();
    $("#players").hide();
})

$("#posts_button").click(function(){
    $("#users").hide();
    $("#posts").show();
    $("#teams").hide();
    $("#players").hide();
})

$("#teams_button").click(function(){
    $("#users").hide();
    $("#posts").hide();
    $("#teams").show();
    $("#players").hide();
})

$("#players_button").click(function(){
    $("#users").hide();
    $("#posts").hide();
    $("#teams").hide();
    $("#players").show();
})


// show and hide team_disp if need it and restreing choices to a maxium of 2
$("#team").change(function() {
    $(this).find("option:selected")
    if ($(this).find("option:selected").length > 2) {
        $(this).find("option").removeAttr("selected");
        $(this).val(arr);
    }else {
        arr = new Array();
        $(this).find("option:selected").each(function(index, item) {
            arr.push($(item).val());

            for (let i=0;i<arr.length;i++){
                if (arr[i] === "0"){
                    $("#team_disp").show();
                    $("#team_label").show();
                    hide = true;
                }else{
                    if(i === 0 && hide === true){
                        $("#team_disp").hide();
                        $("#team_label").hide();
                        hide = false;
                    }    
                }
            }
    
        });
    }
})
