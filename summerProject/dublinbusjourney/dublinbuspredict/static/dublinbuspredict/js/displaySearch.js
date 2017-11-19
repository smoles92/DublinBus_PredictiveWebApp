//// Toggle function for route div on map.html

$(document).ready(function(){
	$("#RouteMap0").click(function(){
		$("#toggleRouteMap0").toggle();
	});
});

$(document).ready(function(){
	$("#RouteMap1").click(function(){
		$("#toggleRouteMap1").toggle();
	});
});

////Toggle function for route div on map.html
$(document).ready(function(){
	$("#RouteMap2").click(function(){
		$("#toggleRouteMap2").toggle();
	});
});

//Toggles plus and minus icon for Show Details
$(document).ready(function(){
	$("#RouteMap0").click(function(){
		$("#RouteMap0").toggleClass('fa-plus-square fa-minus-square');
	});
});

//Toggles plus and minus icon for More Information
$(document).ready(function(){
	$("#RouteMap1").click(function(){
		$("#RouteMap1").toggleClass('fa-plus-square fa-minus-square');
	});
});

//Toggles plus and minus icon for More Information
$(document).ready(function(){
	$("#RouteMap2").click(function(){
		$("#RouteMap2").toggleClass('fa-plus-square fa-minus-square');
	});
});

var map; // define a map as a global variable for use of different functions
var directionsDisplay;
var path;
var service;
var source;
var destination;
var list_origin_dropdown = [];
var infoWindow;
var snappedCoordinates = [];

function initMap() {
//	Function to pull in the map
	map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }); //closing map creation	

//    Add traffic layer to the map.
	  var trafficLayer = new google.maps.TrafficLayer();
	  trafficLayer.setMap(map);

//	  Add Public transit layer to the map.
	  var transitLayer = new google.maps.TransitLayer();
	  transitLayer.setMap(map);

