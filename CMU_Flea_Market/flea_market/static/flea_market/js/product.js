
function geocodePlaceId(geocoder, map, infowindow,placeID) {
    var placeId = placeID;
  
    geocoder.geocode({'placeId': placeId}, function(results, status) {
      if (status === 'OK') {
        if (results[0]) {
          map.setZoom(13);
          map.setCenter(results[0].geometry.location);
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
  
function initMap() {
    map = new google.maps.Map(document.getElementById('product_map'), {
        center: {lat:40.442976, lng: -79.943009},
        zoom: 13
      });
      geocoder = new google.maps.Geocoder;
      if (navigator.geolocation) {
        var options = {timeout:8000};
        navigator.geolocation.getCurrentPosition(showPosition, errorHandler, options);

    }
}

function showPosition(position) {
    lat = position.coords.latitude;
    long = position.coords.longitude;
    myValue = position.coords.latitude + ',' + position.coords.longitude;
    latlngStr = myValue.split(',', 2);

    latlng = {lat: parseFloat(latlngStr[0]), lng: parseFloat(latlngStr[1])};
    geocoder.geocode({'location': latlng}, function (results, status) {
        if (status === 'OK') {
            if (results[0]) {
                var infowindowMe = new google.maps.InfoWindow({
                    content: 'You are here.'
                  });
                var marker1 = new google.maps.Marker({
                    position: latlng,
                    map: map,
                    icon:"https://img.icons8.com/color/48/000000/map-pin.png",
                  });
                infowindowMe.open(map, marker1);
                map.setCenter(latlng);
                startPlaceId = results[0].place_id;
                var itemGeo = document.getElementById('prod_location').value;

                geocodePlaceId(geocoder, map, infoWindow, itemGeo);
  
                new AutocompleteDirectionsHandler(map,itemGeo,startPlaceId);
            } else {
                window.alert('No results found');
            }
        } else {
            window.alert('Geocoder failed due to: ' + status);
        }
    });
}


function errorHandler(err) {
    if(err.code === 1) {
        alert("Error: Access is denied!");
    } else if( err.code === 2) {
        alert("Error: Position is unavailable!");
    }
}


async function loadProdLocation(){
    geocoder = new google.maps.Geocoder;
    infoWindow = new google.maps.InfoWindow;
    initMap();
  }
  
  /**
   * @constructor
   */
  function AutocompleteDirectionsHandler(map,destinationID,startPlaceID ) {
    this.map = map;
    this.originPlaceId = startPlaceID;
    this.destinationPlaceId = destinationID;
    this.travelMode = 'WALKING';
    this.directionsService = new google.maps.DirectionsService;
    this.directionsRenderer = new google.maps.DirectionsRenderer;
    this.directionsRenderer.setMap(map);
  
    var originInput = this.originPlaceId
    var destinationInput = this.destinationPlaceId
    var modeSelector = document.getElementById('mode-selector');
  
    this.setupClickListener('changemode-walking', 'WALKING');
    this.setupClickListener('changemode-transit', 'TRANSIT');
    this.setupClickListener('changemode-driving', 'DRIVING');
  
    this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(originInput);
    this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(
        destinationInput);
    this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(modeSelector);
    this.route();
  }
  
  AutocompleteDirectionsHandler.prototype.setupClickListener = function(
    id, mode) {
  var radioButton = document.getElementById(id);
  var me = this;
  
  radioButton.addEventListener('click', function() {
    me.travelMode = mode;
    me.route();
  });
  };
  
  
  AutocompleteDirectionsHandler.prototype.route = function() {
    if (!this.originPlaceId || !this.destinationPlaceId) {
      return;
    }
    var me = this;
  
    this.directionsService.route(
        {
          origin: {'placeId': this.originPlaceId},
          destination: {'placeId': this.destinationPlaceId},
          travelMode: this.travelMode
        },
        function(response, status) {
          if (status === 'OK') {
            me.directionsRenderer.setDirections(response);
          } else {
            window.alert('Directions request failed due to ' + status);
          }
        });
  };

