var checkDBInterval = undefined;
var getROIInterval = undefined;
var getImageInterval = undefined;
 
function getTableForData(items) {
    var html = '\
    <table class="table">\
        <thead>\
            <tr>\
                <th scope="col">ID</th>\
                <th scope="col">Nome</th>\
                <th scope="col">Anno</th>\
            </tr>\
        </thead>\
        <tbody>';
    items.forEach(function (item) {
        html += '\
        <tr>\
            <th scope="row">' + item.id + '</th>\
            <th>' + item.name + '</th>\
            <th>' + item.year + '</th>\
        </tr>';
    });
    html += '\
        <tbody>\
    </table>';
    return html;
}

function checkCameraSocketThreads() {
  checkDBInterval = setInterval(function() {
    // alert("Interval reached every 5s");
    $.ajax({
      url: "are-camera-connections-alive",
      type: "GET",
      success: function (response) {

        console.log("Thread socket-camera are active: ");
        console.log(response);

      },
      error: function (xhr) {
        colorBackgroundErrorCase();
      },
    });
  }, 100);
}

function colorBackgroundErrorCase() {
  $("body").css('background-color', 'red');
}


function removeRedBackground() {
  $("body").css('background-color', 'white');
}

function write_state_to_db(){

  checkDBInterval = setInterval(function() {

    $.ajax({
      url: "/write_system_state",
      type: "GET",
      success: function (response) {
        console.log("WRITE STATE TO DB");
      }
    });
  },20000);

}

function checkStateConnectivity() {
  checkDBInterval = setInterval(function() {
    // alert("Interval reached every 5s");
    $.ajax({
      url: "/check_system_state",
      type: "GET",
      success: function (response) {

        console.log("JS STATE " + response);

        //---------------DB
        if (response['db']) {
          $('#db-status').removeClass('table-danger').addClass('table-success');

          $("#db-status img").attr("src", "static/img/database-checkmark-icon.png");

          if ($('#mymodal').is(':visible')) {
            $('#mymodal').modal('hide')
          }
        }
        if (!response['db']) {
          $('#db-status').removeClass('table-success').addClass('table-danger');

          $("#db-status img").attr("src", "static/img/database-remove-icon.png");

          if (!$('#mymodal').is(':visible')) {
            console.log('MODAL SHOW')
            //prevent modal from closing on click
            $('#mymodal').modal({
              backdrop: 'static',
              keyboard: false
            })
            $('#mymodal').modal('show')
          }
        }
        
        //---------CAMERA
        if(response["ping_camera"]){
          $("#camera_state").addClass('table-success').removeClass('table-danger');
          $("#camera_state img").attr("src", "static/img/black-camera-icon.png");
        }

        if(!response["ping_camera"]){
          $("#camera_state").addClass('table-danger').removeClass('table-success');
          $("#camera_state img").attr("src", "static/img/no-image-photography-icon.png");
        }

        //TEACH
        if(response["check_teach"]==1){
          console.log("Check Teach")
          $("#check_teach_state").addClass('table-success').removeClass('table-info');
        }

        if(response["check_teach"]==2){
          $("#check_teach_state").addClass('table-danger').removeClass("table-info");
        }

        //BYPASS

        // if(response["bypass"]){
        //   $("#bypass_view").addClass('table-success').removeClass("table-danger");
        // }
        // if(!response["bypass"]){
        //   $("#bypass_view").addClass('table-danger').removeClass("table-success");
        // }


      },
      error: function (xhr) {
        colorBackgroundErrorCase();
      },
    });
  }, 350);
}

function runAfterElementExists(jquery_selector,callback){
  var checker = window.setInterval(function() {
   //if one or more elements have been yielded by jquery
   //using this selector
   if ($(jquery_selector).length) {

      //stop checking for the existence of this element
      clearInterval(checker);

      //call the passed in function via the parameter above
      callback();
      }}, 200); //I usually check 5 times per second
}

