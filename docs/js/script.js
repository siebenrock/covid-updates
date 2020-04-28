// Validate form inputs
// $(function() {
//   var inputs = $("form#userForm input, form#userForm textarea");
//
//   var validateInputs = function validateInputs(inputs) {
//
//     var validForm = true;
//     inputs.each(function(index) {
//       var input = $(this);
//       if (!input.val() || (input.type === "radio" && !input.is(":checked"))) {
//         $("#subuser").attr("disabled", "disabled");
//         validForm = false;
//       }
//     });
//
//     return validForm;
//   };
//
//   inputs.change(function() {
//     if (validateInputs(inputs)) {
//       $("#subuser").removeAttr("disabled");
//     }
//   });
// });


// $('#form-signup').submit(function(e) {
//   console.log("click 1")
//   e.preventDefault();
//   console.log("click 2")
//   $.ajax({
//     url: "http://3.12.83.161:5000/register",
//     data: $(this).serialize(),
//     type: "POST",
//     success: function(data) {
//       console.log("success")
//       alert(data);
//     }
//   });
// });

// Submit form
// $('#form-submit').on('submit', (e) => {
//
//   e.preventDefault();
//   console.log("click 1")
//
//   data = {};
//   $("#form-submit > input").each(function(elem) {
//     data[elem.name] = elem.value;
//   });
//
//   console.log("click 2")
//   $.ajax({
//     type: "POST",
//     url: "http://3.12.83.161:5000/register",
//     data: data,
//     dataType: "json",
//     success: function(response) {
//       alert("The server says: " + response);
//     }
//   });
//
// })




// Show and hide forms for signup, update, unsubscribe
const options = ["signup", "update", "unsubscribe"]
$(document).on('click', 'button[id^="btn-"]', function(e) {

  options.forEach((option) => {
    $("#form-" + option).hide();
    $("#btn-" + option).parent().show();
  });

  $("#form-" + this.id.slice(4)).show();
  $("#" + this.id).parent().hide();

})