$(function(){
    var data;
    $.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/coordinates",
        dataType: "json",
        timeout: 120000,
        error: errorHandlier,
        success: function(r){
            data = r.data;
            console.log(data)
        }
    });
    setTimeout(function(){
        if(data != null){
            /* whatever you want to do using the results */
            /* For example using above API, */ 
            alert("Hello "+data[0].firstname+" "+data[0].lastname);
        }
        else{
            setTimeout(arguments.callee, 100);
        }
    }
});

function initMap() {
  var myLatLng = {lat: 40.7, lng: -74};

  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 10,
    center: myLatLng
  });

  var marker = new google.maps.Marker({
    position: myLatLng,
    map: map,
    title: 'Hello World!'
  });
}