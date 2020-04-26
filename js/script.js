$(function () {
  var inputs = $("form#userForm input, form#userForm textarea");

  var validateInputs = function validateInputs(inputs) {
    var validForm = true;
    inputs.each(function (index) {
      var input = $(this);
      if (!input.val() || (input.type === "radio" && !input.is(":checked"))) {
        $("#subuser").attr("disabled", "disabled");
        validForm = false;
      }
    });
    return validForm;
  };

  inputs.change(function () {
    if (validateInputs(inputs)) {
      $("#subuser").removeAttr("disabled");
    }
  });
});
