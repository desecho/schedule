$(function(){
    $.each(schedules, function(index, value) {
        var name = '#room-hour_' + value;
        $(name).addClass('busy');
    });
});


var App = angular.module('schedule', ['ui.bootstrap']);
App.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});


function Schedule($scope, $dialog) {
  $scope.openDialog = function(){
    var opts = {
      backdrop: true,
      keyboard: true,
      backdropClick: true,
    };
    $dialog.dialog($scope.opts).open('schedule_modal', 'DialogController');
  };

}

function DialogController($scope, dialog){
  $scope.close = function(result){
    dialog.close(result);
  };
}