function detectionResult() {
  checkDBInterval = setInterval(function() {
    // alert("Interval reached every 5s");
    $.ajax({
      url: "/getdetectionresult",
      type: "GET",
      success: function (response) {

        // $('#detection_threshold').html(response["score_value"]);

        $('.img-score h2').text("Score: " + response["score_value"] + " %");

        console.log(response["detection_result"]);
        
        //DETECTION RESULT
        if(response["detection_result"]=="P" || response["detection_result"]=="1"  ){
          
          $("#detection_result").addClass('table-success').removeClass('table-danger');

          // $("#detection_threshold_first_letter").addClass('table-success').removeClass('table-danger');
          // $("#detection_threshold_second_letter").addClass('table-success').removeClass('table-danger');
          // $("#detection_threshold_first_letter").html("<b> O </b>");
          // $("#detection_threshold_second_letter").html("<b> K </b>");
          $("#pass_fail").attr("src", "static/img/check-mark-icon.png");
          $("#pass_fail_td").css("background", "#00FF00");

          $('.img-score h2').css('color', '#008000');
        }

        if (response["detection_result"]=="F" || response["detection_result"]=="0" ){
         
          $("#detection_result").addClass('table-danger').removeClass('table-success');

          // $("#detection_threshold_first_letter").addClass('table-danger').removeClass('table-success');
          // $("#detection_threshold_second_letter").addClass('table-danger').removeClass('table-success');
          // $("#detection_threshold_first_letter").html("<b> K </b>");
          // $("#detection_threshold_second_letter").html("<b> O </b>");

          $("#pass_fail").attr("src", "static/img/close-icon.png");
          $("#pass_fail_td").css("background", "#FF0000");
          $('.img-score h2').css('color', '#B70000');
        }

       

        if(!response["db_check_order"] || (response["detection_result"]=="F" || response["detection_result"]=="0")){

          colorBackgroundErrorCase();

        }else{

          removeRedBackground();
        }
        
        // if(response["db_check_order"]){
        //   $("#main_container").css('background-color', 'white');
        // }

      },
      error: function (xhr) {
        colorBackgroundErrorCase();
      },
    });
  }, 500);
}



function sendBboxToFlask(bbox) {
  $.ajax({
    type: "POST",
    url: "/overlay-teach",
    data: JSON.stringify(bbox),
    contentType:"application/json; charset=utf-8"
  });
}

function hideCropperJsAtStartup() {
  console.log("HideCropper");
  $(".cropper-crop-box").attr("hidden",true);
  $("#teach").removeClass("btn-primary").addClass("btn-secondary");
}

function setCropperLocationDimension() {
  $.ajax({
    type: "GET",
    url: "/get-roi",
    success: function(result) {
      console.log("ROI");
      console.log(result);

      roi_cx = result["roi_cx"];
      roi_cy = result["roi_cy"];
      roi_half_width = result["roi_half_width"];
      roi_half_height = result["roi_half_height"];
      scale_factor = result["scale_factor"];

      left = (roi_cx - roi_half_width) / scale_factor;
      top_ = (roi_cy - roi_half_height) / scale_factor;
      roi_width = roi_half_width * 2 / scale_factor;
      roi_height = roi_half_height * 2 / scale_factor;

      $('#imageForProcessing').data('cropper').setCropBoxData({
        'left': left, 'top': top_, 'width': roi_width, 'height': roi_height
      });
    }
  });
}

function enableOrDisableBypassButton() {
  $.ajax({
    type: "GET",
    url: "/bypass_callback",
    success: function (result) {
      
      if(result["bypass"]){
        $("#bypass_view").addClass('table-success').removeClass("table-danger");
        $("#bypass").attr("disabled", true);
      }else{
        $("#bypass_view").addClass('table-danger').removeClass("table-success");
        $("#warningBypassNotClickable").hide();
      }
      console.log(result);
    }
  });
}

function getCameraLastAccess() {

  checkDBInterval = setInterval(function() {
    $.ajax({
      type: "GET",
      url: "/get-camera-last-access",
      success: function (result) {
        console.log(result);
        $("#camera_last_access").html("Ultima acquisizione: " + result["camera_last_access"]);
      }
    });
  }, 350);
}

function getOrderMachineProcessingQuantity() {
  checkDBInterval = setInterval(function() {

    $.ajax({
      type: "GET",
      url: "/get-order-machine-processing-quantity",
      success: function (result) {
        console.log(result);
        var ompq = "Commessa: " + result["order"] + " - " +
        "Macchina: " + result["machine"] + " - " +
        "Lavorazione: " + result["processing"] + " - " +
        "Quantità: " + result["quantity"];
        $("#order_machine_processing_quantity").html(ompq);
      }
    });

  }, 350);
}