//	Function to pull in the json from the url.
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/sampleQuery", null, function(d) {
        var data = d.data;
        var points = new Array; 
        // Loop to display marker
        var marker, i, newMarker, intSrc, intDst, midPoint;
        var infowindow = new google.maps.InfoWindow();
        for (i = 0; i < data.length; i++) {
                intSrc = parseInt(source);
                intDst = parseInt(destination);
                if (data[i][0] == intSrc){
               	 newMarker = stopsIconSrc;
                } else if (data[i][0] == intDst){
               	 newMarker = stopsIconDst;
               	 midPoint = Math.round(Math.abs(i/2));
                } else {
               	 newMarker = stopsIcon;
                }     
                marker = new google.maps.Marker({
                position: new google.maps.LatLng(data[i][1], data[i][2]),
                map: map,
                icon: newMarker
            });
        // push points for directions service.
        points.push(marker.getPosition().toUrlValue());
        
        // function to add click event to marker to display infowindow. 
        google.maps.event.addListener(marker, 'click', (function(marker, i){
        	return function() {
        		if (data[i][0] == intSrc){
        			infowindow.setContent("<b>Selected Source<br>Stop ID:&nbsp</b>" + data[i][0] + "<br>" + 	
            				"<b>Location:&nbsp</b>" + data[i][3] + "<br>" + "<b>Street:&nbsp</b>" + data[i][4]);
        			infowindow.open(map,marker);
        		} else if(data[i][0] == intDst){
        			infowindow.setContent("<b>Selected Destination<br>Stop ID:&nbsp</b>" + data[i][0] + "<br>" + 	
        				"<b>Location:&nbsp</b>" + data[i][3] + "<br>" + "<b>Street:&nbsp</b>" + data[i][4]);
        		infowindow.open(map,marker);
        		}
        		else {
        			infowindow.setContent("<b>	Stop ID:&nbsp</b>" + data[i][0] + "<br>" + 	
            				"<b>Location:&nbsp</b>" + data[i][3] + "<br>" + "<b>Street:&nbsp</b>" + data[i][4]);
            		infowindow.open(map,marker);}
        	}
        })(marker, i));
        if (data[i][0] == intDst){
      	  i = data.length-1;
        }
        }     
        // center the map only on the midpoint of the journey
        map.setCenter({
     		lat : parseFloat(data[midPoint][1]),
     		lng : parseFloat(data[midPoint][2])
     	});
        
        infoWindow = new google.maps.InfoWindow;
    	// Find geolocation of user. 
        // Function adapted from: https://developers.google.com/maps/documentation/javascript/examples/map-geolocation
      
      if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(function(position) {
              pos = {
                  lat: position.coords.latitude,
                  lng: position.coords.longitude
              };
              // create marker for new location
              marker = new google.maps.Marker({
              	position: pos,
              	map: map,
              	icon: myLocationIcon2
          });  
              
          }, function() {
              handleLocationError(true, infoWindow, map.getCenter());
          });
      } else {
          // Browser doesn't support Geolocation
          handleLocationError(false, infoWindow, map.getCenter());
      }

      function handleLocationError(browserHasGeolocation, infoWindow, pos) {
   		  infoWindow.close();
          infoWindow.setPosition(pos);
          infoWindow.setContent(browserHasGeolocation ?
                                'Error: The Geolocation service failed.' :
                                'Error: Your browser doesn\'t support geolocation.');
          infoWindow.open(map);
      }

      //Initialize the Path Array
      path = new google.maps.MVCArray();
      
      //Initialize the Direction Service
      service = new google.maps.DirectionsService();

      //Set the Path Stroke Color
      $.get('https://roads.googleapis.com/v1/snapToRoads', {
    	    interpolate: true,
    	    key: "AIzaSyAMIv5pNbn7yJWpjSYOr2BMuFuhGFJLcPk",
    	    path: points.join('|')
    	  }, function(data) {
    	    processSnapToRoadResponse(data);
    	         // drawSnappedPolyline();
    	    var poly = new google.maps.Polyline({ 
		    	  map: map,
		    	  strokeColor: '#232943',
		    	  icons:[{
		    		  // create arrows to display the direction of the journey. 
		    		  icon: {
				          path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
				          strokeColor:'#232943',
				          fillColor:'#232943',
				          fillOpacity:1 
				          },
				          repeat:'100px',
		                  path:snappedCoordinates
		    	  		}]  
		      });
    	    
          	// function to display route from point to point on road. 
        	function processSnapToRoadResponse(data) {
        	  snappedCoordinates = [];
        	  var latlng;
        	  for (var i = 0; i < data.snappedPoints.length; i++) {
        		    latlng = new google.maps.LatLng(
        	        data.snappedPoints[i].location.latitude,
        	        data.snappedPoints[i].location.longitude);
        	    snappedCoordinates.push(latlng);
        	  }
        	}  

    	      //Loop and Draw Path Route between the Points on MAP
    	      for (var i = 0; i < snappedCoordinates.length; i++) {
    	          if ((i + 1) < snappedCoordinates.length) {
    	              var src = snappedCoordinates[i];
    	              var des = snappedCoordinates[i + 1];
    	              service.route({
    	                  origin: src,
    	                  destination: des,
    	                  travelMode: google.maps.DirectionsTravelMode.TRANSIT,
    	                  path:snappedCoordinates
    	              })
    	              path.push(src);
    	              path.push(des);
    	              poly.setPath(path);
    	          }
    	      }
    	  });
     
    	    });
    	}

//load in the weather onto map
var dWeather;
function changeWeatherIcon(weatherType) {
    weatherType = weatherType.toLowerCase();
    $("#wIcon").text("");
    $("#wIcon").append("<i></i>");
    // alter the default icons in favour of nicer icons. 
    if (weatherType.indexOf("clouds") != -1) {
        return $("#wIcon").addClass("wi wi-cloudy");
    } else if (weatherType.indexOf("rain") != -1) {
        return $("#wIcon").addClass("wi wi-rain");
    } else if (weatherType.indexOf("thunderstorm") != -1) {
        return $("#wIcon").addClass("wi wi-thunderstorm");
    } else if (weatherType.indexOf("snow") != -1) {
        return $("#wIcon").addClass("wi wi-snow");
    } else if (weatherType.indexOf("mist") != -1) {
        return $("#wIcon").addClass("wi wi-smoke");
    } else {
        return $("#wIcon").addClass("wi wi-day-sunny");
    }
}
// Function to alter all text for weather floating div. 
function titleCase(str) {
    var array = str.split(" ");
    for (var i = 0; i < array.length; i++) {
        var temp_array = array[i].split(''); // "ab" => "a","b"
        temp_array[0] = temp_array[0].toUpperCase(); // "a","b" => "A","b"

        for (var j = 1; j < temp_array.length; j++)
            temp_array[j] = temp_array[j].toLowerCase(); // "a","b" => "A","b"
        array[i] = temp_array.join(''); // "A","b" => "Ab"
    }

    return array.join(' ');
}

