angular.module('teachers', ['ngResource']).
  factory('Teachers', function($resource) {
    return $resource('/load-teachers/', {}, {
      get: {method: 'GET'}
    });
  });

angular.module('scheduleAdmin', ['ngResource']).
  factory('Schedule', function($resource) {
    return $resource('/load-admin-schedule/' + start_date_current, {}, {
      get: {method: 'GET'}
    });
  });

var App = angular.module('schedule', ['loadingIndicator', 'ngRoute', 'ui.bootstrap', 'ui.select2',
                                      'scheduleAdmin', 'saveSettings',
                                      'hourDetails', 'teachers', 'students',
                                      'scheduleSave', 'scheduleDelete', 'makeRegular',
                                      ]);
App.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
}).config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/', {action: 'home'}).
    when('/teacher-:teacher/student-:student/subject-:subject/lesson_type-:lesson_type/', {action: 'filter'}).
    otherwise({redirectTo: '/'});
}]);


function ScheduleController($scope, $route, $routeParams, $location, $dialog, Schedule, Settings) {

  var filter_names = ['teacher', 'student', 'subject', 'lesson_type'];
  $scope.filters = filters;
  $scope.schedule_mode = schedule_mode; //enable set schedule by default

  $scope.saveModeSettings = function() {
    settings = JSON.stringify({mode: $scope.schedule_mode});
    data = $.param({settings: settings});
    Settings.post(data, function(){}, function(){
      displayMessage(false, 'Ошибка сохранения режима');
    });
  };

  function resetClasses(class_name) {
    $('.room-hour').removeClass(class_name);
  }

  $scope.load = function() {
    function activateTimeClasses(time, class_name){
      resetClasses(class_name);
      $.each(time, function(key, value){
        var element = $('#room-hour_' + value);
        if (!element.hasClass('schedule-busy')) {
          element.addClass(class_name);
        }
      });
    }

    var params = angular.copy($scope.filters);
    Schedule.get(params, function (data) {

      function process_teacher_time(){
        if (teacher_time) {
          activateTimeClasses(teacher_time, 'teacher-hour');
        } else {
          resetClasses('teacher-hour');
          resetClasses('teacher-student-hour');
        }
      }

      function process_student_time(){
        if (student_time) {
          activateTimeClasses(student_time, 'student-hour');
        } else {
          resetClasses('student-hour');
          resetClasses('teacher-student-hour');
        }
      }

      function process_teacher_student_overlaps(){
        $.each($('.teacher-hour'), function(key, element){
          if ($(element).hasClass('student-hour')) {
            $(element).removeClass('student-hour');
            $(element).removeClass('teacher-hour');
            $(element).addClass('teacher-student-hour');
          }
        });
      }

      $scope.schedule_regular = data.schedule_regular;
      $scope.schedule_set = data.schedule_set;
      $scope.schedule_replacements = data.schedule_replacements;
      $scope.teachers = data.teachers;
      $scope.students = data.students;
      $scope.subjects = data.subjects;
      $scope.lesson_types = data.lesson_types;
      $scope.activateScheduleClasses();
      var teacher_time = data.teacher_time;
      var student_time = data.student_time;

      process_teacher_time();
      process_student_time();
      process_teacher_student_overlaps();

    });
  };

  $scope.activateScheduleClasses = function(){
    function resetScheduleClasses(){
      resetClasses('schedule-busy');
      resetClasses('schedule-replacement');
    }
    function applyBusyClasses(){
      var schedule = $scope.getCurrentSchedule();
      $.each(schedule, function(id, value) {
          var name = '#room-hour_' + id;
          $(name).addClass('schedule-busy');
      });
    }
    function applyReplacementClasses(){
      $.each($scope.schedule_replacements, function(id, value) {
          var name = '#room-hour_' + id;
          $(name).addClass('schedule-replacement');
      });
    }
    resetScheduleClasses();
    applyBusyClasses();
    applyReplacementClasses();
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
      templateUrl:  '/admin-schedule-modal',
      controller: 'DialogController',
      resolve: {
        free: function(){
          return !(room_hour_code in schedule);
        },
        schedule_id: function(){
          return schedule[room_hour_code];
        },
        schedule_mode: function(){
          return angular.copy($scope.schedule_mode);
        },
        room_hour_code: function(){
          return angular.copy(room_hour_code);
        }
      },
    };
    $dialog.dialog(opts).open().then(function(reload){
      if (reload === true) {
        $scope.load();
      }
    });
  };

  $scope.reset_filter = function(filter) {
    if (filter == 'all')
      $scope.filters = {};
    else
      delete $scope.filters[filter];
    $scope.update_filters();
  };

  $scope.update_filters = function() {
    settings = JSON.stringify({filters: $scope.filters});
    data = $.param({settings: settings});
    Settings.post(data, function(){}, function(){
      displayMessage(false, 'Ошибка сохранения фильтров');
    });
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

  $scope.update_location();
}

