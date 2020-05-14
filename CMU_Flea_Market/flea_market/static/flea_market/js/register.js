x = document.getElementById("id_geo_location");
let geocoder;

function getLocation() {
    if (navigator.geolocation) {
        $('#locating').text('locating...');
        var options = {timeout:8000};
        navigator.geolocation.getCurrentPosition(showPosition, errorHandler, options);
    }
}

function errorHandler(err) {
    if(err.code === 1) {
        alert("Error: Access is denied!");
    } else if( err.code === 2) {
        alert("Error: Position is unavailable!");
    }
}

function showPosition(position) {
    let lat = position.coords.latitude;
    let long = position.coords.longitude;
    let myValue = position.coords.latitude + ',' + position.coords.longitude;
    $('#hidden_geo_lat_long').val(myValue);
    $('#hidden_geo_location').val(myValue).trigger('change');
}


function initMap() {
    geocoder = new google.maps.Geocoder;
}


function geocodeLatLng() {
    var input = document.getElementById("hidden_geo_location").value;
    var latlngStr = input.split(',', 2);
    console.log("latlngStr")
    console.log(latlngStr)
    var latlng = {lat: parseFloat(latlngStr[0]), lng: parseFloat(latlngStr[1])};
    geocoder.geocode({'location': latlng}, function (results, status) {
        if (status === 'OK') {
            if (results[0]) {
                var formatted_address = results[0].formatted_address;
                var placeID = results[0].place_id;
                
                document.getElementById("hidden_geo_location").value = placeID;
                $('#id_geo_location').trigger("focus").val(geo_to_city(results[0]));
                $('#locating').text('');
            } else {
                window.alert('No results found');
            }
        } else {
            window.alert('Geocoder failed due to: ' + status);
        }
    });
}

function geo_to_city(address) {
    let a = address['address_components'];
    return a[3]['short_name'] + ', ' + a[5]['short_name']
}


$(document).ready(function() {
    $(".category_picture_container").click(function () {
      if ($(this).css("box-shadow") === "none") {
          $(this).css({"box-shadow": "1px 8px 16px 1px #4ECDC4", "color": "#4ECDC4"});
      } else {
          $(this).css({"box-shadow": "none", "color": "black"});
      }
    });

    $("#id_preferences").focus(function () {
        $('#light').css("display", "block");
    });

    $("#ok-button").click(function () {
        let preferences = [];
        $(".category").each(function (index, element) {
            if ($(element).children(".category_picture_container").css("box-shadow") !== "none") {
                let pref = $(element).children(".category_name_container").children(".category_name").text();
                preferences.push(pref);
            }
        });

        $('#id_preferences').val(preferences.join(", ")).focus();
        $('#light').css("display", "none");
    });

    $("#cancel-button").click(function () {
        $('#light').css("display", "none");
        $('#id_preferences').val("");
    });
});