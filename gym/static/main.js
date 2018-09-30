$( document ).ready(function() {
    console.log('read')
  // Original JavaScript code by Chirp Internet: www.chirp.com.au
  // Please acknowledge use of this code by including this header.
window.addEventListener("DOMContentLoaded", function(e) {

    var stage = document.getElementById("stage");
    var fadeComplete = function(e) { stage.appendChild(arr[0]); };
    var arr = stage.getElementsByTagName("a");
    for(var i=0; i < arr.length; i++) {
      arr[i].addEventListener("animationend", fadeComplete, false);
    }

}, false);

var markers = Object.create(null);;
    function initMap() {
        
        const Http = new XMLHttpRequest();
        const url=SCRIPT_ROOT + '/coordinates';
        Http.open("GET", url);
        Http.send();
        Http.onreadystatechange=(e)=>{
            var data = JSON.parse(Http.responseText).data;
            //get search coordinates 
            var center = {'lat': data.center[0], 'lng': data.center[1]};
            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: 12,
                center: center
            });
            google.maps.event.trigger(map, 'resize');

            var yourLocation = new google.maps.Marker({
                position: center,
                map: map,
                title: 'Your Location',
                icon: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            });

            //this loop adds markers 
            for(i=0; i < data.gyms.length; i++){
                var gym_info = data.gyms[i];
                var LatLng = {'lat': gym_info['coordinates'][0], 'lng': gym_info['coordinates'][1]};

                var contentString = '<div class="infowindow"><h6 style="margin-bottom:.2rem;">'+ gym_info['name'] + '</h6> <p style="margin-bottom:1%"> This is a great gym!</p>'+'<p style="margin-bottom:1%">'+ gym_info['address'] + '</p> <a href='+ gym_info['link'] +' target="_blank"> View on Google Maps </a></div>';
                var infowindow = new google.maps.InfoWindow({
                  content: contentString
                });
                var marker = new google.maps.Marker({
                    position: LatLng,
                    map: map,
                    title: gym_info['name'] + ' location'
                });
                marker.infowindow = infowindow;
                marker.addListener('click', function() {
                    return this.infowindow.open(map, this);
                });

                if (markers[gym_info['name']] == null){
                    markers[gym_info['name']] = [marker];
                }
                else {
                    markers[gym_info['name']].push(marker);
                }
            }
                

        }

    }
    //hide location addresses 

    function toggleHidden(id) {

       var divelement = document.getElementById(id);

       if(divelement.style.display == 'none')
          divelement.style.display = 'block';
       else
          divelement.style.display = 'none';
    }

    function toggleFocus(gym_name){
        hidden_section = document.getElementById('sectiontohide '+gym_name)
        //if the toggle reealed the locations 
        if (hidden_section.style.display == 'block'){
            for (gym in markers){ 
                //if this is the selected gym 
                if (gym_name == gym) {
                    gym_markers = markers[gym]
                    for (i=0; i < gym_markers.length;i++) {
                        marker = gym_markers[i];
                        marker.setOpacity(1);
                    } 
                }
                //fade out all other gyms 
                else {
                    gym_markers = markers[gym]
                    for (i=0; i < gym_markers.length;i++) {
                        marker = gym_markers[i];
                        marker.setOpacity(0.6);
                        
                    } 
                }
                
            }
        }
        else{
            for (gym in markers){ 
                //set to normal every other marker
                if (gym_name != gym) {
                    gym_markers = markers[gym]
                    for (i=0; i < gym_markers.length;i++) {
                        marker = gym_markers[i];
                        marker.setOpacity(1);
                    } 
                }
                
            }           
        }
    }
});
