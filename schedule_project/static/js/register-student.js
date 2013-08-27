$(function(){
  $('#id_subjects').select2();
  $('#id_offices').select2();
  $('#id_free_time').after($('table'));
  $('#id_free_time').hide();
  $('#id_birthday, #id_passport_issued_date').datepicker();
  if (message) {
    displayMessage(true, message);
  }
});