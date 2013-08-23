angular.module('roomList', ['ngResource']).
  factory('RoomList', function($resource) {
    return $resource('/get-room-list/', {}, {
      get: {method: 'GET', isArray: true}
    });
  });

angular.module('scheduleTeacher', ['ngResource']).
  factory('Schedule', function($resource) {
    return $resource('/load-teacher-schedule/' + start_date_current, {}, {
      get: {method: 'GET'}
    });
  });

var App = angular.module('schedule', ['ui.bootstrap', 'ui.select2',
                                      'scheduleTeacher', 'saveSettings', 'hourDetails',
                                      'teachersAndStudents', 'scheduleSave', 'scheduleDelete',
                                      'roomList']);
App.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

function ScheduleController($scope, $dialog, Schedule, Settings) {
  $scope.schedule_mode = schedule_mode; //enable set schedule by default

  $scope.saveModeSettings = function() {
    settings = JSON.stringify({mode: $scope.schedule_mode});
    data = $.param({settings: settings});
    Settings.post(data, function(){}, function(){
      displayMessage(false, 'Ошибка сохранения режима');
    });
  };

  $scope.load = function() {
    var params = angular.copy($scope.filters);
    Schedule.get(params, function (data) {
      $scope.schedule_set = data.schedule_set;
      $scope.schedule_regular = data.schedule_regular;
      $scope.activateScheduleClasses();
    });
  };

  $scope.activateScheduleClasses = function(){
    function resetScheduleClasses(){
      $('.hour').html('');
    }
    resetScheduleClasses();
    var schedule = $scope.getCurrentSchedule();
    $.each(schedule, function(id, value) {
      var name = '#hour_' + id;
      $(name).html(value['room']);
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
    var hour_code = angular.element(event.target).attr('id').replace('hour_', '');
    var opts = {
      backdrop: true,
      keyboard: true,
      backdropClick: true,
      templateUrl:  '/teacher-schedule-modal',
      controller: 'DialogController',
      resolve: {
        free: function(){
          return !(hour_code in schedule);
        },
        schedule_id: function(){
          if (hour_code in schedule) {
            return schedule[hour_code]['id'];
          }
        },
        schedule_mode: function(){
          return angular.copy($scope.schedule_mode);
        },
        hour_code: function(){
          return angular.copy(hour_code);
        }
      },
    };
    $dialog.dialog(opts).open().then(function(reload){
      if (reload === true) {
        $scope.load();
      }
    });
  };

  $scope.load();

}

function DialogController($scope, dialog, free, hour_code, schedule_id, schedule_mode, HourDetails, TeachersAndStudents, RoomList, ScheduleSave, ScheduleDelete){
  function get_date(code){
    var pattern = /(\d{2})(\d{2})(\d{4})_(\d+)/g;
    var match = pattern.exec(code);
    return match[1] + '.' + match[2] + '.' + match[3] + ' ' + match[4] + ':00';
  }

  $scope.close = function(){
    dialog.close($scope.reload);
  };

  $scope.edit = function(){
    $scope.mode = 'edit';
  };

  $scope.load_teachers_and_students = function() {
    var params = {
      subject_id: $scope.fields.subject,
    };

    TeachersAndStudents.get(params, function (data) {
      $scope.teachers = data.teachers;
      $scope.schedule_students = data.students;
      if (typeof $scope.teacher !== 'undefined') {
        $scope.fields.teacher = $scope.teacher.id;
      }
      if (typeof $scope.students !== 'undefined') {
        $scope.fields.students = $.map($scope.students, function(element) { return element.id; });
      }
    });
  };

  $scope.load = function() {
    var params = {
      schedule_mode: schedule_mode,
      schedule_id: schedule_id,
    };

    HourDetails.get(params, function (data) {
      $scope.teacher = data.teacher;
      $scope.subject = data.subject;
      $scope.room = data.room;
      $scope.lesson_type = data.lesson_type;
      $scope.students = data.students;
      $scope.room_list = data.room_list;
      $scope.fields.subject = $scope.subject.id;
      $scope.fields.lesson_type = $scope.lesson_type.id;
      $scope.fields.room = $scope.room.id;
    });
  };

  $scope.load_room_list = function() {
    var params = {
      schedule_mode: schedule_mode,
      hour_code: hour_code,
    };

    RoomList.get(params, function (data) {
      $scope.room_list = data;
    });
  };

  $scope.save = function() {
    params = {
      students: JSON.stringify($scope.fields.students),
      subject: $scope.fields.subject,
      lesson_type: $scope.fields.lesson_type,
      teacher: $scope.fields.teacher,
      room: $scope.fields.room,
      schedule_mode: schedule_mode,
    };
    if (typeof schedule_id !== 'undefined') {
      params['schedule_id'] = schedule_id;
    } else {
      params['hour_code'] = hour_code;
    }
    ScheduleSave.post($.param(params), function (data) {
      if (data.success) {
        $scope.mode = 'view';
        $scope.free = false;
        $scope.reload = true;
        schedule_id = data.id;
        $scope.load();
      } else {
        displayMessage(false, data.error);
      }
    }, function () {
      displayMessage(false, 'Неизвестная ошибка сохранения');
    }
    );
  };

  $scope.delete = function() {
    params = {
      schedule_id: schedule_id,
      schedule_mode: schedule_mode,
    };
    ScheduleDelete.post($.param(params), function (data) {
      $scope.mode = 'view';
      $scope.free = true;
      $scope.reload = true;
    }, function () {
      displayMessage(false, 'Ошибка удаления');
    }
    );
  };

  $scope.fields = {};
  $scope.reload = false;
  $scope.free = free;
  $scope.mode = 'view';
  if ($scope.free){
    $scope.load_room_list();
  } else {
    $scope.load();
  }
  $scope.date = get_date(hour_code);
  $scope.subjects = subjects;
  $scope.lesson_types = lesson_types;
}
