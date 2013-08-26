$(function(){
  $('#id_subjects').select2();
  $('#id_time_preference').after($('table'));
  $('#id_time_preference').hide();
  $('#id_birthday, #id_passport_issued_date').datepicker();
  if (message) {
    displayMessage(true, message);
  }

});
