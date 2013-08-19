angular.module('scheduleService', ['ngResource']).
  factory('Schedule', function($resource) {
    return $resource('/schedule/' + start_date_current, {}, {
      get: {method: 'GET'}
    });
  });

angular.module('saveSettings', ['ngResource']).
  factory('Settings', function($resource) {
    return $resource('/apply-settings/', {}, {
      post: {method: 'POST',
        headers:{
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'X-Requested-With': 'XMLHttpRequest',
        }
      }
    });
  });

var App = angular.module('schedule', ['ui.bootstrap', 'ui.select2', 'scheduleService', 'saveSettings']);
App.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
}).config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/', {action: 'home'}).
    when('/teacher-:teacher/student-:student/subject-:subject/', {action: 'filter'}).
    otherwise({redirectTo: '/'});
}]);

function ScheduleController($scope, $route, $routeParams, $location, $dialog, Schedule, Settings) {

  var filter_names = ['teacher', 'student', 'subject'];
  $scope.filters = {};
  $scope.schedule_mode = schedule_mode; //enable set schedule by default

  $scope.saveModeSettings = function() {
    settings = JSON.stringify({mode: $scope.schedule_mode});
    data = $.param({'settings': settings});
    Settings.post(data);
  };

  $scope.load = function() {
    var params = angular.copy($scope.filters);
    Schedule.get(params, function (data) {
      $scope.schedule_regular = data.schedule_regular;
      $scope.schedule_set = data.schedule_set;
      $scope.teachers = data.teachers;
      $scope.students = data.students;
      $scope.subjects = data.subjects;
      $scope.activateScheduleClasses();
    });
  };

  $scope.activateScheduleClasses = function(){
    function resetScheduleClasses(){
      $('.room-hour').removeClass('schedule-busy');
    }
    resetScheduleClasses();
    var schedule = $scope.getCurrentSchedule();
    $.each(schedule, function(id, value) {
        var name = '#room-hour_' + id;
        $(name).addClass('schedule-busy');
    });
  };

  $scope.enableSetSchedule = function(){
    $scope.schedule_mode = 0;
    $scope.saveModeSettings();
    $scope.activateScheduleClasses();
  };

  $scope.enableRegularSchedule = function(){
    $scope.schedule_mode = 1;
    $scope.saveModeSettings();
    $scope.activateScheduleClasses();
  };

  $scope.getCurrentSchedule = function(){
    if ($scope.schedule_mode === 0) {
      return $scope.schedule_set;
    }
    if ($scope.schedule_mode == 1) {
      return $scope.schedule_regular;
    }
  };

  $scope.openDialog = function(event){
    var schedule = $scope.getCurrentSchedule();
    var room_hour_code = angular.element(event.target).attr('id').replace('room-hour_', '');
    var opts = {
      backdrop: true,
      keyboard: true,
      backdropClick: true,
      resolve: {
        room_hour_schedule: function(){
        return angular.copy(schedule[room_hour_code]);
      },
        room_hour_code: function(){
        return angular.copy(room_hour_code);
      }},
    };
    $dialog.dialog(opts).open('/schedule_modal', 'DialogController');
  };

  $scope.reset_filter = function(filter) {
    if (filter == 'all')
      $scope.filters = {};
    else
      delete $scope.filters[filter];
    $scope.update_location();
  };

  $scope.is_filtered = function() {
    var result = false;
    for (filter in $scope.filters)
      if ($scope.filters[filter])
        result = true;
    return result;
  };

  $scope.update_location = function() {
    if (!$scope.is_filtered()) {
      $location.path("/");
      return;
    }

    var url = "";
    angular.forEach(filter_names, function(val, key) {
      url += val + "-" + ($scope.filters[val] || "all") + "/";
    });

    $location.path(url);
  };

  $scope.$on(
    "$routeChangeSuccess",
    function($currentRoute, $previousRoute) {
      if ($route.current.action == 'home') {
        $scope.filters = {};
        $scope.load();
      } else if ($route.current.action == 'filter') {
        angular.forEach(filter_names, function(key, value) {
          if ($route.current.params[key] !== 'all')
            $scope.filters[key] = $route.current.params[key];
          else
            delete $scope.filters[key];
        });
        $scope.load();
      }
    }
  );
}

function DialogController($scope, dialog, room_hour_schedule, room_hour_code){
  function get_date_room(code, request){
    var pattern = /(\d+)_(\d{2})(\d{2})(\d{4})_(\d+)/g;
    var match = pattern.exec(code);
    var room = rooms[match[1]];
    var date = match[2] + '.' + match[3] + '.' + match[4] + ' ' + match[5] + ':00';
    return [date, room];
  }

  $scope.free = typeof room_hour_schedule === 'undefined';
  if (!$scope.free){
    $scope.teacher = room_hour_schedule['teacher'];
    $scope.room = room_hour_schedule['room'];
    $scope.subject = room_hour_schedule['subject'];
    $scope.lesson_type = room_hour_schedule['lesson_type'];
    $scope.students = room_hour_schedule['students'];
  }
  var room_date = get_date_room(room_hour_code);
  $scope.date = room_date[0];
  $scope.room = room_date[1];
  $scope.close = function(result){
    dialog.close(result);
  };
}