// Function for displaying output of predictions in divs.
var busNum = 0;
function getPredictedTimes(bus, stops){
	first_stop_distance = 	stops[0][5]
	last_stop_distance = stops[stops.length - 1][5]
    
    var arrival = new Date(bus[0][0].arrival.substring(6, 10), parseInt(bus[0][0].arrival.substring(3, 5)) - 1, bus[0][0].arrival.substring(0, 2), bus[0][0].arrival.substring(11, 13), bus[0][0].arrival.substring(14, 16), bus[0][0].arrival.substring(17, 19), 00);

    var currentTime = new Date();
    var diff = Math.abs(arrival - currentTime);

    var journey_time = 0;
    var no_stops;    
    for (var i = 0; i < bus.length; i++) {
    	var oldArrival = bus[i][0].arrival;
    	var newArrival = oldArrival.slice(11);
    	var stop = bus[i][0].stopid;
    	journey_time += bus[i][0]['duration'];
    	if (stops[i] != null){
            $('#ulOutput'+busNum).append('<li class="passed"><b>Arrival Time:&nbsp;</b>'
                    + newArrival + '&emsp;&emsp;<b>Stop ID:&nbsp</b>' + stop +
                    '&emsp;&emsp;<b>Stop Name:&nbsp;</b> ' + stops[i][3] + "<br>"
                    + '<i class="fa fa-bus fa-x8"></i>'+"<br>"+'</li>');
    	    if (i == bus.length - 1){
                last_stop_distance = stops[i][5]
            }
    	}
    	no_stops +=1;
    }
   $('#dueTime'+busNum).append("<b>" + bus[0][0].arrival.substring(11, 17) + "00" + "<b>" +"<br>");
  $('#journeyTime'+busNum).append("<b>" + Math.floor(journey_time/ 60) + " minutes" + "</b>");
  $('#distance'+busNum).append("<b>" + (Math.round((last_stop_distance - first_stop_distance) * 100) / 100) + "Km</b>");
  
  	// Calculate the cost section for the trip. 
    if (no_stops.length < 4) {
      $('#journeyPrice'+busNum).append("<b>Adult:</b> €2.00" + "<br>");
      $('#journeyPrice'+busNum).append("<b>Leap Card:</b> €1.50" + "<br>");
  } else if (no_stops.length > 3 && no_stops.length < 13){
      $('#journeyPrice'+busNum).append("<b>Adult:</b> €2.70" + "<br>");
      $('#journeyPrice'+busNum).append("<b>Leap Card:</b> €2.05" + "<br>");
  }
  else{
      $('#journeyPrice'+busNum).append("<b>Adult:</b> €3.30" + "<br>");
      $('#journeyPrice'+busNum).append("<b>Leap Card:</b> €2.60" + "<br>");
  }      
    document.getElementById('resultArray'+busNum).style.display = 'block';
    busNum += 1;
  }

function loadRoutes(){
    var counter = 0
    var a = $.getJSON("http://127.0.0.1:8000/dublinbuspredict/loadRoutesForMap", null, function(d) {
        $.each(d['list_routes'], function(i, p) {
            $('#dropdown-list-4').append($('<li></li>').val(p).html('<a onclick=getStops2("' + p + '")>' + p + '</a>'));
        })
        $.each(d['list_stops'], function(i, p) {
//            $('#dropdown-list-5').append($('<li></li>').val(p).html('<a onclick=getStopsStartingFromSource2("' + p + '")>' + p + '</a>'));
            list_origin_dropdown.push(p);
        })
    });
    var b = $.getJSON("http://127.0.0.1:8000/dublinbuspredict/getInfoNextPage", null, function(d) {
        route = d['route'];
        source = d['source'];
        destination = d['destination'];
        time = d['time']
        date = d['date']
        initMap()
        $.getJSON("http://api.openweathermap.org/data/2.5/weather?q=Dublin,Ireland&units=metric&APPID=33e340fbba76a4645e26160abb37f014", null, function(dWeather) {
            var weatherID = dWeather.weather[0].id;
            var weatherTemp = dWeather.main.temp;
            var weatherDesc = dWeather.weather[0].description;
            weatherDesc = titleCase(weatherDesc);
            var weatherIcon = changeWeatherIcon(weatherDesc);

            $("#wTemp1").addClass("wi wi-thermometer");
            $('#wTemp2').html("&nbsp" + weatherTemp);
            $('#wTemp3').html("°C");
            $('#wIcon').html(weatherIcon);
            $('#wDesc').html(weatherDesc);
        });
        if (time != "" || date != ""){
        	document.getElementById('displayWeather').style.display = 'none';
            getPredictionSchedule(route, source, destination, date, time)
        }
        else{
            getPredictions(route, source, destination)
        }
    });
}

