angular.module('hourDetails', ['ngResource']).
  factory('HourDetails', function($resource) {
    return $resource('/get-hour-details/', {}, {
      get: {method: 'GET'}
    });
  });

angular.module('teachersAndStudents', ['ngResource']).
  factory('TeachersAndStudents', function($resource) {
    return $resource('/teachers-and-students/', {}, {
      get: {method: 'GET'}
    });
  });

angular.module('scheduleDelete', ['ngResource']).
  factory('ScheduleDelete', function($resource) {
    return $resource('/delete-schedule/', {}, {
      post: {method: 'POST', headers: headers}
    });
  });

angular.module('scheduleSave', ['ngResource']).
  factory('ScheduleSave', function($resource) {
    return $resource('/save-schedule/', {}, {
      post: {method: 'POST', headers: headers}
    });
  });

angular.module('saveSettings', ['ngResource']).
factory('Settings', function($resource) {
  return $resource('/apply-settings/', {}, {
    post: {method: 'POST', headers: headers}
  });
});

angular.module('makeRegular', ['ngResource']).
factory('MakeRegular', function($resource) {
  return $resource('/make-regular/', {}, {
      get: {method: 'GET'}
    });
  });