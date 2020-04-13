$(function () {
  $("#myForm").submit(function () {
    // get all the inputs into an array.
    var $inputs = $("#myForm :input");

    // not sure if you wanted this, but I thought I'd add it.
    // get an associative array of just the values.
    var values = {};
    $inputs.each(function () {
      values[this.name] = $(this).val();
    });

    console.log(values);
  });

  $("#add-button").click(function () {
    let num1 = $("#add-num1").val();
    let num2 = $("#add-num2").val();

    $.ajax({
      url: "http://192.168.99.100:5001/add",
      type: "GET",
      data: { num1: num1, num2: num2 },
      dataType: "json",
    }).done(function (data) {
      console.log(data.answer);
      $("#add-answer").val(data.answer);
    });
  });
});
