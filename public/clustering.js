document.getElementById("defaultOpen").click();

function changeTab(evt, timerange) {
  // Declare all variables
  var i, tablinks;

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // add an "active" class to the button that opened the tab
  evt.currentTarget.className += " active";

  if(timerange == "hour") data_path = "data/hour/";
  if(timerange == "day") data_path = "data/day/";
  if(timerange == "week") data_path = "data/week/";

  removeAllCollapsibles();
  updateMap();
}

// add collapsible after another
function insertAfter(newNode, referenceNode) {
  referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

// toggle collapse of specified content
function toggleContent(content) {
  if (content.style.maxHeight) {
    content.style.maxHeight = null;
  } else {
    content.style.maxHeight = content.scrollHeight + 'px';
  }
}

// collapse all open content
function collapseAllOpenContent() {
  const colls = document.getElementsByClassName('collapsible');
  for (const coll of colls) {
    if (coll.classList.contains('active')) {
      coll.classList.remove('active');
      toggleContent(coll.nextElementSibling);
    }
  }
}

// create a new collapisble given the title and the content
function newCollapsible(title, content_str, title_id, class_){
  var newButton = document.createElement("button");
  newButton.setAttribute("type", "button");
  newButton.setAttribute("class", "collapsible " + class_);
  newButton.setAttribute("id", title_id + class_);
  newButton.setAttribute("title", class_);

  newButton.innerHTML = title;

  var newContent = document.createElement("div");
  newContent.setAttribute("class", "content");
  newContent.innerHTML = content_str;

  var currentDiv = document.getElementsByClassName("content");
  insertAfter(newButton, currentDiv[currentDiv.length - 1])
  insertAfter(newContent, newButton)

  newButton.addEventListener("click", function() {
    if (!this.classList.contains('active')) {
      collapseAllOpenContent();
    }
    this.classList.toggle("active");
    toggleContent(this.nextElementSibling);
  });
}

// add collapsibles to HTML
function addCollapsibles(data, class_){
  for(var i = 0; i < data.length; i++){
    var colTitle = data[i].properties.title;
    var title = colTitle;
    var color = "#0000ff";
    if(class_ == "A") color = "#51525c";
    if(class_ == "B1") color = "#826d6f";
    if(class_ == "B2") color = "#1e2833";

    var t_counter = counterText(data[i].properties.cluster_counter, data[i].properties.marker_counter, color);

    colTitle = "<i>" + title + "</i>&nbsp&nbsp" + t_counter;
    if(class_ == "Z") colTitle = "<i>" + title + "</i>&nbsp&nbspprovince";

    var colBody = "";
    for(var entry of data[i].properties.entries){
      if(entry.place != "-") colBody += "<p>place: " + entry.place + "<br>user: " + entry.user + "<br>text: " + entry.text + "</p>";
      else colBody += "<p>user: " + entry.user + "<br>text: " + entry.text + "</p>";
    }
    newCollapsible(colTitle, colBody, title, class_);
  }
}

// remove collapsibles from HTML
function removeCollapsibles(data, class_){
  for(var i = 0; i < data.length; i++){
    var colTitle = data[i].properties.title;
    var col = document.getElementById(colTitle + class_);
    col.remove();
  }
}

// remove all collapsibles from HTML
function removeAllCollapsibles(){
  collapseAllOpenContent();
  var some_left = true;
  while(some_left){
    const colls = document.getElementsByClassName('collapsible');
    for (const coll of colls) {
      coll.remove();
    }
    if(colls.length == 0) some_left = false;
  }
}

// control maximum radius of circles
function maxRadius(value, max_value){
  var new_value = 2 * value;
  var min_value = 7;
  if(new_value > max_value) return max_value;
  if(new_value < min_value) return min_value;
  else return new_value;

}

// return text to print on counter
function counterText(c_cluster, c_marker, color){
  //folder: c_cluster + " &#x1F4C1 ";
  //marker: c_marker + "&#x1F4CD";
  var cluster_icon = ' <span style="color: ' + color + ';">&#8857;</span>';
  var marker_icon = ' <span style="color: ' + color + '; vertical-align: middle;">&#8226;</span>';
  var t_cluster = c_cluster + cluster_icon;
  var t_marker = c_marker + marker_icon;
  if(c_cluster == 1) return c_cluster + marker_icon;
  if(c_cluster == 0) return t_marker;
  if(c_marker == 0) return t_cluster;
  else return t_cluster + " + " + t_marker;
}

function checkIfData(d1, d2, d3, d4){
  if(typeof d1 == 'undefined' & typeof d2 == 'undefined' & typeof d3 == 'undefined' & typeof d4 == 'undefined')
    document.getElementById("no-content").innerHTML = "There are no tweets available for this time range";
  else document.getElementById("no-content").innerHTML = "";
}

// create class CircleMarker that also contains a counter
customCircleMarker = L.CircleMarker.extend({
   options: {
      counter_text: "0"
   }
});

// global variables
var map;
var mapZoom = 8;
var mapPosition = [41.702209, 2.057584];
var data_path;
var previous_zoom = 8;

function updateMap(){

  mapZoom = 8;
  previous_zoom = 8;

  // create request for reading JSON file
  var xmlhttp1 = new XMLHttpRequest();
  xmlhttp1.onreadystatechange =
  function(){
    if (this.readyState == 4 && this.status == 200) {
      var myObj1 = JSON.parse(this.responseText);
      var data_json1 = myObj1.features;

      // keep refreshing map
      $(document).ready(function() {
        refreshMap();
        $(".map-refresh-needed").change(function() {
          refreshMap();
        });
      });

      // define what will be done each time there is some interaction with the map
      function refreshMap() {
        var baseTiles = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            maxZoom: 18,
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            id: 'mapbox/streets-v11',
            accessToken: 'pk.eyJ1IjoiYmVydGFiZW5ldCIsImEiOiJja2p0d2g0MGcwMTF1Mnhtc2tobWtuYmoxIn0.HBE73qDutz5qreLjiSt2RQ'
          });

        // setting map
        if (map) {
          map.remove();
        }

        // create map layers
        map = L.map("map-content", { minZoom: mapZoom, maxZoom: 10, zoomControl: false }).setView(
          mapPosition,
          mapZoom
        );
        L.control.zoom({position: "bottomleft"}).addTo(map);

        map.on("moveend", function() {
          mapPosition = map.getCenter();
        });

        baseTiles.addTo(map);

        // define circles of class A
        var markers1 = L.geoJSON(myObj1, {
          pointToLayer: function(geoJsonPoint, latlng) {
            return new customCircleMarker(latlng, {
              fillColor: "#7b7d8a",
              color: "#7b7d8a",
              title: geoJsonPoint.properties.title,
              radius: maxRadius(geoJsonPoint.properties.cluster_counter, 40),
              counter_text: geoJsonPoint.properties.cluster_counter + geoJsonPoint.properties.marker_counter,
              visible: true});
          },
          // add numbered text
          onEachFeature: function(feature, layer){
            var text = L.tooltip({
                permanent: false,
                direction: 'center',
                className: 'text'
            })
            .setContent(function(){
              var c = layer.options.counter_text;
              if (c == 1) return "";
              if (layer.options.visible == false) return "";
              return c.toString()
            })
            .setLatLng(layer.getLatLng());
            text.addTo(map);
          }
        // when click, open/close content of collapsible
        }).on("click", function(m){
            var title = m.layer.options.title;
            var col = document.getElementById(title + "A");

            if (!col.classList.contains('active')) {
              collapseAllOpenContent();
            }
            col.classList.toggle("active");
            toggleContent(col.nextElementSibling);
        }).addTo(map);

        var xmlhttp2 = new XMLHttpRequest();
        xmlhttp2.onreadystatechange =
        function(){
          if (this.readyState == 4 && this.status == 200) {
            var myObj2 = JSON.parse(this.responseText);
            var data_json2 = myObj2.features;

            // define markers of class B2
            var markers2 = L.geoJSON(myObj2, {
              pointToLayer: function(geoJsonPoint, latlng) {
                return new customCircleMarker(latlng, {
                  fillColor: "#304257",
                  color: "#304257",
                  fillOpacity: 1.0,
                  title: geoJsonPoint.properties.title,
                  radius: 6,
                  counter_text: geoJsonPoint.properties.cluster_counter + geoJsonPoint.properties.marker_counter,
                  visible: true});
              }
            // when click, open/close content of collapsible
            }).on("click", function(m){
                var title = m.layer.options.title;
                var col = document.getElementById(title + "B2");

                if (!col.classList.contains('active')) {
                  collapseAllOpenContent();
                }
                col.classList.toggle("active");
                toggleContent(col.nextElementSibling);
            });

            var xmlhttp3 = new XMLHttpRequest();
            xmlhttp3.onreadystatechange =
            function(){
              if (this.readyState == 4 && this.status == 200) {
                var myObj3 = JSON.parse(this.responseText);
                var data_json3 = myObj3.features;

                // define markers of class B1
                var markers3 = L.geoJSON(myObj3, {
                  pointToLayer: function(geoJsonPoint, latlng) {
                    return new customCircleMarker(latlng, {
                      fillColor: "#b8989b",
                      color: "#b8989b",
                      fillOpacity: 1.0,
                      title: geoJsonPoint.properties.title,
                      radius: 6,
                      counter_text: geoJsonPoint.properties.cluster_counter + geoJsonPoint.properties.marker_counter,
                      visible: true});
                  }
                // when click, open/close content of collapsible
                }).on("click", function(m){
                    var title = m.layer.options.title;
                    var col = document.getElementById(title + "B1");

                    if (!col.classList.contains('active')) {
                      collapseAllOpenContent();
                    }
                    col.classList.toggle("active");
                    toggleContent(col.nextElementSibling);
                }).addTo(map);

                var xmlhttp4 = new XMLHttpRequest();
                xmlhttp4.onreadystatechange =
                function(){
                  if (this.readyState == 4 && this.status == 200) {
                    var myObj4 = JSON.parse(this.responseText);
                    var data_json4 = myObj4.features;

                    checkIfData(data_json1, data_json2, data_json3, data_json4);

                    // change visible layers depending on zoom level
                    map.on("zoomend", function() {
                      checkIfData(data_json1, data_json2, data_json3, data_json4);
                      collapseAllOpenContent();
                      var texts = document.getElementsByClassName("text");
                      if(map.getZoom() == 9 & previous_zoom == 8){
                          // remove furthest
                          for(var i = 0; i < texts.length; i++){
                            texts[i].style.visibility = 'hidden'; // visible
                          }
                          map.removeLayer(markers1);
                          removeCollapsibles(data_json1, "A");

                          // add closest
                          markers2.addTo(map);
                          addCollapsibles(data_json2, "B2");

                          // manage collapsible order
                          removeCollapsibles(data_json4, "Z");
                          addCollapsibles(data_json4, "Z")

                      }
                      else if(map.getZoom() == 8){
                        // manage collapsible order
                        removeCollapsibles(data_json4, "Z");

                        addCollapsibles(data_json1, "A");
                        addCollapsibles(data_json4, "Z");

                        // add furthest
                        markers1.addTo(map);
                        for(var i = 0; i < texts.length; i++){
                          texts[i].style.visibility = 'visible';
                        }

                        // remove closest
                        map.removeLayer(markers2);
                        removeCollapsibles(data_json2, "B2");

                      }
                      previous_zoom = map.getZoom();
                    });

                    // initialize all collapsibles
                    addCollapsibles(data_json3, "B1");
                    addCollapsibles(data_json1, "A");
                    addCollapsibles(data_json4, "Z");

                  }
                };
                xmlhttp4.open("GET", data_path + "geojson_clustering_classZ.json", true);
                xmlhttp4.send();

              }
            };
            xmlhttp3.open("GET", data_path + "geojson_clustering_classB1.json", true);
            xmlhttp3.send();

          } // end of if (this.readyState == 4 && this.status == 200)
        }; // end of XMLHttpRequest
        //xmlhttp2.open("GET", "data/geojson_clustering_allplaces.json", true); // 100
        xmlhttp2.open("GET", data_path + "geojson_clustering_classB2.json", true);
        xmlhttp2.send();

      } // end of refreshMap
    } // end of if (this.readyState == 4 && this.status == 200)
  }; // end of XMLHttpRequest
  xmlhttp1.open("GET", data_path + "geojson_clustering_classA.json", true);
  xmlhttp1.send();
}