function searchFunctionRoute2() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("search-box-4");
    filter = input.value.toUpperCase();
    ul = document.getElementById("dropdown-list-4");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function getStops2(route) {
    document.getElementById("search-box-4").value = route;
    document.getElementById('spinner5').style.display = 'block';
    document.getElementById('search-box-5').onkeyup = function(e){searchFunctionSRC2()};
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/pilotRoutes", {"route":route}, function(d) {
        document.getElementById("dropdown-list-5").innerHTML = "";
        document.getElementById("search-box-5").value = "";
        document.getElementById("search-box-6").value = "";
        $.each(d['stops'], function(i, p) {
            $('#dropdown-list-5').append($('<li></li>').val(p[0]).html('<a onclick=getStopsDest2(' + p[0] + ')>' + route + ' - ' + p[0] + '</a>'));
        });
        document.getElementById('spinner5').style.display = 'none';
    });
}

function searchFunctionSRC2() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("search-box-5");
    filter = input.value.toUpperCase();
    ul = document.getElementById("dropdown-list-5");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function getStopsDest2(source) {
    document.getElementById("search-box-5").value = source;
    route = document.getElementById("search-box-4").value;
    document.getElementById('spinner6').style.display = 'block';
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/pilotDest", {"route":route, "source":source}, function(d) {
        document.getElementById("dropdown-list-6").innerHTML = "";
        document.getElementById("search-box-6").value = "";
        $.each(d['stops'], function(i, p) {
            $('#dropdown-list-6').append($('<li></li>').val(p[0]).html('<a onclick=getStopsDestExtra2(' + p[0] + ')>' + route + ' - ' + p[0] + '</a>'));
        });
        document.getElementById('spinner6').style.display = 'none';
    });
}

function getStopsDestExtra2(stop){
    document.getElementById("search-box-6").value = stop;
    
    // Enable button once route, source and destination are input
	var routeInput = document.getElementById("search-box-4").value;
	var sourceInput = document.getElementById("search-box-5").value;
	var destInput = document.getElementById("search-box-6").value;
	
	if (routeInput !='' && sourceInput !='' && sourceInput !=''){
		document.getElementById("submit-route2").disabled = false;
	}    
}

function searchFunctionDest2() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("search-box-6");
    filter = input.value.toUpperCase();
    ul = document.getElementById("dropdown-list-6");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function getStopsStartingFromSource2(stop){
    document.getElementById("search-box-5").value = stop
    document.getElementById("dropdown-list-4").innerHTML = "";
    document.getElementById("search-box-4").value = "";
    document.getElementById("dropdown-list-6").innerHTML = "";
    document.getElementById("search-box-6").value = "";
    document.getElementById('spinner6').style.display = 'block';
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/getStopsStartingFromSource", {"source":stop}, function(d) {
        $.each(d['stops'], function(i, p) {
            $('#dropdown-list-6').append($('<li></li>').val(p).html('<a onclick=getStopsDestExtraRoute2(' + p + ')>'+ p + '</a>'));
        });
        document.getElementById('spinner6').style.display = 'none';
    });
}

function getStopsDestExtraRoute2(route){
    document.getElementById("search-box-6").value = route;
    document.getElementById("dropdown-list-4").innerHTML = "";
    document.getElementById("search-box-4").value = "";
    source = document.getElementById("search-box-5").value;
    dest = document.getElementById("search-box-6").value;
    document.getElementById('spinner4').style.display = 'block';
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/getStopsDestExtraRoute", {"source":source, "dest":dest}, function(d) {
        $.each(d['routes'], function(i, p) {
            $('#dropdown-list-4').append($('<li></li>').val(p).html('<a onclick=getExtraRoute2("' + p[0] + '")>'+ p[0] + '&emsp;&emsp;' + p[1] + 'Km</a>'));
        });
        document.getElementById('spinner4').style.display = 'none';
    });
}

function getExtraRoute2(route){
    document.getElementById("search-box-4").value = route;
    var routeInput = document.getElementById("search-box-4").value;
	var sourceInput = document.getElementById("search-box-5").value;
	var destInput = document.getElementById("search-box-6").value;

	if (routeInput !='' && sourceInput !='' && sourceInput !=''){
		document.getElementById("submit-route2").disabled = false;
	}
	$.getJSON("http://127.0.0.1:8000/dublinbuspredict/setStopsForMaps", {"route":route, "source":sourceInput, "dest":destInput}, function() {});
}

