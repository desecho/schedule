angular.module('freeTimeSave', ['ngResource']).
  factory('FreeTimeSave', function($resource) {
    return $resource('/save-free-time/', {}, {
      post: {method: 'POST', headers: headers}
    });
  });

var class_name = 'free-hour';
var empty_time = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]};

var App = angular.module('schedule', ['loadingIndicator', 'freeTimeSave']);
App.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

function TimeSelectionController($scope, FreeTimeSave) {
  $scope.mousedown = false;
  $scope.result = JSON.stringify(empty_time);
  $scope.select_hour = function(event){
    function mark_hour(){
      id = angular.element(event.target).attr('id');
      $('#' + id).toggleClass(class_name);
    }
    function generate_result(){
      function parse_day_and_hour(code){
        var pattern = /(\d)_(\d{2})/g;
        var match = pattern.exec(code);
        var day = match[1];
        var hour = match[2];
        return [day, hour];
      }
      var time = empty_time;
      $.each($('.free-hour'), function(id, element) {
        id = $(element).attr('id');
        day_and_hour = parse_day_and_hour(id);
        day = day_and_hour[0];
        hour = day_and_hour[1];
        time[day].push(hour);
      });
      return JSON.stringify(time);
    }
    if ($scope.mousedown) {
      mark_hour();
      $scope.result = generate_result();
    }
  };

  var load = function(time) {
    function mark_time() {
      $.each(time, function(day, hours) {
        $.each(hours, function(index, hour) {
          $('#' + day + '_' + hour).addClass(class_name);
        });
      });
    }
    mark_time();
  };

  $scope.reset = function(){
    $('.hour').removeClass(class_name);
  };

  $scope.mouse_down = function(event){
    $scope.mousedown = true;
    $scope.select_hour(event);
  };

  $scope.mouse_up = function(){
    $scope.mousedown = false;
  };

  $scope.save = function(){
    FreeTimeSave.post($.param({free_time: $scope.result}), function (data) {
    }, function () {
      displayMessage(false, 'Ошибка сохранения');
    }
    );
  };

  if (typeof time !== 'undefined') load(time);
  // Register student

  $scope.submitForm = function(){
    $('#id_time_preference').val($scope.result);
    if ($('form').valid()) {
      $('form').submit();
    }
  };

  if (typeof $('#id_time_preference') !== 'undefined') load($.parseJSON($('#id_time_preference').val()));

}