function DialogController($scope, dialog, free, schedule_id, room_hour_code, schedule_mode, HourDetails, Teachers, Students, ScheduleSave, ScheduleDelete, MakeRegular){
  function get_date_room(code){
    var pattern = /(\d+)_(\d{2})(\d{2})(\d{4})_(\d+)/g;
    var match = pattern.exec(code);
    var room_id = match[1];
    var date = match[2] + '.' + match[3] + '.' + match[4] + ' ' + match[5] + ':00';
    return [date, room_id];
  }

  $scope.close = function(){
    dialog.close($scope.reload);
  };

  $scope.edit = function(){
    $scope.mode = 'edit';
  };

  $scope.load_teachers = function() {
    var params = {
      subject_id: $scope.fields.subject,
      schedule_mode: schedule_mode,
      room_hour_code: room_hour_code,
    };
    if (typeof schedule_id !== 'undefined') {
      params['schedule_id'] = schedule_id;
    }
    Teachers.get(params, function (data) {
      $scope.teachers = data.teachers;
      if (typeof $scope.teacher !== 'undefined') {
        $scope.fields.teacher = $scope.teacher.id;
      }
    });
  };

  $scope.load_students = function() {
    var params = {
      subject_id: $scope.fields.subject,
      room_hour_code: room_hour_code,
    };

    Students.get(params, function (data) {
      $scope.schedule_students = data.students;
      if (typeof $scope.students !== 'undefined') {
        $scope.fields.students = $.map($scope.students, function(element) { return element.id; });
      }
    });
  };

  $scope.load_teachers_and_students = function() {
    $scope.load_teachers();
    $scope.load_students();
  };

  $scope.makeRegular = function() {
    var params = {
      schedule_id: schedule_id,
    };

    MakeRegular.get(params, function (data) {
      if (data.success) {
        $scope.reload = true;
      } else {
        displayMessage(false, data.error);
      }
    }, function () {
      displayMessage(false, 'Ошибка назначения расписания в качестве постоянного');
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
      $scope.lesson_type = data.lesson_type;
      $scope.students = data.students;
      $scope.fields.subject = $scope.subject.id;
      $scope.fields.lesson_type = $scope.lesson_type.id;
    });
  };
  $scope.is_set_schedule_mode_and_not_empty = function() {
    return schedule_mode == 0 && !$scope.free;
  };

  $scope.save = function() {
    params = {
      students: JSON.stringify($scope.fields.students),
      subject: $scope.fields.subject,
      lesson_type: $scope.fields.lesson_type,
      teacher: $scope.fields.teacher,
      schedule_mode: schedule_mode,
    };
    if (typeof schedule_id !== 'undefined') {
      params['schedule_id'] = schedule_id;
    } else {
      params['room_hour_code'] = room_hour_code;
    }
    ScheduleSave.post($.param(params), function (data) {
      if (data.success) {
        $scope.mode = 'view';
        $scope.free = false;
        $scope.reload = true;
        schedule_id = data.schedule_id;
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
      if (data.success) {
        $scope.mode = 'view';
        $scope.free = true;
        $scope.reload = true;
      } else {
        displayMessage(false, data.error);
      }
    }, function () {
      displayMessage(false, 'Ошибка удаления');
    }
    );
  };

  $scope.fields = {};
  $scope.reload = false;
  $scope.free = free;
  $scope.mode = 'view';
  if (!$scope.free){
    $scope.load();
  }
  var date_room = get_date_room(room_hour_code);
  $scope.date = date_room[0];
  $scope.room_id = date_room[1];
  $scope.room_name = rooms[$scope.room_id];
  $scope.subjects = subjects;
  $scope.lesson_types = lesson_types;
}
