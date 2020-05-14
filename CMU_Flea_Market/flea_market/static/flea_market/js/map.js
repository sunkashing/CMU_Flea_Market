function locateMe(map, infoWindow, callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            me_latlng = [pos.lat, pos.lng];

            infoWindow.setPosition(pos);
            infoWindow.setContent('You at here.');
            infoWindow.open(map);
            map.setCenter(pos);

        }, function() {
            handleLocationError(true, infoWindow, map.getCenter());
        });
    } else {
        // Browser doesn't support Geolocation
        handleLocationError(false, infoWindow, map.getCenter());
        return null;
    }

}


function userSetLocation() {
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 40.442976, lng: -79.943009 },
        zoom: 13
    });

    var input = document.getElementById('pac-input');
    var infoWindow = new google.maps.InfoWindow;
    var autocomplete = new google.maps.places.Autocomplete(input);
    var geocoder = new google.maps.Geocoder;
    var user_preferred_location = document.getElementById('user_prefer_geo').value;
    autocomplete.bindTo('bounds', map);

    locateMe(map, infoWindow);
    geocodePlaceId(geocoder, map, infowindow, user_preferred_location)

    // Specify just the place data fields that you need.
    autocomplete.setFields(['place_id', 'geometry', 'name']);

    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    var infowindow = new google.maps.InfoWindow();
    var infowindowContent = document.getElementById('infowindow-content');
    infowindow.setContent(infowindowContent);

    var marker = new google.maps.Marker({
        map: map,
        icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
    });

    marker.addListener('click', function() {
        infowindow.open(map, marker);
    });

    autocomplete.addListener('place_changed', function() {
        infowindow.close();

        place = autocomplete.getPlace();
        if (!place.geometry) {
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);
        }

        // Set the position of the marker using the place ID and location.
        marker.setPlace({
            placeId: place.place_id,
            location: place.geometry.location
        });

        marker.setVisible(true);

        infowindowContent.children['place-name'].textContent = place.name;

        // infowindowContent.children['place-id'].textContent = place.place_id;
        infowindowContent.children['place-address'].textContent =
            place.formatted_address;
        infowindow.open(map, marker);

        document.getElementById("change_location").innerHTML = place.name;
        document.getElementById("update_location").value = place.place_id;
    });
}


function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
}

function geocodePlaceId(geocoder, map, infowindow, placeID) {
    var placeId = placeID;

    geocoder.geocode({ 'placeId': placeId }, function(results, status) {
        if (status === 'OK') {
            if (results[0]) {
                map.setZoom(13);
                map.setCenter(results[0].geometry.location);
                var marker = new google.maps.Marker({
                    map: map,
                    position: results[0].geometry.location
                });
                document.getElementById("load_location").innerHTML = results[0].formatted_address;

                // return marker
            } else {
                window.alert('No results found');
                // return;
            }
        } else {
            window.alert('Geocoder failed due to: ' + status);
            // return;
        }
    });
    // return;
}
