angular.module('freeTime', ['ngResource']).
  factory('FreeTime', function($resource) {
    return $resource('/load-free-time/', {}, {
      get: {method: 'GET'}
    });
  });

angular.module('freeTimeSave', ['ngResource']).
  factory('FreeTimeSave', function($resource) {
    return $resource('/save-free-time/', {}, {
      post: {method: 'POST', headers: headers}
    });
  });

var class_name = 'free-hour';

var App = angular.module('schedule', ['loadingIndicator', 'freeTime', 'freeTimeSave']);
App.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

function FreeTimeController($scope, FreeTime, FreeTimeSave) {
  $scope.mousedown = false;
  $scope.select_hour = function(event){
    if ($scope.mousedown) {
      id = angular.element(event.target).attr('id');
      $('#' + id).toggleClass(class_name);
    }
  };

  $scope.load = function() {
    FreeTime.get({}, function (data) {
      function mark_time() {
        $.each($scope.time, function(day, hours) {
          $.each(hours, function(index, hour) {
            $('#' + day + '_' + hour).addClass(class_name);
          });
        });
      }
      $scope.time = data.time;
      mark_time();
    });
  };

  $scope.reset = function(event){
    $('.hour').removeClass(class_name);
  };

  $scope.mouse_down = function(event){
    $scope.mousedown = true;
    $scope.select_hour(event);
  };

  $scope.mouse_up = function(){
    $scope.mousedown = false;
  };

  $scope.save = function(event){
    function parse_day_and_hour(code){
      var pattern = /(\d)_(\d{2})/g;
      var match = pattern.exec(code);
      var day = match[1];
      var hour = match[2];
      return [day, hour];
    }
    $scope.time = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]};
    $.each($('.free-hour'), function(id, element) {
      id = $(element).attr('id');
      day_and_hour = parse_day_and_hour(id);
      day = day_and_hour[0];
      hour = day_and_hour[1];
      $scope.time[day].push(hour);
    });

    FreeTimeSave.post($.param({free_time: JSON.stringify($scope.time)}), function (data) {

    }, function () {
      displayMessage(false, 'Ошибка сохранения');
    }
    );

    console.log($scope.time);
    console.log(JSON.stringify($scope.time));
  };

  $scope.load();
}