function loadRoutes2(){
    var counter = 0
    document.getElementById("dropdown-list-4").innerHTML = "";
    document.getElementById("search-box-4").value = "";
    document.getElementById("dropdown-list-5").innerHTML = "";
    document.getElementById("search-box-5").value = "";
    document.getElementById("dropdown-list-6").innerHTML = "";
    document.getElementById("search-box-6").value = "";
    var a = $.getJSON("http://127.0.0.1:8000/dublinbuspredict/loadRoutesForMap", null, function(d) {
        $.each(d['list_routes'], function(i, p) {
            $('#dropdown-list-4').append($('<li></li>').val(p).html('<a onclick=getStops2("' + p + '")>' + p + '</a>'));
        })
    });
    loadOrigin2();
}

function loadOrigin2(){
    document.getElementById('search-box-5').onkeyup = function(e){newSearch2()};
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/loadRoutesForMap", null, function(d) {
             $.each(d['list_stops'], function(i, p) {
                list_origin_dropdown.push(p);
             });
    });
}

function newSearch2(){
    stop = document.getElementById('search-box-5').value;
    var node;
    var textnode;
    text = '';
    document.getElementById("dropdown-list-5").innerHTML = "";
    var i;
    document.getElementById('spinner5').style.display = 'block';
    for(i = 0; i < list_origin_dropdown.length; i++){
        if (list_origin_dropdown[i].toString().indexOf(stop.toString()) != -1){
            if (stop.length > 0){
                var same = true;
                for (var j = 0; j < stop.length; j++){
                    if (stop[j] != list_origin_dropdown[i].toString()[j]){
                        same = false
                    }
                }
                if (same == true){
                    text += '<li><a onclick="getStopsStartingFromSource2('+ list_origin_dropdown[i] +')">' + list_origin_dropdown[i] + '</a></li>'
                }
            }
        }
    }
    document.getElementById("dropdown-list-5").innerHTML = text;
    document.getElementById('spinner5').style.display = 'none';
}

function getPredictions(route, source, destination){
    busNum = 0
    var buses = 0
    var direction = 0
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/getNumberBuses", {"route":route, "source":source}, function(d) {
        buses = d['buses']
        direction = d['direction']
        if (buses == 1){
            document.getElementById('spinner-result-0').style.display = 'block';
        }
        else if (buses == 2){
            document.getElementById('spinner-result-0').style.display = 'block';
            document.getElementById('spinner-result-1').style.display = 'block';
        }
        else if (buses == 3){
            document.getElementById('spinner-result-0').style.display = 'block';
            document.getElementById('spinner-result-1').style.display = 'block';
            document.getElementById('spinner-result-2').style.display = 'block';
        }
        if (buses != 'No buses found!'){
            $.getJSON("http://127.0.0.1:8000/dublinbuspredict/runModel", {"route":route, "source":source, "destination":destination, "direction":direction, "position":0}, function(d) {
                var d2 = d.info_buses;
                getPredictedTimes(d.info_buses[0], d.info_stops);
                document.getElementById('spinner-result-0').style.display = 'none';
                var bus0, bus1, bus2;
                if (buses > 1){
                    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/runModel", {"route":route, "source":source, "destination":destination, "direction":direction, "position":1}, function(d) {
                        var d2 = d.info_buses;
                        getPredictedTimes(d.info_buses[0], d.info_stops);
                        document.getElementById('spinner-result-1').style.display = 'none';
                        var bus0, bus1, bus2;
                        if (buses > 2){
                            $.getJSON("http://127.0.0.1:8000/dublinbuspredict/runModel", {"route":route, "source":source, "destination":destination, "direction":direction, "position":2}, function(d) {
                                var d2 = d.info_buses;
                                getPredictedTimes(d.info_buses[0], d.info_stops);
                                document.getElementById('spinner-result-2').style.display = 'none';
                                var bus0, bus1, bus2;
                            });
                        }
                    });
                }
            });
        }else{
            document.getElementById('fail2').style.display = 'block';
        }
    });
}

