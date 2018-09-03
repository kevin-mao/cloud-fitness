SCRIPT_ROOT = {{ request.script_root|tojson|safe }}; 

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
            zoom: 11,
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
        
        }
            

    }

}
