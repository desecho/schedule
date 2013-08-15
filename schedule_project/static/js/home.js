var App = angular.module('schedule', ['ui.bootstrap']);
App.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});


function Schedule($scope, $dialog) {
  $scope.resetSchedule = function(){
    $('.room-hour').removeClass('schedule-set');
    $('.room-hour').removeClass('schedule-regular');
  };

  $scope.enableSetSchedule = function(){
    $scope.schedule_mode = 0;
    $scope.resetSchedule();
    $.each(schedule_set, function(id, value) {
        var name = '#room-hour_' + id;
        $(name).addClass('schedule-set');
    });
  };

  $scope.enableRegularSchedule = function(){
    $scope.schedule_mode = 1;
    $scope.resetSchedule();
    $.each(schedule_regular, function(id, value) {
        var name = '#room-hour_' + id;
        $(name).addClass('schedule-regular');
    });
  };
  //$scope.schedule_mode = 0;
  $scope.enableSetSchedule();
  $scope.openDialog = function(event){
    var schedule;
    if ($scope.schedule_mode === 0) {
      schedule = schedule_set;
    }
    if ($scope.schedule_mode == 1) {
      schedule = schedule_regular;
    }
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
    $dialog.dialog(opts).open('schedule_modal', 'DialogController');
  };

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
    $scope.group_type = room_hour_schedule['group_type'];
    $scope.students = room_hour_schedule['students'];
  }
  var room_date = get_date_room(room_hour_code);
  $scope.date = room_date[0];
  $scope.room = room_date[1];
  $scope.close = function(result){
    dialog.close(result);
  };
}