function getPredictionSchedule(route, source, destination, date, time){
    var busNum = 0;
    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/runQueries", {"route":route, "source":source, "destination":destination, "date":date, "time":time}, function(d) {
        var bus1 = [d.list_stops[0][0]]
        var bus2 = [d.list_stops[0][1]]
        var bus3 = [d.list_stops[0][2]]
        var stops1 = [d.list_stops[1]]
        var stops2 = [d.list_stops[2]]
        var stops3 = [d.list_stops[3]]
        var stops = d.stops
        document.getElementById('spinner-result-0').style.display = 'block';
        document.getElementById('spinner-result-1').style.display = 'block';
        document.getElementById('spinner-result-2').style.display = 'block';
        $.getJSON("http://127.0.0.1:8000/dublinbuspredict/runPlanner", {"route":route, "source":source, "destination":destination, "date":date, "time":time, 'bus':bus1, 'stops': stops1}, function(d1) {
            if (d1 === "No buses found1!"){
                document.getElementById('fail').style.display = 'block';
            }
            else{
                displayPredictionSchedule(d1.info_buses, busNum, d1.stops)
                busNum += 1;
                document.getElementById('spinner-result-0').style.display = 'none';
                $.getJSON("http://127.0.0.1:8000/dublinbuspredict/runPlanner", {"route":route, "source":source, "destination":destination, "date":date, "time":time, 'bus':bus2, 'stops': stops2}, function(d2) {
                    if (d2 === "No buses found2!"){
                        document.getElementById('fail').style.display = 'block';
                    }
                    else{
                        if (d2.stops [0] != null){
                            displayPredictionSchedule(d2.info_buses, busNum, d2.stops )
                            busNum += 1;
                        }
                        document.getElementById('spinner-result-1').style.display = 'none';
                    }
                    $.getJSON("http://127.0.0.1:8000/dublinbuspredict/runPlanner", {"route":route, "source":source, "destination":destination, "date":date, "time":time, 'bus':bus3, 'stops': stops3}, function(d3) {
                        if (d3 === "No buses found3!"){
                            document.getElementById('fail').style.display = 'block';
                        }
                        else{
                            if (d3.stops[0] != null){
                            console.log('????', d3.stops)
                                displayPredictionSchedule(d3.info_buses, busNum, d3.stops)
                            }
                            document.getElementById('spinner-result-2').style.display = 'none';
                        }
                    });
                });
            }
        });
    });
}

function displayPredictionSchedule(bus, busNum, stops){
    var arrival = bus[0].predicted_arrival_time;
    var journey_time = 0;
    var no_stops;
    first_stop_distance = stops[0][3]
	last_stop_distance = stops[stops.length - 1][3]
    for (var i = 0; i < bus.length; i++) {
        var oldArrival = bus[i].predicted_arrival_time;
        var newArrival = oldArrival.slice(11);
        var stop = bus[i].stopid;
        journey_time += bus[i].duration;
        $('#ulOutput'+busNum).append('<li class="passed"><b>Arrival Time:&nbsp;</b>'
                + newArrival + '&emsp;&emsp;<b>Stop ID:&nbsp</b>' + stop +
                '&emsp;&emsp;<b>Stop Name:&nbsp;</b>' + stops[i][2] + "<br>"
                + '<i class="fa fa-bus fa-x8"></i>'+"<br>"+'</li>');
        no_stops ++;
    }
    $('#dueTime'+busNum).append("<b>" + arrival.slice(11)
           + "<b>" +"<br>");
    $('#journeyTime'+busNum).append("<b>" + Math.floor(journey_time/ 60) + " minutes" + "</b>");
    $('#distance'+busNum).append("<b>" + (Math.round((last_stop_distance - first_stop_distance) * 100) / 100) + "Km</b>");

    
    // Calculate the cost section for the trip.
    if (stops.length < 4) {
      $('#journeyPrice'+busNum).append("<b>Adult:</b> €2.00" + "<br>");
      $('#journeyPrice'+busNum).append("<b>Leap Card:</b> €1.50" + "<br>");
    } else if (stops.length > 3 && stops.length < 13){
      $('#journeyPrice'+busNum).append("<b>Adult:</b> €2.70" + "<br>");
      $('#journeyPrice'+busNum).append("<b>Leap Card:</b> €2.05" + "<br>");
    }
    else{
      $('#journeyPrice'+busNum).append("<b>Adult:</b> €3.30" + "<br>");
      $('#journeyPrice'+busNum).append("<b>Leap Card:</b> €2.60" + "<br>");
    }
    document.getElementById('resultArray'+busNum).style.display = 'block';
    busNum += 1;
}

//function to center based on geolocation button. 
function geoLocation(){
	map.setZoom(12);
	map.setCenter(pos);
}
// add click event to geolocation button
$(document).ready(function (){
  $("#buttonLocation2").on('click', function ()
  {
	  geoLocation();	  
	});
});