$(function () {
    checkStateConnectivity();
    detectionResult();
    enableOrDisableBypassButton();
    write_state_to_db();
    getCameraLastAccess();
    getOrderMachineProcessingQuantity();
    //checkCameraSocketThreads();

    $('.img-score').draggable({
      containment: ".img-container"
    });

    $("#trigger").bind("click", function () {
      $.ajax({
        type: "POST",
        url: "/trigger",
        success: function (result) {
          console.log(result);
        }
      });
    });
    
    //close connect to database
    $("#closeCntDatabase").bind("click", function () {
        
        $.ajax({
            type: "POST",
            url: "/closedb",
            success: function (result) {
                $("#connectionDBStatus").text("NON sei connesso al database e alla telecamera");
                $("#connectionDBStatus").css('color', 'red');

                clearInterval(checkDBInterval);
            }
        });
    });
    
    $("#velogo").bind('click', function () { 
      $("#VELogoModal").modal();
    });

    //get data
    $("#getDataFromDatabase").bind("click", function () {
        $.ajax({
            type: "GET",
            url: "/getdbdata",
            success: function (items) {
                $("#dbDataTable").html(getTableForData(items));
            },
            fail: function(result) {
                $("#dbDataTable").html("<p> Non connesso al DB -> Prima clicca per connetterti </p>");
            }
        });
    });

    //connect to database
    $("#openCntDatabase").bind("click", function () {
      $.ajax({
        type: "POST",
        url: "/connectdb",
        success: function (result) {
            $("#connectionDBStatus").text("Connesso al database e alla telecamera");
            $("#connectionDBStatus").css('color', 'green');

            checkDBConnectivity();
        }
      });
    });

    //connect to database
    $("#bypass").bind("click", function () {
      console.log("CLIIIIIIIIIIIIIIIIIIIIIIIIIIICK DISABLED");

      $.ajax({
        type: "POST",
        url: "/bypass_callback",
        success: function (result) {
          
          if(result["bypass"]){
            $("#bypass_view").addClass('table-success').removeClass("table-danger");
          }else{
            $("#bypass_view").addClass('table-danger').removeClass("table-success");
          }
          console.log(result);
        }
      });
    });

    $("#shutdown").bind("click", function () {
      $("#shutdownModal").modal();
    });

    $("#proceedShutdown").bind("click", function() {
      $.ajax({
        type: "POST",
        url: "/shutdown",
        success: function (result) {
          console.log(result);
        }
      });
    });

    $("#teach").bind("click", function () {
      
      if($("#teach").hasClass("btn-secondary")){
        
        setCropperLocationDimension();

        console.log("btn-secondary");
        $(".cropper-crop-box").removeAttr('hidden');
        $("#teach").removeClass("btn-secondary").addClass("btn-primary");
      }
      else{
        console.log("btn-primary");
        $(".cropper-crop-box").attr("hidden",true);
        $("#teach").removeClass("btn-primary").addClass("btn-secondary");

        //chima la funzione di teach per imparare
        $.ajax({
          type: "POST",
          url: "/teach",
          success: function (result) {
            $("#check_teach_state").addClass('table-info').removeClass('table-danger').removeClass('table-success');
            
            console.log(result);
          }
        }); 
      }
    });


     //connect to database
     $("#stop").bind("click", function () {
      $.ajax({
        type: "POST",
        url: "/stop_system",
        success: function (result) {
          
          console.log(result);
        }
      });
    });

  $('#imageForProcessing').cropper({
    dragMode: 'none',
    zoomable: false,
    zoomOnWheel: false,
    rotatable: false,
    movable: false,
    crop: function(event) {
      var actualWidth = eval($('#imageForProcessing').prop('width'));
      var actualHeight = eval($('#imageForProcessing').prop('height'));
      var originalWidth = document.querySelector('#imageForProcessing').naturalWidth;
      var originalHeight = document.querySelector('#imageForProcessing').naturalHeight;
      var ratioWidth = originalWidth / actualWidth;
      var ratioHeight = originalHeight / actualHeight;

      var cropper = $('#imageForProcessing').data('cropper');
      cropper.cropBoxData.maxWidth = 300;
      cropper.cropBoxData.maxHeight = 300; 

      // console.log("x :" + event.detail.x);
      // console.log("y :" + event.detail.y);
      // console.log("width :" + event.detail.width);
      // console.log("height :" + event.detail.height);
      // console.log("------------------------");

      var bbox = {
        "x-top": event.detail.x, 
        "y-top": event.detail.y, 
        "x-bottom": event.detail.width, 
        "y-bottom": event.detail.height
      };

      // console.log("Loaded cropper");

      $('.cropper-view-box').css({'outline': '4px solid #ff0000'})
      $('.cropper-modal').css({ 'background-color' : '', 'opacity' : '0' });
      $('.cropper-point').css({'background-color': 'red', 'height': '20px', 
      'width': '20px', 'opacity': '1'});
      // $('.cropper-line').css({'width': '10px', 'opacity': '1', 'background-color': 'red'});
      
      // console.log(bbox);
      sendBboxToFlask(bbox);  
    }
  });
  
  runAfterElementExists(".cropper-crop-box", function() {
    hideCropperJsAtStartup();
  
    });
     
    
});


